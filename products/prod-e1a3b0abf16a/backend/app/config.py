"""Runtime configuration for Relay.

Settings are read from environment variables with sensible local defaults so
the app boots in a sandbox with no external infrastructure.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Persistence
    relay_db_path: str = Field(default="./.data/relay.db", alias="RELAY_DB_PATH")

    # Security
    session_secret: str = Field(
        default="dev-only-secret-please-change-32+chars",
        alias="SESSION_SECRET",
        min_length=16,
    )
    session_ttl_days: int = Field(default=7, alias="SESSION_TTL_DAYS", ge=1, le=60)
    cors_origin: str = Field(default="http://localhost:5173", alias="CORS_ORIGIN")

    # Verification adapter
    metis_verify_url: Optional[str] = Field(default=None, alias="METIS_VERIFY_URL")

    # Optional Redis for rate-limit + session cache
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")

    # Demo seed (sandbox)
    sandbox_demo_email: str = Field(
        default="[email protected]", alias="SANDBOX_DEMO_EMAIL"
    )
    sandbox_demo_password: str = Field(
        default="RelayDemo!2025", alias="SANDBOX_DEMO_PASSWORD"
    )

    # Rate limiting (per-IP, /share/* and /embed.js)
    share_rate_limit_per_min: int = Field(default=60, alias="SHARE_RATE_LIMIT_PER_MIN", ge=1)

    # Vite mirror (used for documentation; backend itself doesn't read VITE_*)
    vite_demo_email: Optional[str] = Field(default=None, alias="VITE_DEMO_EMAIL")
    vite_demo_password: Optional[str] = Field(default=None, alias="VITE_DEMO_PASSWORD")

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.relay_db_path}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

# aicom-factory-settings-export — vendored only; product tree under data/code is untouched.
# Generated apps often ``from .config import settings`` and read ``settings.SANDBOX_DEMO_EMAIL``
# while config.py only defines ``get_settings()`` + snake_case fields. Without this shim the
# Vercel function dies at import with ImportError / AttributeError (FUNCTION_INVOCATION_FAILED).
class _AicomSettingsView:
    __slots__ = ("_inner",)

    def __init__(self, inner):
        object.__setattr__(self, "_inner", inner)

    def __getattr__(self, name: str):
        inner = object.__getattribute__(self, "_inner")
        if name in ("ALGORITHM", "algorithm"):
            for cand in ("algorithm", "ALGORITHM", "jwt_algorithm"):
                if hasattr(inner, cand):
                    val = getattr(inner, cand)
                    if val:
                        return val
            return "HS256"
        if hasattr(inner, name):
            return getattr(inner, name)
        low = name.lower()
        if low != name and hasattr(inner, low):
            return getattr(inner, low)
        raise AttributeError(name)

    def __call__(self) -> "Settings":
        return object.__getattribute__(self, "_inner")


settings = _AicomSettingsView(get_settings())
get_settings = settings
