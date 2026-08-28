import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy import UUID
from sqlalchemy.orm import relationship
from ..db import Base


class AuditEntry(Base):
    __tablename__ = "audit_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    handoff_id = Column(UUID(as_uuid=True), ForeignKey("handoffs.id"), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"), nullable=False)
    action = Column(
        SAEnum(
            "created", "verified", "approved", "rejected", "exported", "branding_updated",
            name="audit_action",
        ),
        nullable=False,
    )
    payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    handoff = relationship("Handoff", back_populates="audit_entries")
    actor = relationship("Operator", back_populates="audit_entries")
