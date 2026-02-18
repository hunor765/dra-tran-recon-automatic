"""Webhook management endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import get_current_user, require_admin
from core.database import get_db
from core.rate_limiter import limiter, RateLimits
from models.webhook import Webhook, WebhookEvent, WebhookStatus
from schemas.webhook import Webhook as WebhookSchema, WebhookCreate, WebhookUpdate

router = APIRouter()


@router.post("/", response_model=WebhookSchema)
@limiter.limit(RateLimits.CREATE)
async def create_webhook(
    request: Request,
    client_id: int,
    webhook: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Create a new webhook for a client."""
    # Validate events
    valid_events = [e.value for e in WebhookEvent]
    for event in webhook.events:
        if event not in valid_events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event: {event}. Must be one of: {', '.join(valid_events)}"
            )
    
    db_webhook = Webhook(
        client_id=client_id,
        url=str(webhook.url),
        secret=webhook.secret,
        events=webhook.events,
        status=WebhookStatus.ACTIVE
    )
    db.add(db_webhook)
    await db.commit()
    await db.refresh(db_webhook)
    return db_webhook


@router.get("/", response_model=List[WebhookSchema])
@limiter.limit(RateLimits.LIST)
async def list_webhooks(
    request: Request,
    client_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """List all webhooks for a client."""
    result = await db.execute(
        select(Webhook).where(Webhook.client_id == client_id)
    )
    webhooks = result.scalars().all()
    return webhooks


@router.get("/{webhook_id}", response_model=WebhookSchema)
@limiter.limit(RateLimits.GET)
async def get_webhook(
    request: Request,
    client_id: int,
    webhook_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get a specific webhook."""
    result = await db.execute(
        select(Webhook)
        .where(Webhook.id == webhook_id)
        .where(Webhook.client_id == client_id)
    )
    webhook = result.scalars().first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook


@router.put("/{webhook_id}", response_model=WebhookSchema)
@limiter.limit(RateLimits.UPDATE)
async def update_webhook(
    request: Request,
    client_id: int,
    webhook_id: int,
    webhook_update: WebhookUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Update a webhook."""
    result = await db.execute(
        select(Webhook)
        .where(Webhook.id == webhook_id)
        .where(Webhook.client_id == client_id)
    )
    webhook = result.scalars().first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Validate events if provided
    if webhook_update.events is not None:
        valid_events = [e.value for e in WebhookEvent]
        for event in webhook_update.events:
            if event not in valid_events:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid event: {event}. Must be one of: {', '.join(valid_events)}"
                )
        webhook.events = webhook_update.events
    
    if webhook_update.url is not None:
        webhook.url = str(webhook_update.url)
    
    if webhook_update.secret is not None:
        webhook.secret = webhook_update.secret
    
    if webhook_update.status is not None:
        webhook.status = webhook_update.status
        # Reset failure count when reactivating
        if webhook_update.status == WebhookStatus.ACTIVE:
            webhook.failure_count = 0
    
    await db.commit()
    await db.refresh(webhook)
    return webhook


@router.delete("/{webhook_id}")
@limiter.limit(RateLimits.DELETE)
async def delete_webhook(
    request: Request,
    client_id: int,
    webhook_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Delete a webhook."""
    result = await db.execute(
        select(Webhook)
        .where(Webhook.id == webhook_id)
        .where(Webhook.client_id == client_id)
    )
    webhook = result.scalars().first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    await db.delete(webhook)
    await db.commit()
    return {"message": "Webhook deleted successfully"}


@router.post("/{webhook_id}/test")
@limiter.limit(RateLimits.CONNECTOR_TEST)
async def test_webhook(
    request: Request,
    client_id: int,
    webhook_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Send a test webhook notification."""
    from core.webhooks import WebhookService
    from models.job import Job, JobStatus
    from datetime import datetime
    
    result = await db.execute(
        select(Webhook)
        .where(Webhook.id == webhook_id)
        .where(Webhook.client_id == client_id)
    )
    webhook = result.scalars().first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Create a fake job for testing
    test_job = Job(
        id=0,
        client_id=client_id,
        status=JobStatus.COMPLETED,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        result_summary={
            "match_rate": 95.5,
            "test": True,
            "message": "This is a test webhook notification"
        }
    )
    
    service = WebhookService(db)
    success = await service._send_webhook(
        webhook, WebhookEvent.JOB_COMPLETED, test_job, client_id
    )
    
    if success:
        return {"success": True, "message": "Test webhook sent successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to send test webhook. Check the webhook URL and try again."
        )
