"""
Security utilities for Relay: password hashing (argon2id), signed sessions,
CSRF tokens, share tokens, SHA-256 hashing, and session invalidation.
"""
import hashlib
import secrets
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from itsdangerous import URLSafeTimedSerializer

from .config import settings

ph = PasswordHasher()
serializer = URLSafeTimedSerializer(settings.session_secret, salt="relay-session")

# In-memory set of invalidated session token IDs.
# NOTE: This is in-process state and will not scale beyond a single worker/replica.
# An operator who logs out of one instance will still be authenticated on another.
# For production, replace with a shared store (Redis, DB table) when running
# multiple workers. Cleared on restart – acceptable for single-worker MVP.
_invalidated_sessions: set[str] = set()


def hash_password(password: str) -> str:
    """Return argon2id hash of the given password."""
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Return True if the password matches the stored hash."""
    try:
        return ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def create_session_token(operator_id: str) -> str:
    """Create a signed session token for the given operator id."""
    return serializer.dumps({"operator_id": operator_id})


def decode_session_token(token: str) -> Optional[dict]:
    """Decode and validate a session token. Returns payload dict or None."""
    try:
        return serializer.loads(token)
    except Exception:
        return None


def create_csrf_token() -> str:
    """Generate a random CSRF token."""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected: str) -> bool:
    """Constant-time comparison of CSRF tokens."""
    return secrets.compare_digest(token, expected)


def new_share_token() -> str:
    """Generate a 128-bit URL-safe share token."""
    return secrets.token_urlsafe(16)


def sha256_text(text: str) -> str:
    """Return the SHA-256 hex digest of the given text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Aliases to satisfy existing imports without breaking callers
new_csrf_token = create_csrf_token
unsign_session = decode_session_token
sign_session = create_session_token


def invalidate_session(token: str) -> None:
    """Mark a session token as invalidated (logout)."""
    _invalidated_sessions.add(token)


def is_session_invalidated(token: str) -> bool:
    """Return True if the session token has been invalidated."""
    return token in _invalidated_sessions
