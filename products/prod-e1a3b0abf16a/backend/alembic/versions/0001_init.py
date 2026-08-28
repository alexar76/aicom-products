"""Initial schema for Relay.

Creates workspaces, operators, sessions, handoffs, verification_items, and
audit_entries. This is the single first revision; subsequent schema changes
should add new revision files rather than editing this one.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("accent_color", sa.String(length=7), nullable=False, server_default="#8a1c2b"),
        sa.Column("tier", sa.String(length=16), nullable=False, server_default="free"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "operators",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("workspace_id", sa.String(length=36), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False, server_default="owner"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_operators_email"),
    )
    op.create_index("ix_operators_workspace_id", "operators", ["workspace_id"])

    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("operator_id", sa.String(length=36), sa.ForeignKey("operators.id", ondelete="CASCADE"), nullable=False),
        sa.Column("csrf_token", sa.String(length=120), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sessions_operator_id", "sessions", ["operator_id"])

    op.create_table(
        "handoffs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("workspace_id", sa.String(length=36), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_name", sa.String(length=200), nullable=False),
        sa.Column("project_name", sa.String(length=200), nullable=False),
        sa.Column("source_ai_tool", sa.String(length=80), nullable=False),
        sa.Column("draft_text", sa.Text(), nullable=False),
        sa.Column("approved_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("share_token", sa.String(length=64), nullable=False, unique=True),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("verification_source", sa.String(length=16), nullable=False, server_default="local"),
        sa.Column("created_by", sa.String(length=36), sa.ForeignKey("operators.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_by", sa.String(length=36), sa.ForeignKey("operators.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_handoffs_workspace_id", "handoffs", ["workspace_id"])
    op.create_index("ix_handoffs_status", "handoffs", ["status"])
    op.create_index("ix_handoffs_created_at", "handoffs", ["created_at"])

    op.create_table(
        "verification_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("handoff_id", sa.String(length=36), sa.ForeignKey("handoffs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(length=16), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("reviewer_id", sa.String(length=36), sa.ForeignKey("operators.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_verification_items_handoff_id", "verification_items", ["handoff_id"])

    op.create_table(
        "audit_entries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("handoff_id", sa.String(length=36), sa.ForeignKey("handoffs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.String(length=36), sa.ForeignKey("operators.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_entries_handoff_id", "audit_entries", ["handoff_id"])
    op.create_index("ix_audit_entries_created_at", "audit_entries", ["created_at"])


def downgrade() -> None:
    for table in [
        "audit_entries",
        "verification_items",
        "handoffs",
        "sessions",
        "operators",
        "workspaces",
    ]:
        op.drop_table(table)
