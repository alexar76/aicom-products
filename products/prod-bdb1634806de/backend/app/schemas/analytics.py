from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DashboardCreate(BaseModel):
    name: str

class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None  # 'draft', 'published', 'archived'

class DashboardResponse(BaseModel):
    id: str
    name: str
    state: str
    created_at: datetime
    updated_at: datetime

class MetricCreate(BaseModel):
    name: str
    description: Optional[str] = None
    query_definition: Dict[str, Any]
    data_source: str  # 'advisory', 'audit', 'allowance'

class MetricResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    query_definition: Dict[str, Any]
    data_source: str
    created_at: datetime

class ChartCreate(BaseModel):
    dashboard_id: str
    metric_id: str
    chart_type: str  # 'line', 'bar', 'area', 'table'
    config: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, Any]] = None

class ChartResponse(BaseModel):
    id: str
    dashboard_id: str
    metric_id: str
    chart_type: str
    config: Optional[Dict[str, Any]]
    position: Optional[Dict[str, Any]]
    created_at: datetime

class ShareResponse(BaseModel):
    share_token: str
    share_url: str


DashboardResponse = ShareResponse
MetricResponse = ShareResponse
DatasetCreate = ChartCreate
DatasetResponse = ShareResponse
DashboardDataResponse = DashboardUpdate


class ExportRequest(BaseModel):
    format: str = "csv"

class DatasetCreate(BaseModel):
    name: str
    source: str  # 'advisory', 'audit', 'allowance'
    schema_: Optional[Dict[str, Any]] = Field(None, alias="schema")

class DatasetResponse(BaseModel):
    id: str
    name: str
    source: str
    schema_: Optional[Dict[str, Any]] = Field(None, alias="schema")
    created_at: datetime

class DashboardDataResponse(BaseModel):
    dashboard_id: str
    charts: List[Dict[str, Any]]
    filters: List[Dict[str, Any]]
    metrics: List[Dict[str, Any]]

class ExportRequest(BaseModel):
    format: str  # 'csv' or 'xlsx'
