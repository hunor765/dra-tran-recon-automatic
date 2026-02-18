"""Webhook model for job notifications."""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from core.database import Base


class WebhookEvent(str, enum.Enum):
    """Webhook event types."""
    JOB_STARTED = "job.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"


class WebhookStatus(str, enum.Enum):
    """Webhook delivery status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"  # Too many delivery failures


class Webhook(Base):
    """Webhook configuration for client notifications."""
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    
    # Webhook configuration
    url = Column(String, nullable=False)
    secret = Column(String, nullable=True)  # For HMAC signature
    events = Column(JSONB, default=list)  # List of WebhookEvent values
    status = Column(String, default=WebhookStatus.ACTIVE)
    
    # Delivery tracking
    failure_count = Column(Integer, default=0)
    last_success = Column(DateTime(timezone=True), nullable=True)
    last_failure = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WebhookDelivery(Base):
    """Webhook delivery attempt log."""
    __tablename__ = "webhook_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    
    # Delivery details
    event = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)
    
    # Response tracking
    status_code = Column(Integer, nullable=True)
    response_body = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    
    # Timing
    attempt_count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Success flag
    success = Column(Boolean, default=False)
