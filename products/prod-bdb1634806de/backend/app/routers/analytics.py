from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ..deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# ---------- Dashboards ----------

@router.get("/dashboards")
async def list_dashboards(
    state: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """List dashboards, optionally filtered by state."""
    # TODO: implement real query
    return []

@router.post("/dashboards", status_code=201)
async def create_dashboard(
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new dashboard (initial state draft)."""
    # TODO: implement creation
    return {"id": "placeholder", "name": payload.get("name", ""), "state": "draft"}

@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(
    dashboard_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get dashboard detail with charts, filters, metrics."""
    # TODO: implement retrieval
    return {"id": dashboard_id, "name": "...", "state": "draft", "charts": [], "filters": []}

@router.patch("/dashboards/{dashboard_id}")
async def update_dashboard(
    dashboard_id: str,
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    """Update dashboard name or transition state."""
    # TODO: implement update
    return {"id": dashboard_id, "name": payload.get("name", ""), "state": payload.get("state", "draft")}

@router.get("/dashboards/{dashboard_id}/data")
async def get_dashboard_data(
    dashboard_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the actual data backing a dashboard (drill-down)."""
    # TODO: implement data retrieval
    return {"dashboard_id": dashboard_id, "rows": []}

@router.get("/dashboards/{dashboard_id}/export")
async def export_dashboard(
    dashboard_id: str,
    format: str = Query("csv"),
    current_user: User = Depends(get_current_user)
):
    """Export dashboard data as CSV or XLSX."""
    # TODO: implement export
    return {"status": "ok", "format": format}

@router.post("/dashboards/{dashboard_id}/share")
async def share_dashboard(
    dashboard_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate share token for dashboard."""
    # TODO: implement sharing
    return {"share_token": "placeholder", "share_url": f"/shared/placeholder"}

# ---------- Metrics ----------

@router.get("/metrics")
async def list_metrics(
    current_user: User = Depends(get_current_user)
):
    """List available metrics."""
    # TODO: implement
    return []

@router.post("/metrics", status_code=201)
async def create_metric(
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a custom metric."""
    # TODO: implement
    return {"id": "placeholder", "name": payload.get("name", "")}

# ---------- Datasets ----------

@router.post("/datasets", status_code=201)
async def create_dataset(
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a dataset definition."""
    # TODO: implement
    return {"id": "placeholder", "name": payload.get("name", "")}

# ---------- Filters ----------

@router.get("/filters")
async def list_filters(
    current_user: User = Depends(get_current_user)
):
    """List available filters."""
    # TODO: implement
    return []
