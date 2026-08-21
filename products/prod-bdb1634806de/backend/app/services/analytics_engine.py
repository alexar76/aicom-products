from sqlalchemy.orm import Session
from ..models.audit import InvokeAuditLog
from ..models.advisory import Advisory

def get_invoke_timeseries(db: Session, metric_type: str):
    # simplified: return aggregated counts per day
    if metric_type == "invokes":
        return db.query(InvokeAuditLog).with_entities(InvokeAuditLog.created_at, InvokeAuditLog.cost_usd).all()
    return []
