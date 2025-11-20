import uuid
from sqlalchemy import (
    Column, Integer, String, Boolean, Text, Numeric, DateTime
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(255), nullable=False)
    sku_normalized = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255))
    description = Column(Text)
    price = Column(Numeric(10, 2))
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255))
    status = Column(String(50), default="pending", index=True)
    total_rows = Column(Integer)
    processed_rows = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1024), nullable=False)
    event_type = Column(String(255), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    last_response_code = Column(Integer)
    last_response_time_ms = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
