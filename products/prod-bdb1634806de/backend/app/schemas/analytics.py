from pydantic import BaseModel
from typing import Optional, List

class DashboardCreate(BaseModel):
    name: str

class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None

class MetricCreate(BaseModel):
    name: str
    description: Optional[str] = None
    query_definition: Optional[dict] = None
    data_source: str

class ChartCreate(BaseModel):
    dashboard_id: str
    metric_id: str
    chart_type: str
    config: Optional[dict] = None
    position: Optional[dict] = None

class FilterCreate(BaseModel):
    dashboard_id: str
    name: str
    config: Optional[dict] = None

class ShareResponse(BaseModel):
    share_token: str
    share_url: str
