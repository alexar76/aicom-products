from __future__ import annotations

import asyncio
import os

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.config import get_settings
from app.db import Base, engine
from app.models import *  # noqa: F401 — register models on Base
from app.routers import advisory, analytics, auth, embed, operator
from app.services.heartbeat import heartbeat_loop
from app.services.seeding import seed_demo_user

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    seed_demo_user()
    task = asyncio.create_task(heartbeat_loop())
    yield
    task.cancel()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(advisory.router)
app.include_router(auth.router)
app.include_router(operator.router)
app.include_router(analytics.router)
app.include_router(embed.router)


@app.get("/api/health")
async def health():
    from sqlalchemy import text as sql_text

    from app.config import get_settings

    cfg = get_settings()
    db_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(sql_text("SELECT 1"))
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "service": cfg.app_name,
        "database": "ok" if db_ok else "error",
        "hub": os.getenv("AIMARKET_HUB_URL", "https://modelmarket.dev"),
    }


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    static_dir = "frontend/dist"
    file_path = os.path.join(static_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(static_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend bundle not built")
