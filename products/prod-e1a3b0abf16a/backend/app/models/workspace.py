import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum as SAEnum
from sqlalchemy import UUID
from sqlalchemy.orm import relationship
from ..db import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    logo_url = Column(String(1024), nullable=True)
    accent_color = Column(String(7), default="#8a1c2b", nullable=False)
    tier = Column(SAEnum("free", "solo", "team", "agency", name="workspace_tier"), default="free", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    operators = relationship("Operator", back_populates="workspace")
    handoffs = relationship("Handoff", back_populates="workspace")
