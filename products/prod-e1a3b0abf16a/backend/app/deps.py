"""FastAPI dependencies: current operator, workspace, and CSRF guard."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .models import Operator, Session as SessionModel, Workspace
from .security import (
    is_session_invalidated,
    new_csrf_token,
    unsign_session,
    verify_csrf_token,
)


SESSION_COOKIE_NAME = "relay_session"
CSRF_HEADER_NAME = "x-relay-csrf"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _operator_from_session(db: Session, sid: str) -> Optional[Operator]:
    if not sid or is_session_invalidated(sid):
        return None
    sess: Optional[SessionModel] = db.get(SessionModel, sid)
    if sess is None:
        return None
    expires = sess.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires <= _now():
        return None
    return db.get(Operator, sess.operator_id)


def get_current_operator(
    request: Request,
    db: Session = Depends(get_db),
) -> Operator:
    """Resolve the current operator from Bearer session id or signed cookie."""
    auth_header = request.headers.get("Authorization") or ""
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        operator = _operator_from_session(db, token)
        if operator is not None:
            return operator

    raw = request.cookies.get(SESSION_COOKIE_NAME)
    if raw:
        sid = unsign_session(raw)
        operator = _operator_from_session(db, sid or "")
        if operator is not None:
            return operator

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")


def get_current_workspace(
    operator: Operator = Depends(get_current_operator),
    db: Session = Depends(get_db),
) -> Workspace:
    try:
        ws = db.get(Workspace, operator.workspace_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"workspace load: {type(exc).__name__}: {exc}",
        ) from exc
    if ws is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="workspace missing")
    return ws


def get_csrf_token_for(operator: Operator, db: Session) -> str:
    """Return the current CSRF token for the operator's active session."""
    sess = (
        db.query(SessionModel)
        .filter(SessionModel.operator_id == operator.id)
        .order_by(SessionModel.created_at.desc())
        .first()
    )
    if sess is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no session")
    return new_csrf_token(sess.id)


def require_csrf(
    request: Request,
    operator: Operator = Depends(get_current_operator),
    db: Session = Depends(get_db),
    x_relay_csrf: Optional[str] = Header(default=None, alias=CSRF_HEADER_NAME),
) -> Operator:
    """Dependency that 403s on missing/invalid CSRF for mutating requests."""
    auth_header = request.headers.get("Authorization") or ""
    sid = ""
    if auth_header.startswith("Bearer "):
        sid = auth_header[7:].strip()
    if not sid:
        raw = request.cookies.get(SESSION_COOKIE_NAME, "")
        sid = unsign_session(raw) or ""
    token = x_relay_csrf or request.headers.get(CSRF_HEADER_NAME, "")
    if not token or not verify_csrf_token(token, sid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="csrf failed")
    return operator


def rate_limit_key(request: Request) -> str:
    """Per-IP key for the public share rate limiter."""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def session_expiry() -> datetime:
    return _now() + timedelta(days=get_settings().session_ttl_days)
