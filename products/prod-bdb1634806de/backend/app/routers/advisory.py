# aicom-factory-atlas-escrow-single
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
import json
import asyncio
from ..db import get_db
from ..config import get_settings
from ..services.atlas_client import AtlasClient
from ..services.rule_engine import RuleEngine
from ..services.cache import CacheService
from ..models.advisory import Advisory, CachedMeshReading
from ..models.audit import InvokeAuditLog
from ..schemas.advisory import AdvisoryResponse, HazardResponse, ThresholdInfo, OverallResponse

from collections import defaultdict, deque
import time

_rate_requests = defaultdict(deque)

def _check_rate_limit(ip: str, max_requests: int = 30, window_seconds: int = 60) -> bool:
    now = time.time()
    dq = _rate_requests[ip]
    while dq and now - dq[0] > window_seconds:
        dq.popleft()
    if len(dq) >= max_requests:
        return False
    dq.append(now)
    return True

router = APIRouter(prefix="/api/advisory", tags=["advisory"])
settings = get_settings()
cache = CacheService()

@router.get("", response_model=AdvisoryResponse)
async def get_advisory(
    request: Request,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    visitor_id: str = Query(None),
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # round to 1 decimal
    rounded_lat = round(lat, 1)
    rounded_lon = round(lon, 1)

    # check cache for this rounded location
    cached = cache.get(rounded_lat, rounded_lon)
    if cached:
        # return cached advisory
        return cached

    # check daily budget
    daily_spend = db.query(InvokeAuditLog).filter(
        InvokeAuditLog.created_at >= datetime.now(timezone.utc) - timedelta(days=1)
    ).with_entities(func.sum(InvokeAuditLog.cost_usd)).scalar() or 0
    if daily_spend >= settings.sentinel_daily_invoke_budget_usd:
        # serve last cached or unknown
        last_advisory = db.query(Advisory).order_by(Advisory.created_at.desc()).first()
        if last_advisory:
            # construct simple response from last advisory? For simplicity return UNKNOWN
            return AdvisoryResponse(
                overall=OverallResponse(level="UNKNOWN", reason="Daily budget reached; showing last known or unknown.", receipt=None),
                hazards=[],
                thresholds=[],
                location={"lat": rounded_lat, "lon": rounded_lon, "rounded": True}
            )
        else:
            return AdvisoryResponse(
                overall=OverallResponse(level="UNKNOWN", reason="Daily budget reached; no cached advisory available.", receipt=None),
                hazards=[],
                thresholds=[],
                location={"lat": rounded_lat, "lon": rounded_lon, "rounded": True}
            )

    # Invoke ATLAS capabilities (run in thread to avoid blocking event loop)
    import concurrent.futures
    atlas = AtlasClient()
    loop = asyncio.get_running_loop()
    try:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            situation = await atlas.invoke_situation_brief(rounded_lat, rounded_lon)
        fire_weather = situation
        nearest = situation
    except Exception as e:
        # degrade gracefully: return UNKNOWN with explanation
        return AdvisoryResponse(
            overall=OverallResponse(level="UNKNOWN", reason=f"Mesh unavailable: {str(e)}", receipt=None),
            hazards=[],
            thresholds=[],
            location={"lat": rounded_lat, "lon": rounded_lon, "rounded": True}
        )

    # Apply rule engine
    engine = RuleEngine()
    result = engine.evaluate(situation, fire_weather, nearest)

    # Save advisories to DB
    for hazard in result["hazards"]:
        adv = Advisory(
            rounded_lat=rounded_lat,
            rounded_lon=rounded_lon,
            hazard=hazard["type"],
            level=hazard["level"],
            measurement=hazard.get("measurement"),
            distance_km=hazard.get("distance_km"),
            receipt_digest=hazard.get("receipt"),
            timestamp=datetime.now(timezone.utc),
            is_cached=False,
            sim_flag=hazard.get("sim", False)
        )
        db.add(adv)
    db.commit()

    # Cache the result
    response = AdvisoryResponse(
        overall=OverallResponse(
            level=result["overall"]["level"],
            reason=result["overall"]["reason"],
            receipt=result["overall"].get("receipt")
        ),
        hazards=[HazardResponse(**h) for h in result["hazards"]],
        thresholds=[ThresholdInfo(**t) for t in result["thresholds"]],
        location={"lat": rounded_lat, "lon": rounded_lon, "rounded": True}
    )
    cache.set(rounded_lat, rounded_lon, response)
    return response
