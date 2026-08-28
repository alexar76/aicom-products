"""Idempotent demo operator seed for sandbox + Vercel.

Uses SANDBOX_DEMO_* (injected by the factory on Vercel and compose preview),
falling back to Settings defaults that match the factory live-gate identity.
Always upserts the password so a redeploy with a rotated factory password
still logs in.
"""
from __future__ import annotations

import os

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import SessionLocal
from app.models.user import User
from app.utils.security import hash_password


def _demo_credentials() -> tuple[str, str] | None:
    settings = get_settings()
    email = (
        os.getenv("SANDBOX_DEMO_EMAIL")
        or os.getenv("VITE_SANDBOX_DEMO_EMAIL")
        or settings.sandbox_demo_email
        or ""
    ).strip()
    password = (
        os.getenv("SANDBOX_DEMO_PASSWORD")
        or os.getenv("VITE_SANDBOX_DEMO_PASSWORD")
        or settings.sandbox_demo_password
        or ""
    ).strip()
    if not email or not password:
        return None
    return email, password



def _aicom_demo_user_id(email: str) -> str:
    """Stable PK across serverless instances (live_ephemeral_identity gate)."""
    import uuid as _uuid
    return str(_uuid.uuid5(_uuid.NAMESPACE_URL, f"aicom-demo:{email.strip().lower()}"))

# aicom-factory-demo-uuid5
def seed_demo_user(db: Session | None = None) -> None:
    """Create or refresh the demo operator. Never raises."""
    creds = _demo_credentials()
    if not creds:
        return
    email, password = creds
    own = db is None
    session = db if db is not None else SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        hashed = hash_password(password)
        if user is None:
            user = User(
            id=_aicom_demo_user_id(email),
            email=email, hashed_password=hashed, role="admin")
            session.add(user)
        else:
            user.hashed_password = hashed
            if not getattr(user, "role", None):
                user.role = "admin"
        session.commit()
    except Exception as exc:
        session.rollback()
        print(f"Failed to seed demo user: {exc}")
    finally:
        if own:
            session.close()
