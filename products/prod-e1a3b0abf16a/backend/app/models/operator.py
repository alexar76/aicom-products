import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy import UUID
from sqlalchemy.orm import relationship
from ..db import Base


class Operator(Base):
    __tablename__ = "operators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    role = Column(SAEnum("owner", "operator", name="operator_role"), default="operator", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="operators")
    created_handoffs = relationship("Handoff", back_populates="creator", foreign_keys="Handoff.created_by")
    approved_handoffs = relationship("Handoff", back_populates="approver", foreign_keys="Handoff.approved_by")
    audit_entries = relationship("AuditEntry", back_populates="actor")
    sessions = relationship("Session", back_populates="operator")
