from sqlalchemy import Column, String, Float, Boolean, DateTime, Enum
from datetime import datetime, timezone
from ..db import Base
from .user import gen_uuid

class Advisory(Base):
    __tablename__ = "advisories"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    rounded_lat = Column(Float, nullable=False)
    rounded_lon = Column(Float, nullable=False)
    hazard = Column(Enum("WEATHER", "WILDFIRE", "FLOOD", name="hazard_type"), nullable=False)
    level = Column(Enum("CALM", "WATCH", "WARNING", "EMERGENCY", "UNKNOWN", name="hazard_level"), nullable=False)
    measurement = Column(String, nullable=True)
    distance_km = Column(Float, nullable=True)
    receipt_digest = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_cached = Column(Boolean, default=False)
    sim_flag = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class CachedMeshReading(Base):
    __tablename__ = "cached_mesh_readings"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    rounded_lat = Column(Float, nullable=False)
    rounded_lon = Column(Float, nullable=False)
    capability_name = Column(String(255), nullable=False)
    response_json = Column(String, nullable=False)  # JSON as text
    receipt_digest = Column(String(255), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class WatchLocation(Base):
    __tablename__ = "watch_locations"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    label = Column(String(255), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

from sqlalchemy import Column, Integer


class AllowanceState(Base):
    __tablename__ = "allowance_state"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    used_invocations = Column(Integer, default=0)
    max_invocations = Column(Integer, default=10)
    window_seconds = Column(Integer, default=3600)
    renews_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
