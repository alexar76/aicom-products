"""Audit log helpers."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import AuditAction, AuditEntry, Handoff, Operator


def list_audit(
    db: Session,
    *,
    handoff: Handoff,
    actor: Optional[Operator] = None,
) -> List[AuditEntry]:
    query = (
        db.query(AuditEntry)
        .filter(AuditEntry.handoff_id == handoff.id)
        .order_by(AuditEntry.created_at.desc())
    )
    if actor is not None:
        query = query.filter(AuditEntry.actor_id == actor.id)
    return query.all()


def serialize_audit(entries: List[AuditEntry], email_by_id: dict) -> list[dict]:
    out = []
    for e in entries:
        out.append(
            {
                "id": e.id,
                "action": e.action.value,
                "actor_email": email_by_id.get(e.actor_id),
                "payload_json": e.payload_json,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
        )
    return out
