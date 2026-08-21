from sqlalchemy.orm import Session

from .config import settings
from .db import SessionLocal
from .models.user import User
from .utils.security import hash_password


def seed_demo_user() -> None:
    """Seed the sandbox demo user if SANDBOX_DEMO_EMAIL/PASSWORD are set and the user does not exist."""
    email = getattr(settings, "SANDBOX_DEMO_EMAIL", None)
    password = getattr(settings, "SANDBOX_DEMO_PASSWORD", None)
    if not email or not password:
        return

    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return
        user = User(
            email=email,
            hashed_password=hash_password(password),
            role="admin",
        )
        db.add(user)
        db.commit()
    finally:
        db.close()
