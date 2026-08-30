"""Receipt export service.

Builds a per-handoff JSON receipt containing the operator email, timestamps,
verification items, approval state, content hash, and share URL. The shape
matches `docs/receipts.schema.json` and is validated in tests.
"""
from __future__ import annotations

from typing import Iterable

from ..models import Handoff, Operator, VerificationItem, Workspace


def build_receipt(
    handoff: Handoff,
    *,
    workspace: Workspace,
    operator: Operator,
    reviewer_emails_by_id: dict,
    base_url: str,
) -> dict:
    items: Iterable[VerificationItem] = handoff.verification_items
    verification_items = [
        {
            "category": (vi.category.value if hasattr(vi.category, "value") else str(vi.category)),
            "passed": bool(vi.passed),
            "notes": vi.notes or "",
            "reviewer_email": reviewer_emails_by_id.get(vi.reviewer_id),
        }
        for vi in items
    ]
    return {
        "handoff_id": str(handoff.id),
        "created_at": handoff.created_at.isoformat() if handoff.created_at else None,
        "approved_at": handoff.approved_at.isoformat() if handoff.approved_at else None,
        "operator_email": operator.email,
        "workspace_name": workspace.name,
        "client_name": handoff.client_name,
        "project_name": handoff.project_name,
        "source_ai_tool": handoff.source_ai_tool,
        "verification_items": verification_items,
        "approval_state": (handoff.status.value if hasattr(handoff.status, "value") else str(handoff.status)),
        "content_sha256": handoff.content_sha256,
        "share_url": f"{base_url.rstrip('/')}/share/{handoff.share_token}",
        "verification_source": (handoff.verification_source.value if hasattr(handoff.verification_source, "value") else str(handoff.verification_source)),
    }
