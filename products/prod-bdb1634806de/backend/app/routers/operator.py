from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from typing import Optional
from ..db import get_db
from ..config import get_settings
from ..deps import get_current_user
from ..models.audit import InvokeAuditLog
from ..models.advisory import Advisory, AllowanceState
from ..schemas.operator import SpendResponse, AllowanceResponse, WalletResponse, AuditResponse, AuditItem

router = APIRouter(prefix="/api/operator", tags=["operator"])
settings = get_settings()

@router.get("/spend", response_model=SpendResponse)
async def get_spend(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    total_spend = db.query(InvokeAuditLog).with_entities(func.sum(InvokeAuditLog.cost_usd)).scalar() or 0
    daily_spend = db.query(InvokeAuditLog).filter(
        InvokeAuditLog.created_at >= datetime.now(timezone.utc) - timedelta(days=1)
    ).with_entities(func.sum(InvokeAuditLog.cost_usd)).scalar() or 0
    invokes_total = db.query(InvokeAuditLog).count()
    invokes_24h = db.query(InvokeAuditLog).filter(
        InvokeAuditLog.created_at >= datetime.now(timezone.utc) - timedelta(days=1)
    ).count()
    advisories_served = db.query(Advisory).count()
    receipts_verified = db.query(InvokeAuditLog).filter(InvokeAuditLog.response_receipt_digest.isnot(None)).count()
    errors_24h = db.query(InvokeAuditLog).filter(
        InvokeAuditLog.status.in_(["error", "refusal"]),
        InvokeAuditLog.created_at >= datetime.now(timezone.utc) - timedelta(days=1)
    ).count()
    cache_hit_rate = 0.0  # simplified
    return SpendResponse(
        total_spend_usd=total_spend,
        daily_spend_usd=daily_spend,
        budget_usd=settings.sentinel_daily_invoke_budget_usd,
        invokes_total=invokes_total,
        invokes_24h=invokes_24h,
        advisories_served=advisories_served,
        receipts_verified=receipts_verified,
        errors_24h=errors_24h,
        cache_hit_rate=cache_hit_rate
    )

@router.get("/allowance", response_model=AllowanceResponse)
async def get_allowance(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    allowance = db.query(AllowanceState).order_by(AllowanceState.updated_at.desc()).first()
    if not allowance:
        return AllowanceResponse(used=0, max=10, window_seconds=3600, renews_at=None)
    return AllowanceResponse(
        used=allowance.used_invocations,
        max=allowance.max_invocations,
        window_seconds=allowance.window_seconds,
        renews_at=allowance.renews_at.isoformat() if allowance.renews_at else None
    )

@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(current_user = Depends(get_current_user)):
    if settings.wallet_enabled:
        return WalletResponse(
            wallet_enabled=True,
            address_truncated=settings.wallet_address[:6] + "..." + settings.wallet_address[-4:],
            chain=settings.wallet_chain
        )
    return WalletResponse(wallet_enabled=False)

@router.get("/audit", response_model=AuditResponse)
async def get_audit(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    capability: Optional[str] = None,
    status: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(InvokeAuditLog)
    if date_from:
        query = query.filter(InvokeAuditLog.created_at >= date_from)
    if date_to:
        query = query.filter(InvokeAuditLog.created_at <= date_to)
    if capability:
        query = query.filter(InvokeAuditLog.capability_name == capability)
    if status:
        query = query.filter(InvokeAuditLog.status == status)
    total = query.count()
    items = query.order_by(InvokeAuditLog.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
    audit_items = [
        AuditItem(
            id=item.id,
            capability=item.capability_name,
            cost_usd=item.cost_usd,
            receipt=item.response_receipt_digest,
            latency_ms=item.latency_ms,
            status=item.status,
            created_at=item.created_at.isoformat()
        ) for item in items
    ]
    return AuditResponse(items=audit_items, total=total, page=page, per_page=per_page)
