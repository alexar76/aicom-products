from fastapi import FastAPI
from app.services.demo_seed import seed_demo_user
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .db import Base, engine
from .seed import seed_demo_user
from .services.seeding import seed_demo_user
from .config import get_settings
from .models import *  # noqa: F401 — register models on Base
from .routers import advisory, auth, operator, analytics, embed
from .seed import seed_demo_user
from .services.heartbeat import heartbeat_loop
import asyncio
import os

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_all covers serverless where Alembic is not run.
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    seed_demo_user()
    seed_demo_user()
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
    return {"status": "ok"}


from fastapi.responses import FileResponse


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        return {"detail": "Not Found"}, 404
    static_dir = "frontend/dist"
    file_path = os.path.join(static_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(static_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": "Sentinel API"}
