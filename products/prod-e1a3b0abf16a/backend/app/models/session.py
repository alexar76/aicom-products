import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy import UUID
from sqlalchemy.orm import relationship
from ..db import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(255), primary_key=True)  # signed token string
    operator_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"), nullable=False)
    csrf_token = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    operator = relationship("Operator", back_populates="sessions")
