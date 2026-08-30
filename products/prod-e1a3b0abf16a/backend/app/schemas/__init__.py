"""Pydantic schemas for Relay API – all models defined inline to avoid missing-module imports."""

import sys
from pathlib import Path

# Ensure the project root is on sys.path so that `backend` is importable.
# This repairs ModuleNotFoundError: No module named 'backend' when the
# app is started with `uvicorn backend.app.main:app` from a directory
# that is not the project root.
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from datetime import datetime
from typing import List, Optional

from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel, Field, field_validator


class BaseModel(PydanticBaseModel):
    model_config = {"from_attributes": True}

    @field_validator("*", mode="before")
    @classmethod
    def stringify_uuid(cls, value):
        return str(value) if isinstance(value, UUID) else value


# ---------------------------------------------------------------------------
# Operator schemas
# ---------------------------------------------------------------------------

class OperatorCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=10)
    workspace_name: str


class OperatorOut(BaseModel):
    id: str
    email: str
    role: str
    workspace_id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Workspace schemas
# ---------------------------------------------------------------------------

class WorkspaceOut(BaseModel):
    id: str
    name: str
    logo_url: Optional[str] = None
    accent_color: str
    tier: str
    created_at: datetime


class BrandingUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    accent_color: Optional[str] = None


# ---------------------------------------------------------------------------
# Handoff schemas
# ---------------------------------------------------------------------------

class HandoffCreate(BaseModel):
    draft_text: str = Field(..., min_length=20, max_length=50000)
    client_name: str
    project_name: str
    source_ai_tool: str


class HandoffOut(BaseModel):
    id: str
    workspace_id: str
    client_name: str
    project_name: str
    source_ai_tool: str
    draft_text: str
    approved_text: Optional[str] = None
    status: str
    share_token: str
    content_sha256: str
    verification_source: str
    created_by: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None
    created_at: datetime


class PublicHandoffOut(BaseModel):
    id: str
    client_name: str
    project_name: str
    approved_text: str
    verification_source: str
    workspace: WorkspaceOut
    created_at: datetime


class ApproveRequest(BaseModel):
    approved_text: Optional[str] = None
    override_rejection: bool = False


# ---------------------------------------------------------------------------
# Verification schemas
# ---------------------------------------------------------------------------

class VerificationItemOut(BaseModel):
    id: str
    handoff_id: str
    category: str
    passed: bool
    notes: str
    reviewer_id: str
    created_at: datetime


class VerifyIn(BaseModel):
    items: List[dict]  # list of {category, passed, notes}
    use_metis: bool = False


class VerifyOut(BaseModel):
    verification_items: List[VerificationItemOut]
    verification_source: str


# ---------------------------------------------------------------------------
# Audit schemas
# ---------------------------------------------------------------------------

class AuditEntryOut(BaseModel):
    id: str
    handoff_id: str
    actor_id: str
    action: str
    payload_json: Optional[str] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class LoginIn(BaseModel):
    email: str
    password: str


class MeOut(BaseModel):
    operator: OperatorOut
    workspace: WorkspaceOut


class SignupIn(BaseModel):
    email: str
    password: str = Field(..., min_length=10)
    workspace_name: str


# ---------------------------------------------------------------------------
# Aliases for callers that use different names
# ---------------------------------------------------------------------------

BrandingIn = BrandingUpdate
BrandingOut = BrandingUpdate


class PublicHandoffShareOut(BaseModel):
    """Approved handoff slice for the public share page."""
    id: str
    client_name: str
    project_name: str
    source_ai_tool: str
    approved_text: str
    approved_at: Optional[datetime] = None
    content_sha256: str


class PublicReadOut(BaseModel):
    handoff: PublicHandoffShareOut
    workspace: WorkspaceOut
    verification_source: str  # aicom-factory-relay-public-export

PublicWorkspaceOut = WorkspaceOut
ApproveIn = ApproveRequest


# ---------------------------------------------------------------------------
# Additional schemas required by routers
# ---------------------------------------------------------------------------

class EmbedSnippetOut(BaseModel):
    script: str
    iframe: str


class HandoffCounts(BaseModel):
    pending: int
    approved: int
    rejected: int


class HandoffListOut(BaseModel):
    items: List[HandoffOut]
    counts: HandoffCounts


class RejectIn(BaseModel):
    reason: str


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "OperatorCreate", "OperatorOut",
    "WorkspaceOut", "BrandingUpdate",
    "HandoffCreate", "HandoffOut", "PublicHandoffOut", "ApproveRequest",
    "VerificationItemOut",
    "AuditEntryOut",
    "VerifyIn", "VerifyOut",
    "LoginIn", "MeOut", "SignupIn",
    "BrandingIn", "BrandingOut", "PublicReadOut", "PublicWorkspaceOut",
    "ApproveIn", "EmbedSnippetOut", "HandoffCounts", "HandoffListOut", "RejectIn",
]
