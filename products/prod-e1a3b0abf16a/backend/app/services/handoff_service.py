"""Handoff service: state machine, persistence, audit, and share tokens."""
from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import (
    AuditAction,
    AuditEntry,
    Handoff,
    HandoffStatus,
    Operator,
    VerificationItem,
    VerificationSource,
    Workspace,
)
from ..security import new_share_token, sha256_text


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_handoff(
    db: Session,
    *,
    workspace: Workspace,
    creator: Operator,
    client_name: str,
    project_name: str,
    source_ai_tool: str,
    draft_text: str,
) -> Handoff:
    """Create a pending handoff and write a 'created' audit row in the same tx."""
    share_token = new_share_token()
    # Tiny collision check: regenerate if extremely unlikely clash.
    while db.query(Handoff).filter(Handoff.share_token == share_token).first() is not None:
        share_token = new_share_token()

    handoff = Handoff(
        workspace_id=workspace.id,
        client_name=client_name,
        project_name=project_name,
        source_ai_tool=source_ai_tool,
        draft_text=draft_text,
        status=HandoffStatus.pending,
        share_token=share_token,
        content_sha256=sha256_text(draft_text),
        verification_source=VerificationSource.local,
        created_by=creator.id,
    )
    db.add(handoff)
    db.flush()  # populate handoff.id

    db.add(
        AuditEntry(
            handoff_id=handoff.id,
            actor_id=creator.id,
            action=AuditAction.created,
            payload_json=json.dumps(
                {
                    "client_name": client_name,
                    "project_name": project_name,
                    "source_ai_tool": source_ai_tool,
                    "draft_length": len(draft_text),
                }
            ),
        )
    )
    db.commit()
    db.refresh(handoff)
    return handoff


def list_handoffs(
    db: Session,
    *,
    workspace: Workspace,
    status: Optional[HandoffStatus] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[List[Handoff], dict]:
    """List handoffs for a workspace with counts per status."""
    base = db.query(Handoff).filter(Handoff.workspace_id == workspace.id)
    counts = {
        "pending": base.filter(Handoff.status == HandoffStatus.pending).count(),
        "approved": base.filter(Handoff.status == HandoffStatus.approved).count(),
        "rejected": base.filter(Handoff.status == HandoffStatus.rejected).count(),
    }
    query = base.order_by(Handoff.created_at.desc())
    if status is not None:
        query = query.filter(Handoff.status == status)
    items = query.limit(max(1, min(limit, 200))).offset(max(0, offset)).all()
    return items, counts


def get_handoff_for_workspace(
    db: Session, *, workspace: Workspace, handoff_id: str
) -> Optional[Handoff]:
    return (
        db.query(Handoff)
        .filter(Handoff.id == __import__("uuid").UUID(str(handoff_id)), Handoff.workspace_id == workspace.id)
        .first()
    )


def get_public_approved_handoff(db: Session, *, share_token: str) -> Optional[Handoff]:
    return (
        db.query(Handoff)
        .filter(
            Handoff.share_token == share_token,
            Handoff.status == HandoffStatus.approved,
        )
        .first()
    )


def save_verification(
    db: Session,
    *,
    handoff: Handoff,
    reviewer: Operator,
    items: List[dict],
    verification_source: VerificationSource,
) -> List[VerificationItem]:
    """Persist verification checklist rows. Replaces any prior items."""
    # Clear prior items to keep the timeline clean.
    for existing in list(handoff.verification_items):
        db.delete(existing)
    db.flush()

    persisted: List[VerificationItem] = []
    for item in items:
        vi = VerificationItem(
            handoff_id=handoff.id,
            category=item["category"],
            passed=bool(item["passed"]),
            notes=item.get("notes", "") or "",
            reviewer_id=reviewer.id,
        )
        db.add(vi)
        persisted.append(vi)
    db.flush()

    handoff.verification_source = verification_source

    db.add(
        AuditEntry(
            handoff_id=handoff.id,
            actor_id=reviewer.id,
            action=AuditAction.verified,
            payload_json=json.dumps(
                {
                    "items": [
                        {"category": (it.category.value if hasattr(it.category, "value") else str(it.category)), "passed": it.passed}
                        for it in persisted
                    ],
                    "source": (verification_source.value if hasattr(verification_source, "value") else str(verification_source)),
                }
            ),
        )
    )
    db.commit()
    for vi in persisted:
        db.refresh(vi)
    return persisted


def approve_handoff(
    db: Session,
    *,
    handoff: Handoff,
    approver: Operator,
    approved_text: Optional[str] = None,
    override_rejection: bool = False,
) -> Handoff:
    """Transition to 'approved'. Requires explicit action — never implicit."""
    text = approved_text or handoff.draft_text
    handoff.approved_text = text
    handoff.status = HandoffStatus.approved
    handoff.approved_by = approver.id
    handoff.approved_at = _now()
    handoff.content_sha256 = sha256_text(text)

    db.add(
        AuditEntry(
            handoff_id=handoff.id,
            actor_id=approver.id,
            action=AuditAction.approved,
            payload_json=json.dumps(
                {
                    "override_rejection": bool(override_rejection),
                    "approved_length": len(text),
                }
            ),
        )
    )
    db.commit()
    db.refresh(handoff)
    return handoff


def reject_handoff(
    db: Session, *, handoff: Handoff, rejecter: Operator, reason: str
) -> Handoff:
    handoff.status = HandoffStatus.rejected
    handoff.rejected_reason = reason
    db.add(
        AuditEntry(
            handoff_id=handoff.id,
            actor_id=rejecter.id,
            action=AuditAction.rejected,
            payload_json=json.dumps({"reason": reason}),
        )
    )
    db.commit()
    db.refresh(handoff)
    return handoff


def record_export(db: Session, *, handoff: Handoff, exporter: Operator) -> None:
    db.add(
        AuditEntry(
            handoff_id=handoff.id,
            actor_id=exporter.id,
            action=AuditAction.exported,
            payload_json=json.dumps({"format": "json-receipt"}),
        )
    )
    db.commit()
