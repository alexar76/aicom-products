from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10)
    workspace_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OperatorOut(BaseModel):
    id: str
    email: str
    role: str
    workspace_id: str

    model_config = {"from_attributes": True}


class WorkspaceOut(BaseModel):
    id: str
    name: str
    logo_url: str | None
    accent_color: str
    tier: str

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    operator: OperatorOut
    workspace: WorkspaceOut


class MeResponse(BaseModel):
    operator: OperatorOut
    workspace: WorkspaceOut


class MessageResponse(BaseModel):
    ok: bool = True
