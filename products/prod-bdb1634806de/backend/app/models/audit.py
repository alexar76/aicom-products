from sqlalchemy import Column, String, Text, DateTime, Enum, Float, Integer, ForeignKey
from datetime import datetime, timezone
from ..db import Base
from .user import gen_uuid

class InvokeAuditLog(Base):
    __tablename__ = "invoke_audit_log"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    advisory_id = Column(String(36), ForeignKey("advisories.id"), nullable=True)
    capability_name = Column(String(255), nullable=False)
    request_payload = Column(Text, nullable=True)
    response_receipt_digest = Column(String(255), nullable=True)
    cost_usd = Column(Float, nullable=False, default=0.0)
    latency_ms = Column(Integer, nullable=True)
    status = Column(Enum("success", "error", "402", "refusal", name="invoke_status"), nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    cost_bucket = Column(String(255), nullable=True)

class HeartbeatLog(Base):
    __tablename__ = "heartbeat_log"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    sent_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    success = Column(Integer, default=0)
    response_code = Column(Integer, nullable=True)
    payload = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
