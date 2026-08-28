"""Idempotent demo seeder for the sandbox environment.

Creates one operator + workspace + three sample handoffs (pending, approved,
rejected) when the database is empty. Safe to run on every boot.
"""
from __future__ import annotations

import logging

from .config import get_settings
from .db import init_db, session_scope
from .models import Handoff, HandoffStatus, Operator, OperatorRole, VerificationSource, Workspace, WorkspaceTier
from .security import hash_password, new_share_token, sha256_text
from .services import handoff_service

log = logging.getLogger("relay.seed")

_DEMO_DRAFT = (
    "Hi {client}, here is the proposed positioning for {project}. "
    "We are recommending a calm, evidence-led voice grounded in three proofs: "
    "a published case study, a third-party benchmark, and an independent review. "
    "Source: relay.example/research/2025. Numbers in this brief are estimates. "
)


def seed_demo() -> None:
    settings = get_settings()
    init_db()
    with session_scope() as db:
        if db.query(Operator).count() > 0:
            return

        workspace = Workspace(
            name="Relay Demo Studio",
            tier=WorkspaceTier.solo,
            accent_color="#8a1c2b",
        )
        db.add(workspace)
        db.flush()

        operator = Operator(
            email=settings.sandbox_demo_email.lower().strip(),
            password_hash=hash_password(settings.sandbox_demo_password),
            workspace_id=workspace.id,
            role=OperatorRole.owner,
        )
        db.add(operator)
        db.flush()

        # 1) pending
        handoff_service.create_handoff(
            db,
            workspace=workspace,
            creator=operator,
            client_name="Atlas Coffee Roasters",
            project_name="Q2 Brand Brief",
            source_ai_tool="ChatGPT",
            draft_text=_DEMO_DRAFT.format(client="Atlas", project="Q2 Brand Brief"),
        )
        # 2) approved
        approved_text = _DEMO_DRAFT.format(client="Northwind", project="Marketplace Launch")
        h2 = handoff_service.create_handoff(
            db,
            workspace=workspace,
            creator=operator,
            client_name="Northwind Goods",
            project_name="Marketplace Launch",
            source_ai_tool="Claude",
            draft_text=approved_text,
        )
        handoff_service.approve_handoff(db, handoff=h2, approver=operator, approved_text=approved_text)
        # 3) rejected
        h3 = handoff_service.create_handoff(
            db,
            workspace=workspace,
            creator=operator,
            client_name="Lumen Studios",
            project_name="Pricing Page Rewrite",
            source_ai_tool="ChatGPT",
            draft_text="Buy now, limited offer, call 555-123-9999 immediately for a free trial!!!",
        )
        handoff_service.reject_handoff(
            db, handoff=h3, rejecter=operator, reason="Hype tone and exposed phone number."
        )

        log.info("seed: created demo workspace + operator + 3 handoffs")

seed = seed_demo


if __name__ == "__main__":  # pragma: no cover - manual script
    logging.basicConfig(level=logging.INFO)
    seed_demo()
