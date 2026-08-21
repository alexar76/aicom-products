import asyncio
import httpx
from datetime import datetime, timezone, timedelta
from ..config import get_settings
from ..db import SessionLocal
from ..models.audit import InvokeAuditLog, HeartbeatLog
from sqlalchemy import func

settings = get_settings()

async def send_heartbeat():
    db = SessionLocal()
    try:
        invokes_total = db.query(InvokeAuditLog).count()
        invokes_24h = db.query(InvokeAuditLog).filter(
            InvokeAuditLog.created_at >= datetime.now(timezone.utc) - timedelta(days=1)
        ).count()
        spend_total = db.query(InvokeAuditLog).with_entities(func.sum(InvokeAuditLog.cost_usd)).scalar() or 0
        spend_24h = db.query(InvokeAuditLog).filter(
            InvokeAuditLog.created_at >= datetime.now(timezone.utc) - timedelta(days=1)
        ).with_entities(func.sum(InvokeAuditLog.cost_usd)).scalar() or 0
        # simplified stats
        payload = {
            "agent_id": settings.sentinel_agent_id,
            "name": settings.app_name,
            "product_id": settings.sentinel_product_id,
            "sdk": "aimarket-agent",
            "version": settings.sentinel_sdk_version,
            "public_url": settings.sentinel_public_url,
            "capabilities_used": ["atlas.situation.brief@v1", "atlas.fire.weather@v1", "atlas.nearest.read@v1"],
            "stats": {
                "invokes_total": invokes_total,
                "invokes_24h": invokes_24h,
                "spend_usd_total": spend_total,
                "spend_usd_24h": spend_24h,
                "advisories_served": 0,
                "receipts_verified": 0,
                "errors_24h": 0,
                "cache_hit_rate": 0.0
            }
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{settings.aicom_registry_url}/api/agents/heartbeat",
                    json=payload,
                    headers={"X-Agent-Key": settings.sentinel_agent_key},
                    timeout=5.0
                )
                success = resp.status_code == 200
                code = resp.status_code
            except Exception:
                success = False
                code = None
        db.add(HeartbeatLog(sent_at=datetime.now(timezone.utc), success=success, response_code=code, payload=str(payload)))
        db.commit()
    except Exception as e:
        db.rollback()
        # log failure but don't crash
    finally:
        db.close()

async def heartbeat_loop():
    while True:
        await send_heartbeat()
        await asyncio.sleep(60)
