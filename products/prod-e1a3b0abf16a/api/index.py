"""Vercel serverless ASGI entrypoint for Relay.

Vercel routes every `/api/*` request to this module. We expose the FastAPI
`app` object under the conventional `app` name so the platform picks it up,
and we also provide a `handler` for compatibility with `mangum`-style adapters.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the repo root is on sys.path so `backend.app` imports work in
# Vercel's serverless environment.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Vercel ephemeral filesystem: default the DB path to /tmp so the SQLite file
# is writable in serverless invocations. In production the operator is
# expected to point RELAY_DB_PATH at a persistent store.
os.environ.setdefault("RELAY_DB_PATH", "/tmp/relay.db")

from backend.app.main import app  # noqa: E402  (import after path tweak)

__all__ = ["app", "handler"]


def handler(request, context):  # pragma: no cover - Vercel runtime shape
    """Mangum-style adapter; rarely used because Vercel speaks ASGI directly."""
    return app
