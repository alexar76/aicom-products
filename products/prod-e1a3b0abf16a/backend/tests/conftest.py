"""Pytest fixtures shared by the unit and integration suites."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Iterator
import atexit
import shutil
import sys

import pytest
from fastapi.testclient import TestClient

# Use a per-test temp DB so suites are isolated.
_TMP_DIR = tempfile.mkdtemp(prefix="relay-tests-")
atexit.register(shutil.rmtree, str(_TMP_DIR), ignore_errors=True)
_DB_PATH = Path(_TMP_DIR) / "relay-test.db"

# Only set test defaults when running under pytest to avoid leaking a
# known-weak SESSION_SECRET into production contexts (e.g. REPL imports
# of conftest helpers or runtime tooling that walks the package).
if "pytest" in sys.modules:
    os.environ.setdefault("RELAY_DB_PATH", str(_DB_PATH))
    os.environ.setdefault("SESSION_SECRET", "test-secret-please-be-32-chars-or-more")
    os.environ.setdefault("CORS_ORIGIN", "http://localhost:5173")

from backend.app.config import get_settings  # noqa: E402  (env must come first)
from backend.app.db import init_db  # noqa: E402
from backend.app.main import create_app  # noqa: E402
from backend.app.security import hash_password, new_csrf_token  # noqa: E402
from backend.app.models import Operator, OperatorRole, Session as SessionModel, Workspace, WorkspaceTier  # noqa: E402
from backend.app.db import session_scope  # noqa: E402
from backend.app.deps import session_expiry  # noqa: E402


@pytest.fixture()
def settings():
    return get_settings()


@pytest.fixture()
def app():
    application = create_app()
    init_db()
    return application


@pytest.fixture()
def client(app) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def seeded_user(app) -> dict:
    """Insert a workspace + operator directly, bypassing the public signup."""
    with session_scope() as db:
        ws = Workspace(name="Acme Studio", tier=WorkspaceTier.solo, accent_color="#8a1c2b")
        db.add(ws)
        db.flush()
        op_ = Operator(
            email="[email protected]",
            password_hash=hash_password("supersecret1!"),
            workspace_id=ws.id,
            role=OperatorRole.owner,
        )
        db.add(op_)
        db.flush()
        sid = "test-session-1"
        csrf = new_csrf_token(sid)
        db.add(
            SessionModel(
                id=sid,
                operator_id=op_.id,
                csrf_token=csrf,
                expires_at=session_expiry(),
            )
        )
        return {
            "operator_id": op_.id,
            "workspace_id": ws.id,
            "email": op_.email,
            "password": "supersecret1!",
            "session_id": sid,
            "csrf": csrf,
        }


@pytest.fixture()
def auth_client(client, seeded_user):
    """TestClient with the session cookie + csrf header pre-set."""
    from backend.app.deps import SESSION_COOKIE_NAME
    from backend.app.security import sign_session

    client.cookies.set(SESSION_COOKIE_NAME, sign_session(seeded_user["session_id"]))
    client.headers["x-relay-csrf"] = seeded_user["csrf"]
    return client


@pytest.fixture(autouse=True)
def _reset_db():
    """Drop and recreate all tables before each test for isolation."""
    from backend.app.db import engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope="session")
def receipt_schema_path():
    """Locate the JSON receipt schema relative to the project root."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            schema = parent / "docs" / "receipts.schema.json"
            if schema.exists():
                return schema
    fallback = Path(__file__).resolve().parents[3] / "docs" / "receipts.schema.json"
    return fallback if fallback.exists() else None
