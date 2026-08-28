from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class BrandingUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    logo_url: Optional[HttpUrl] = None
    accent_color: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$")
