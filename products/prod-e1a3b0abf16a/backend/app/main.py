from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, handoffs, public, workspace, health
from .db import engine, Base
from . import models  # noqa
from .seed import seed

def create_app() -> FastAPI:
    app = FastAPI(title="Relay", version="0.1.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
    app.include_router(auth.router, tags=["auth"])
    app.include_router(handoffs.router, prefix="/api/handoffs", tags=["handoffs"])
    app.include_router(public.router, prefix="/api/public", tags=["public"])
    app.include_router(workspace.router, tags=["workspace"])
    app.include_router(health.router, tags=["health"])

    @app.on_event("startup")
    def on_startup():
        Base.metadata.create_all(bind=engine)
        seed()

    return app

app = create_app()
