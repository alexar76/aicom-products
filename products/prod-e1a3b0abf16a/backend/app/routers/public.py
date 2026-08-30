"""Public router: no-auth read of approved handoffs, rate-limited."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import Handoff
from ..schemas import PublicHandoffShareOut, PublicReadOut, PublicWorkspaceOut  # aicom-factory-relay-public-export
from ..services import handoff_service

router = APIRouter(tags=["public"])

# --- In-process token bucket (Redis-ready; per IP) ---------------------------

_BUCKETS: dict[str, deque[float]] = defaultdict(deque)
_BUCKETS_LOCK = Lock()


def _rate_limit(ip: str, limit: int) -> tuple[bool, int]:
    """Returns (allowed, retry_after_seconds)."""
    now = time.monotonic()
    window = 60.0
    with _BUCKETS_LOCK:
        q = _BUCKETS[ip]
        while q and now - q[0] > window:
            q.popleft()
        if len(q) >= limit:
            retry = int(window - (now - q[0])) + 1
            return False, max(retry, 1)
        q.append(now)
        return True, 0


@router.get("/handoffs/{share_token}", response_model=PublicReadOut)
def read_public(
    share_token: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> PublicReadOut:
    settings = get_settings()
    ip = (request.headers.get("x-forwarded-for", "").split(",")[0].strip()
          or (request.client.host if request.client else "unknown"))
    allowed, retry = _rate_limit(ip, settings.share_rate_limit_per_min)
    if not allowed:
        raise HTTPException(status_code=429, detail="rate limited", headers={"Retry-After": str(retry)})

    h = handoff_service.get_public_approved_handoff(db, share_token=share_token)
    if h is None:
        raise HTTPException(status_code=404, detail="not available")
    workspace = h.workspace
    return PublicReadOut(
        handoff=PublicHandoffShareOut(
            id=str(h.id),  # aicom-factory-relay-public-export
            client_name=h.client_name,
            project_name=h.project_name,
            source_ai_tool=h.source_ai_tool,
            approved_text=h.approved_text or h.draft_text,
            approved_at=h.approved_at,
            content_sha256=h.content_sha256,
        ),
        workspace=PublicWorkspaceOut(
            name=workspace.name,
            logo_url=workspace.logo_url,
            accent_color=workspace.accent_color,
            tier=(workspace.tier.value if hasattr(workspace.tier, 'value') else str(workspace.tier)),  # aicom-factory-relay-public-export
        ),
        verification_source=h.verification_source.value,
    )


@router.get("/health")
def health_public() -> dict:
    return {"ok": True}
