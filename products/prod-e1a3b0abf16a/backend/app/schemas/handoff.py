from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class HandoffCreate(BaseModel):
    draft_text: str = Field(min_length=20, max_length=50_000)
    client_name: str = Field(min_length=1, max_length=255)
    project_name: str = Field(min_length=1, max_length=255)
    source_ai_tool: str = Field(min_length=1, max_length=255)


class VerificationItemIn(BaseModel):
    category: str  # claims, sources, tone, risk
    passed: bool
    notes: Optional[str] = None


class VerificationRequest(BaseModel):
    items: List[VerificationItemIn]
    use_metis: bool = False


class VerificationItemOut(BaseModel):
    id: str
    category: str
    passed: bool
    notes: Optional[str]
    reviewer_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HandoffOut(BaseModel):
    id: str
    workspace_id: str
    client_name: str
    project_name: str
    source_ai_tool: str
    draft_text: str
    approved_text: Optional[str]
    status: str
    share_token: str
    content_sha256: str
    verification_source: str
    created_by: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    rejected_reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class HandoffListResponse(BaseModel):
    items: List[HandoffOut]
    counts: dict  # {"pending": int, "approved": int, "rejected": int}


class HandoffDetailResponse(BaseModel):
    handoff: HandoffOut
    verification_items: List[VerificationItemOut]
    audit: List["AuditEntryOut"]


class AuditEntryOut(BaseModel):
    id: str
    action: str
    actor_email: str
    payload_json: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ApproveRequest(BaseModel):
    approved_text: Optional[str] = None
    override_rejection: bool = False


class RejectRequest(BaseModel):
    reason: str = Field(min_length=1)


class EmbedSnippetResponse(BaseModel):
    script: str
    iframe: str


class ReceiptResponse(BaseModel):
    handoff_id: str
    created_at: datetime
    approved_at: Optional[datetime]
    operator_email: str
    verification_items: List[dict]
    approval_state: str
    content_sha256: str
    share_url: str
