# aicom-factory-auth-seed-helper
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
import logging

from ..db import get_db
from ..services.seeding import seed_demo_user
from ..schemas.auth import LoginRequest
from ..models.user import User
from ..utils.security import verify_password, create_access_token, hash_password
import os
import jwt
import datetime
os.environ.setdefault("SECRET_KEY", "sentinel-dev-secret-change-in-prod")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    seed_demo_user(db)

    # Authenticate
    try:
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Authentication error")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        secret = os.environ.get("SECRET_KEY", "sentinel-dev-secret-change-in-prod")
        payload = {
            "sub": user.email,
            "email": user.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
    except Exception as e:
        logger.exception("Token generation failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token generation failed")
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=3600,
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "logged out"}
