from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
import re

from app.db import get_db
from app.models import Operator, Workspace, Handoff, AuditEntry
from app.config import settings
from app.routers.handoffs import get_current_operator_bearer  # shared bearer+cookie dependency

router = APIRouter(prefix="/api/workspace", tags=["workspace"])


@router.get("/branding")
async def get_branding(
    request: Request = None,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator_bearer),
):
    workspace = db.get(Workspace, current_operator.workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"workspace": _workspace_to_dict(workspace)}


@router.put("/branding")
async def update_branding(
    payload: dict = Body(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator_bearer),
):
    workspace = db.get(Workspace, current_operator.workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if workspace.tier == "free":
        raise HTTPException(status_code=402, detail="Upgrade required to edit branding")
    name = payload.get("name")
    logo_url = payload.get("logo_url")
    accent_color = payload.get("accent_color")
    if name is not None:
        workspace.name = name
    if logo_url is not None:
        if not logo_url.startswith("https://"):
            raise HTTPException(status_code=422, detail="logo_url must be https")
        workspace.logo_url = logo_url
    if accent_color is not None:
        if not re.match(r'^#[0-9a-fA-F]{6}$', accent_color):
            raise HTTPException(status_code=422, detail="accent_color must be 6-digit hex")
        workspace.accent_color = accent_color
    db.commit()
    db.refresh(workspace)
    return {"workspace": _workspace_to_dict(workspace)}


@router.get("/export.csv")
async def export_csv(
    request: Request = None,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator_bearer),
):
    workspace = db.get(Workspace, current_operator.workspace_id)
    if current_operator.role != "owner":
        raise HTTPException(status_code=403, detail="Only owners can export")
    handoffs = db.query(Handoff).filter(Handoff.workspace_id == workspace.id).all()
    csv_lines = ["id,client_name,project_name,status,created_at,approved_at"]
    for h in handoffs:
        csv_lines.append(f"{h.id},{h.client_name},{h.project_name},{h.status},{h.created_at.isoformat()},{h.approved_at.isoformat() if h.approved_at else ''}")
    return PlainTextResponse("\n".join(csv_lines), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=relay_export.csv"})


def _workspace_to_dict(w: Workspace) -> dict:
    return {
        "id": w.id,
        "name": w.name,
        "logo_url": w.logo_url,
        "accent_color": w.accent_color,
        "tier": w.tier,
        "created_at": w.created_at.isoformat() if w.created_at else None,
    }
