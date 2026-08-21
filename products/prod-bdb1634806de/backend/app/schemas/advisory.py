from pydantic import BaseModel
from typing import Optional, List

class HazardResponse(BaseModel):
    type: str
    level: str
    measurement: Optional[str] = None
    distance_km: Optional[float] = None
    receipt: Optional[str] = None
    timestamp: Optional[str] = None
    is_cached: bool = False
    sim: bool = False

class ThresholdInfo(BaseModel):
    name: str
    condition: str
    fired: bool

class OverallResponse(BaseModel):
    level: str
    reason: str
    receipt: Optional[str] = None

class AdvisoryResponse(BaseModel):
    overall: OverallResponse
    hazards: List[HazardResponse]
    thresholds: List[ThresholdInfo]
    location: dict
