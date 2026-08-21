from pydantic import BaseModel
from typing import Optional, List

class SpendResponse(BaseModel):
    total_spend_usd: float
    daily_spend_usd: float
    budget_usd: float
    invokes_total: int
    invokes_24h: int
    advisories_served: int
    receipts_verified: int
    errors_24h: int
    cache_hit_rate: float

class AllowanceResponse(BaseModel):
    used: int
    max: int
    window_seconds: int
    renews_at: Optional[str] = None

class WalletResponse(BaseModel):
    wallet_enabled: bool
    address_truncated: Optional[str] = None
    chain: Optional[str] = None

class AuditItem(BaseModel):
    id: str
    capability: str
    cost_usd: float
    receipt: Optional[str] = None
    latency_ms: Optional[int] = None
    status: str
    created_at: str

class AuditResponse(BaseModel):
    items: List[AuditItem]
    total: int
    page: int
    per_page: int
