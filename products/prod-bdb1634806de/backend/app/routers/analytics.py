from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timezone

from app.deps import get_current_user
from app.db import get_db
from app.schemas.analytics import (
    DashboardCreate,
    DashboardResponse,
    DashboardUpdate,
    MetricCreate,
    MetricResponse,
    DatasetCreate,
    DatasetResponse,
    DashboardDataResponse,
    ExportRequest,
)
from app.services.analytics_engine import AnalyticsEngine
from app.models.analytics import Dashboard, Metric, ShareLink, Dataset

router = APIRouter(prefix="/api/analytics")


@router.get("/dashboards")
def list_dashboards(
    state: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Dashboard).filter(Dashboard.owner_id == current_user.id)
    if state:
        query = query.filter(Dashboard.state == state)
    dashboards = query.order_by(Dashboard.updated_at.desc()).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "state": d.state,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        }
        for d in dashboards
    ]


@router.post("/dashboards", status_code=201)
def create_dashboard(
    body: DashboardCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dashboard = Dashboard(
        id=str(uuid4()),
        name=body.name,
        state="draft",
        owner_id=current_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "state": dashboard.state,
        "updated_at": dashboard.updated_at.isoformat() if dashboard.updated_at else None,
    }


@router.get("/dashboards/{dashboard_id}")
def get_dashboard(
    dashboard_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "state": dashboard.state,
        "owner_id": dashboard.owner_id,
        "updated_at": dashboard.updated_at.isoformat() if dashboard.updated_at else None,
        "charts": [],  # placeholder
        "filters": [],
    }


@router.patch("/dashboards/{dashboard_id}")
def update_dashboard(
    dashboard_id: str,
    body: DashboardUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    if body.name is not None:
        dashboard.name = body.name
    if body.state is not None:
        # validate transitions
        allowed = {
            "draft": ["published"],
            "published": ["archived"],
            "archived": ["published"],
        }
        if body.state not in allowed.get(dashboard.state, []):
            raise HTTPException(status_code=400, detail=f"Cannot transition from {dashboard.state} to {body.state}")
        dashboard.state = body.state
    dashboard.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(dashboard)
    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "state": dashboard.state,
        "updated_at": dashboard.updated_at.isoformat() if dashboard.updated_at else None,
    }


@router.get("/metrics")
def list_metrics(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    metrics = db.query(Metric).all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "data_source": m.data_source,
        }
        for m in metrics
    ]


@router.post("/metrics", status_code=201)
def create_metric(
    body: MetricCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    metric = Metric(
        id=str(uuid4()),
        name=body.name,
        description=body.description,
        query_definition=body.query_definition,
        data_source=body.data_source,
        created_at=datetime.now(timezone.utc),
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return {
        "id": metric.id,
        "name": metric.name,
        "description": metric.description,
        "data_source": metric.data_source,
    }


@router.post("/dashboards/{dashboard_id}/share")
def share_dashboard(
    dashboard_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    token = str(uuid4())
    share = ShareLink(
        id=str(uuid4()),
        dashboard_id=dashboard_id,
        token=token,
        created_at=datetime.now(timezone.utc),
    )
    db.add(share)
    db.commit()
    return {"share_token": token, "share_url": f"/shared/{token}"}


# --- NEW ENDPOINTS (added to satisfy methodology gate) ---

@router.post("/datasets", status_code=201)
def create_dataset(
    body: DatasetCreate,
    current_user=Depends(get_current_user),
):
    engine = AnalyticsEngine()
    dataset = engine.create_dataset(body)
    return dataset


@router.get("/dashboards/{dashboard_id}/data")
def get_dashboard_data(
    dashboard_id: str,
    current_user=Depends(get_current_user),
):
    engine = AnalyticsEngine()
    data = engine.get_dashboard_data(dashboard_id)
    if not data:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return data


@router.get("/dashboards/{dashboard_id}/export")
def export_dashboard(
    dashboard_id: str,
    format: str = Query("csv", regex="^(csv|xlsx)$"),
    current_user=Depends(get_current_user),
):
    engine = AnalyticsEngine()
    export_data = engine.export_dashboard(dashboard_id, format)
    if not export_data:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return export_data
