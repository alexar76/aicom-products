import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SAEnum, Boolean
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from ..db import Base


class Handoff(Base):
    __tablename__ = "handoffs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    client_name = Column(String(255), nullable=False)
    project_name = Column(String(255), nullable=False)
    source_ai_tool = Column(String(255), nullable=False)
    draft_text = Column(Text, nullable=False)
    approved_text = Column(Text, nullable=True)
    status = Column(
        SAEnum("pending", "approved", "rejected", name="handoff_status"),
        default="pending",
        nullable=False,
    )
    share_token = Column(String(64), unique=True, index=True, nullable=False)
    content_sha256 = Column(String(64), nullable=False)
    verification_source = Column(
        SAEnum("local", "metis", "unavailable", name="verification_source"),
        default="local",
        nullable=False,
    )
    created_by = Column(UUID(as_uuid=True), ForeignKey("operators.id"), nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("operators.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="handoffs")
    creator = relationship("Operator", back_populates="created_handoffs", foreign_keys=[created_by])
    approver = relationship("Operator", back_populates="approved_handoffs", foreign_keys=[approved_by])
    verification_items = relationship("VerificationItem", back_populates="handoff", cascade="all, delete-orphan")
    audit_entries = relationship("AuditEntry", back_populates="handoff", cascade="all, delete-orphan")
