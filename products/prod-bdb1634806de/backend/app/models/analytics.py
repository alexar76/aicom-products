from sqlalchemy import Column, String, Text, DateTime, Enum, JSON, ForeignKey
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from ..db import Base
from .user import gen_uuid

class Dashboard(Base):
    __tablename__ = "dashboards"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    state = Column(Enum("draft", "published", "archived", name="dashboard_state"), default="draft", nullable=False)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    share_token = Column(String(255), nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="dashboards")
    charts = relationship("Chart", back_populates="dashboard")
    filters = relationship("Filter", back_populates="dashboard")

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    query_definition = Column(JSON, nullable=True)
    data_source = Column(Enum("advisory", "audit", "allowance", name="data_source"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    charts = relationship("Chart", back_populates="metric")

class Chart(Base):
    __tablename__ = "charts"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    dashboard_id = Column(String(36), ForeignKey("dashboards.id"), nullable=False)
    metric_id = Column(String(36), ForeignKey("metrics.id"), nullable=False)
    chart_type = Column(Enum("line", "bar", "area", "table", name="chart_type"), nullable=False)
    config = Column(JSON, nullable=True)
    position = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    dashboard = relationship("Dashboard", back_populates="charts")
    metric = relationship("Metric", back_populates="charts")

class Filter(Base):
    __tablename__ = "filters"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    dashboard_id = Column(String(36), ForeignKey("dashboards.id"), nullable=False)
    name = Column(String(255), nullable=False)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    dashboard = relationship("Dashboard", back_populates="filters")

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    source = Column(Enum("advisory", "audit", "allowance", name="dataset_source"), nullable=False)
    schema = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class ShareLink(Base):
    __tablename__ = "share_links"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    dashboard_id = Column(String(36), ForeignKey("dashboards.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class DataExport(Base):
    __tablename__ = "data_exports"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    dashboard_id = Column(String(36), ForeignKey("dashboards.id"), nullable=False)
    format = Column(Enum("csv", "xlsx", name="export_format"), nullable=False)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
