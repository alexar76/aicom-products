"""Relay backend package.

The app factory lives in `backend.app.main`. The models package is imported
here so that `Base.metadata.create_all()` (used by tests and the seed helper)
discovers every table.
"""
from .config import Settings, get_settings  # noqa: F401
from .db import Base, SessionLocal, engine, get_db  # noqa: F401
from . import models  # noqa: F401  (side-effect import for metadata)
from . import schemas  # noqa: F401
from .main import app, create_app  # noqa: F401
