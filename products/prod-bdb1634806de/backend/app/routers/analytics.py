from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..deps import get_current_user
from ..schemas.analytics import DashboardCreate, DashboardUpdate, MetricCreate, ChartCreate, FilterCreate, ShareResponse
from ..models.analytics import Dashboard, Metric, Chart, Filter, ShareLink
from ..utils.security import generate_token
import uuid

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

def slugify(name: str) -> str:
    import re
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

@router.get("/dashboards")
async def list_dashboards(
    state: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Dashboard).filter(Dashboard.owner_id == current_user.id)
    if state:
        query = query.filter(Dashboard.state == state)
    dashboards = query.order_by(Dashboard.updated_at.desc()).all()
    return [{"id": d.id, "name": d.name, "state": d.state, "updated_at": d.updated_at.isoformat()} for d in dashboards]

@router.post("/dashboards", status_code=201)
async def create_dashboard(
    payload: DashboardCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard = Dashboard(
        name=payload.name,
        slug=slugify(payload.name) + "-" + str(uuid.uuid4())[:8],
        state="draft",
        owner_id=current_user.id
    )
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    return {"id": dashboard.id, "name": dashboard.name, "state": dashboard.state}

@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(
    dashboard_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id, Dashboard.owner_id == current_user.id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "state": dashboard.state,
        "charts": [],
        "filters": []
    }

@router.patch("/dashboards/{dashboard_id}")
async def update_dashboard(
    dashboard_id: str,
    payload: DashboardUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id, Dashboard.owner_id == current_user.id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    if payload.name is not None:
        dashboard.name = payload.name
        dashboard.slug = slugify(payload.name) + "-" + str(uuid.uuid4())[:8]
    if payload.state is not None:
        valid_transitions = {
            "draft": ["published"],
            "published": ["archived"],
            "archived": ["published"]
        }
        if payload.state not in valid_transitions.get(dashboard.state, []):
            raise HTTPException(status_code=400, detail=f"Invalid state transition from {dashboard.state} to {payload.state}")
        dashboard.state = payload.state
    db.commit()
    db.refresh(dashboard)
    return {"id": dashboard.id, "name": dashboard.name, "state": dashboard.state}

@router.get("/metrics")
async def list_metrics(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    metrics = db.query(Metric).all()
    return [{"id": m.id, "name": m.name, "source": m.data_source} for m in metrics]

@router.post("/metrics", status_code=201)
async def create_metric(
    payload: MetricCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    metric = Metric(
        name=payload.name,
        description=payload.description,
        query_definition=payload.query_definition,
        data_source=payload.data_source
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return {"id": metric.id, "name": metric.name, "source": metric.data_source}

@router.post("/charts", status_code=201)
async def create_chart(payload: ChartCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    chart = Chart(**payload.dict())
    db.add(chart)
    db.commit()
    db.refresh(chart)
    return {"id": chart.id}

@router.post("/filters", status_code=201)
async def create_filter(payload: FilterCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    flt = Filter(**payload.dict())
    db.add(flt)
    db.commit()
    db.refresh(flt)
    return {"id": flt.id}

@router.post("/dashboards/{dashboard_id}/share", response_model=ShareResponse)
async def share_dashboard(
    dashboard_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id, Dashboard.owner_id == current_user.id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    token = generate_token()
    share_link = ShareLink(dashboard_id=dashboard.id, token=token)
    db.add(share_link)
    db.commit()
    return ShareResponse(share_token=token, share_url=f"/shared/{token}")
