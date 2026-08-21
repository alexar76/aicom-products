import os
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models.user import User
from .utils.security import get_password_hash


def seed_demo_user():
    db = SessionLocal()
    try:
        email = os.getenv("SANDBOX_DEMO_EMAIL", "operator@sentinel.local")
        password = os.getenv("SANDBOX_DEMO_PASSWORD", "SentinelDemo123!")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                role="admin",
            )
            db.add(user)
            db.commit()
            print(f"Seeded demo user: {email}")
        else:
            # Update password if env provides one
            if os.getenv("SANDBOX_DEMO_PASSWORD"):
                user.hashed_password = get_password_hash(password)
                db.commit()
    finally:
        db.close()
