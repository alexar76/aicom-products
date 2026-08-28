"""Unit tests for the receipt builder."""
from __future__ import annotations

import json
import re

from backend.app.db import init_db, session_scope
from backend.app.models import (
    Operator,
    OperatorRole,
    VerificationSource,
    Workspace,
    WorkspaceTier,
)
from backend.app.security import hash_password, new_share_token, sha256_text
from backend.app.services import handoff_service
from backend.app.services.receipt import build_receipt


def _setup():
    init_db()
    with session_scope() as db:
        ws = Workspace(name="R WS", tier=WorkspaceTier.solo)
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


def test_receipt_contains_required_fields_and_valid_hash():
    ws_id, op_id = _setup()
    with session_scope() as db:
        ws = db.get(Workspace, ws_id)
        op_ = db.get(Operator, op_id)
        h = handoff_service.create_handoff(
            db, workspace=ws, creator=op_, client_name="C", project_name="P",
            source_ai_tool="ChatGPT",
            draft_text="A draft body that is at least twenty characters long.",
        )
        handoff_service.approve_handoff(db, handoff=h, approver=op_)
        receipt = build_receipt(
            h, workspace=ws, operator=op_, reviewer_emails_by_id={op_.id: op_.email},
            base_url="https://relay.example",
        )
    for key in [
        "handoff_id", "created_at", "approved_at", "operator_email", "workspace_name",
        "verification_items", "approval_state", "content_sha256", "share_url",
    ]:
        assert key in receipt
    assert re.fullmatch(r"[0-9a-f]{64}", receipt["content_sha256"])
    assert receipt["share_url"] == f"https://relay.example/share/{h.share_token}"
    assert receipt["approval_state"] == "approved"
    json.dumps(receipt)  # serializable
