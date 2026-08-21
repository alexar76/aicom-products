import os
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.user import User
from app.utils.security import hash_password, verify_password


def seed_demo_user() -> None:
    """Seed the sandbox demo operator user if it does not exist or if its
    password does not match the current environment. Reads credentials from
    SANDBOX_DEMO_EMAIL / SANDBOX_DEMO_PASSWORD with fallback to VITE_* mirror
    variables used by the frontend prefill, so a build that only sets VITE_*
    still creates a matching backend user.
    """
    email = os.getenv("SANDBOX_DEMO_EMAIL") or os.getenv("VITE_SANDBOX_DEMO_EMAIL") or "operator@sentinel.local"
    password = os.getenv("SANDBOX_DEMO_PASSWORD") or os.getenv("VITE_SANDBOX_DEMO_PASSWORD") or "SentinelDemo123!"

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            user = User(
                email=email,
                hashed_password=hash_password(password),
                role="operator",
            )
            db.add(user)
            db.commit()
        else:
            # Ensure the password matches the current demo credentials.
            if not verify_password(password, user.hashed_password):
                user.hashed_password = hash_password(password)
                db.commit()
    finally:
        db.close()
