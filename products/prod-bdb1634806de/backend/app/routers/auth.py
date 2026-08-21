from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..config import get_settings
from ..schemas.auth import LoginRequest
from ..models.user import User
from ..utils.security import verify_password, create_access_token, hash_password
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


@router.post("/login")
async def login(
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    # Serverless SQLite is empty every cold start — seed before authenticate.
    email = os.environ.get("SANDBOX_DEMO_EMAIL")
    password = os.environ.get("SANDBOX_DEMO_PASSWORD")
    if email and password:
        existing = db.query(User).filter(User.email == email).first()
        if not existing:
            hashed = hash_password(password)
            demo_user = User(email=email, hashed_password=hashed, role="admin")
            db.add(demo_user)
            db.commit()
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user.id), user.email)
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
