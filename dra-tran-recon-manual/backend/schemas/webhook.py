"""Webhook schemas."""
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime


class WebhookBase(BaseModel):
    """Base webhook schema."""
    url: HttpUrl
    events: List[str] = Field(default_factory=list, description="List of events to subscribe to. Empty = all events.")
    secret: Optional[str] = Field(default=None, description="Secret for HMAC signature verification")


class WebhookCreate(WebhookBase):
    """Schema for creating a webhook."""
    pass


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook."""
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    secret: Optional[str] = None
    status: Optional[str] = None


class Webhook(WebhookBase):
    """Webhook response schema."""
    id: int
    client_id: int
    status: str
    failure_count: int
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WebhookDelivery(BaseModel):
    """Webhook delivery log schema."""
    id: int
    webhook_id: int
    job_id: Optional[int]
    event: str
    status_code: Optional[int]
    success: bool
    error_message: Optional[str]
    attempt_count: int
    created_at: datetime
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True
