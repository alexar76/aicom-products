"""SQLAlchemy engine, session, and declarative base.

The engine points at the SQLite file configured by `Settings.relay_db_path`.
We enable `check_same_thread=False` because FastAPI uses a thread pool, and
we expose a `get_db` dependency that always closes the session.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    """Declarative base for every model in the project."""


_settings = get_settings()

# `check_same_thread=False` is required for SQLite under FastAPI's threaded
# request handling. WAL mode improves concurrent reads.
engine: Engine = create_engine(
    _settings.database_url,
    connect_args={"check_same_thread": False},
    future=True,
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _):  # noqa: ANN001
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Standalone context manager for scripts (seed, jobs)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Create every table declared on `Base.metadata`.

    Tests and the local seed helper call this; production runs Alembic.
    """
    # Import models so they are registered on `Base.metadata` before create_all.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
