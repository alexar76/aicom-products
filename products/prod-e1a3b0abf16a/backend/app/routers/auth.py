"""
Authentication routes for Relay.
Provides JSON login endpoints at /login and /api/auth/login.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models, security
from ..config import settings
from ..db import get_db

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _create_access_token(operator_id) -> str:
    """Create a signed token carrying the operator id."""
    from itsdangerous import URLSafeTimedSerializer

    secret = getattr(settings, "SESSION_SECRET", "dev-secret")
    serializer = URLSafeTimedSerializer(secret)
    return serializer.dumps({"sub": str(operator_id)}, salt="relay-access-token")


def _set_session_cookie(response: Response, operator_id) -> str:
    token = _create_access_token(operator_id)
    secure = getattr(settings, "SESSION_COOKIE_SECURE", False)
    max_age = getattr(settings, "SESSION_COOKIE_MAX_AGE", 60 * 60 * 24 * 7)  # 7 days
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=max_age,
        path="/",
    )
    return token


def _authenticate(payload: LoginRequest, response: Response, db: Session):
    operator = db.query(models.Operator).filter(models.Operator.email == payload.email).first()
    if not operator or not security.verify_password(payload.password, operator.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = _set_session_cookie(response, operator.id)
    return LoginResponse(access_token=token, token_type="bearer")


@router.post("/login", response_model=LoginResponse)
def login_root(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Login for operator console (root path)."""
    return _authenticate(payload, response, db)


@router.post("/api/auth/login", response_model=LoginResponse)
def login_api(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Login for API clients (/api/auth/login)."""
    return _authenticate(payload, response, db)
