"""Unit tests for the handoff state machine."""
from __future__ import annotations

from backend.app.db import init_db, session_scope
from backend.app.models import (
    AuditAction,
    Handoff,
    HandoffStatus,
    Operator,
    OperatorRole,
    VerificationSource,
    Workspace,
    WorkspaceTier,
)
from backend.app.security import hash_password
from backend.app.services import handoff_service


def _setup():
    init_db()
    with session_scope() as db:
        ws = Workspace(name="State WS", tier=WorkspaceTier.solo)
        db.add(ws)
        db.flush()
        op_ = Operator(
            email="[email protected]",
            password_hash=hash_password("longenoughpassword"),
            workspace_id=ws.id,
            role=OperatorRole.owner,
        )
        db.add(op_)
        db.flush()
        return ws.id, op_.id


def test_create_writes_audit_and_share_token():
    ws_id, op_id = _setup()
    with session_scope() as db:
        ws = db.get(Workspace, ws_id)
        op_ = db.get(Operator, op_id)
        h = handoff_service.create_handoff(
            db, workspace=ws, creator=op_, client_name="C", project_name="P",
            source_ai_tool="ChatGPT", draft_text="x" * 40,
        )
        assert h.status == HandoffStatus.pending
        assert len(h.share_token) >= 16
        assert h.content_sha256 != ""
        assert any(a.action == AuditAction.created for a in h.audit_entries)


def test_approve_transitions_to_approved():
    ws_id, op_id = _setup()
    with session_scope() as db:
        ws = db.get(Workspace, ws_id)
        op_ = db.get(Operator, op_id)
        h = handoff_service.create_handoff(
            db, workspace=ws, creator=op_, client_name="C", project_name="P",
            source_ai_tool="ChatGPT", draft_text="This is the draft body that is at least twenty chars.",
        )
        handoff_service.approve_handoff(db, handoff=h, approver=op_)
        assert h.status == HandoffStatus.approved
        assert h.approved_by == op_.id
        assert h.approved_at is not None
        actions = [a.action for a in h.audit_entries]
        assert AuditAction.created in actions
        assert AuditAction.approved in actions


def test_reject_records_reason():
    ws_id, op_id = _setup()
    with session_scope() as db:
        ws = db.get(Workspace, ws_id)
        op_ = db.get(Operator, op_id)
        h = handoff_service.create_handoff(
            db, workspace=ws, creator=op_, client_name="C", project_name="P",
            source_ai_tool="ChatGPT", draft_text="This is a draft body, at least twenty chars.",
        )
        handoff_service.reject_handoff(db, handoff=h, rejecter=op_, reason="tone is off")
        assert h.status == HandoffStatus.rejected
        assert h.rejected_reason == "tone is off"


def test_save_verification_replaces_prior_items():
    ws_id, op_id = _setup()
    with session_scope() as db:
        ws = db.get(Workspace, ws_id)
        op_ = db.get(Operator, op_id)
        h = handoff_service.create_handoff(
            db, workspace=ws, creator=op_, client_name="C", project_name="P",
            source_ai_tool="ChatGPT", draft_text="This is a draft body, at least twenty chars.",
        )
        handoff_service.save_verification(
            db, handoff=h, reviewer=op_,
            items=[{"category": "claims", "passed": True, "notes": "ok"}],
            verification_source=VerificationSource.local,
        )
        first_count = len(h.verification_items)
        handoff_service.save_verification(
            db, handoff=h, reviewer=op_,
            items=[
                {"category": "claims", "passed": True, "notes": "ok"},
                {"category": "tone", "passed": False, "notes": "hype"},
            ],
            verification_source=VerificationSource.local,
        )
        assert len(h.verification_items) == 2
        assert first_count == 1
