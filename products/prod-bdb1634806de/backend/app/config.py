from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Sentinel Verified Safety Companion"
    secret_key: str = "dev-secret-key-change-me"
    database_url: str = "sqlite:///./sentinel.db"
    atlas_base_url: str = "https://atlas.modelmarket.dev"
    atlas_agent_key: str = "demo-atlas-key"
    aicom_registry_url: str = "https://modelmarket.dev"
    sentinel_agent_key: str = "demo-sentinel-key"
    sentinel_daily_invoke_budget_usd: float = 2.00
    wallet_enabled: int = 0
    wallet_address: str = ""
    wallet_chain: str = "base"
    # Must match factory live-gate / sandbox demo identity (not a private sentinel-only mailbox).
    sandbox_demo_email: str = ""
    sandbox_demo_password: str = ""
    redis_url: str = ""
    sentinel_agent_id: str = "sentinel-local"
    sentinel_sdk_version: str = "0.1.0"
    sentinel_product_id: str = "sentinel-safety"
    sentinel_public_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
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


settings = _AicomSettingsView(get_settings())
