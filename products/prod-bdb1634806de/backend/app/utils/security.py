import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from ..config import get_settings

settings = get_settings()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

get_password_hash = hash_password

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: str, email: str) -> str:
    issuer = os.getenv("JWT_ISSUER", "sentinel")
    audience = os.getenv("JWT_AUDIENCE", "sentinel-api")
    payload = {
        "sub": user_id,
        "email": email,
        "iss": issuer,
        "aud": audience,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def decode_access_token(token: str) -> dict:
    issuer = os.getenv("JWT_ISSUER", "sentinel")
    audience = os.getenv("JWT_AUDIENCE", "sentinel-api")
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
            options={"verify_exp": True},
            issuer=issuer,
            audience=audience,
        )
    except jwt.PyJWTError:
        return {}

