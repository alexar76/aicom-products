import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Enum as SAEnum
from sqlalchemy import UUID
from sqlalchemy.orm import relationship
from ..db import Base


class VerificationItem(Base):
    __tablename__ = "verification_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    handoff_id = Column(UUID(as_uuid=True), ForeignKey("handoffs.id"), nullable=False)
    category = Column(
        SAEnum("claims", "sources", "tone", "risk", name="verification_category"),
        nullable=False,
    )
    passed = Column(Boolean, nullable=False)
    notes = Column(Text, nullable=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    handoff = relationship("Handoff", back_populates="verification_items")
    reviewer = relationship("Operator")
