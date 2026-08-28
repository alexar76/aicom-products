"""Receipt Pydantic schema (matches docs/receipts.schema.json)."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ReceiptVerificationItem(BaseModel):
    category: str
    passed: bool
    notes: str
    reviewer_email: Optional[str] = None


class ReceiptOut(BaseModel):
    handoff_id: str
    created_at: datetime
    approved_at: Optional[datetime] = None
    operator_email: str
    workspace_name: str
    verification_items: List[ReceiptVerificationItem]
    approval_state: str
    content_sha256: str
    share_url: str
    client_name: str
    project_name: str
    source_ai_tool: str
    verification_source: str = Field(default="local")
