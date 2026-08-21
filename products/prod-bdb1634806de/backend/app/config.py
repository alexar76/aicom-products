from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Sentinel Verified Safety Companion"
    secret_key: str = "dev-secret-key-change-me"
    database_url: str = "sqlite:///./sentinel.db"
    atlas_base_url: str = "http://localhost:8001"
    atlas_agent_key: str = "demo-atlas-key"
    aicom_registry_url: str = "http://localhost:8002"
    sentinel_agent_key: str = "demo-sentinel-key"
    sentinel_daily_invoke_budget_usd: float = 2.00
    wallet_enabled: int = 0
    wallet_address: str = ""
    wallet_chain: str = "base"
    # Must match factory live-gate / sandbox demo identity (not a private sentinel-only mailbox).
    sandbox_demo_email: str = "sandbox.demo@magic-ai-factory.com"
    sandbox_demo_password: str = "SentinelDemo123!"
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
