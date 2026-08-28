from pydantic import BaseModel
from typing import Optional


class PublicHandoffResponse(BaseModel):
    handoff: dict
    workspace: dict
    verification_source: str
