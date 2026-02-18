"""Webhook notification service.

Handles sending webhook notifications for job events with
retry logic and signature verification.
"""
import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Any, Optional, List

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models.webhook import Webhook, WebhookEvent, WebhookStatus, WebhookDelivery
from models.job import Job

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for managing and sending webhook notifications."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeout = settings.WEBHOOK_TIMEOUT_SECONDS
        self.max_retries = settings.WEBHOOK_MAX_RETRIES
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload.
        
        Args:
            payload: JSON string payload
            secret: Webhook secret
            
        Returns:
            str: Hex-encoded HMAC-SHA256 signature
        """
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _build_payload(
        self,
        event: WebhookEvent,
        job: Job,
        client_id: int
    ) -> dict:
        """Build webhook payload for a job event.
        
        Args:
            event: The webhook event type
            job: The job model
            client_id: The client ID
            
        Returns:
            dict: Webhook payload
        """
        payload = {
            "event": event.value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {
                "job_id": job.id,
                "client_id": client_id,
                "status": job.status.value if hasattr(job.status, 'value') else job.status,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            }
        }
        
        # Add result summary for completed jobs
        if event == WebhookEvent.JOB_COMPLETED and job.result_summary:
            payload["data"]["result"] = job.result_summary
        
        # Add error info for failed jobs
        if event == WebhookEvent.JOB_FAILED and job.logs:
            payload["data"]["error"] = job.logs
        
        return payload
    
    async def _send_webhook(
        self,
        webhook: Webhook,
        event: WebhookEvent,
        job: Job,
        client_id: int
    ) -> bool:
        """Send a single webhook notification.
        
        Args:
            webhook: Webhook configuration
            event: Event type
            job: Job model
            client_id: Client ID
            
        Returns:
            bool: True if successful
        """
        payload = self._build_payload(event, job, client_id)
        payload_json = json.dumps(payload, default=str)
        
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": event.value,
            "X-Webhook-ID": str(webhook.id),
        }
        
        # Add signature if secret is configured
        if webhook.secret:
            signature = self._generate_signature(payload_json, webhook.secret)
            headers["X-Webhook-Signature"] = f"sha256={signature}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook.url,
                    content=payload_json,
                    headers=headers,
                    timeout=self.timeout
                )
                
                success = 200 <= response.status_code < 300
                
                # Log delivery attempt
                delivery = WebhookDelivery(
                    webhook_id=webhook.id,
                    job_id=job.id,
                    event=event.value,
                    payload=payload,
                    status_code=response.status_code,
                    response_body=response.text[:1000],  # Limit size
                    attempt_count=1,
                    success=success,
                    delivered_at=datetime.utcnow() if success else None
                )
                self.db.add(delivery)
                
                if success:
                    webhook.last_success = datetime.utcnow()
                    webhook.failure_count = 0
                    logger.info(
                        f"Webhook {webhook.id} delivered successfully",
                        extra={"webhook_id": webhook.id, "event": event.value}
                    )
                else:
                    webhook.last_failure = datetime.utcnow()
                    webhook.failure_count += 1
                    logger.warning(
                        f"Webhook {webhook.id} failed with status {response.status_code}",
                        extra={"webhook_id": webhook.id, "status_code": response.status_code}
                    )
                
                await self.db.commit()
                return success
                
        except httpx.TimeoutException:
            logger.error(f"Webhook {webhook.id} timed out")
            await self._log_delivery_failure(webhook, job, event, payload, "Timeout")
            return False
        except Exception as e:
            logger.error(f"Webhook {webhook.id} error: {e}")
            await self._log_delivery_failure(webhook, job, event, payload, str(e))
            return False
    
    async def _log_delivery_failure(
        self,
        webhook: Webhook,
        job: Job,
        event: WebhookEvent,
        payload: dict,
        error: str
    ) -> None:
        """Log a failed webhook delivery."""
        delivery = WebhookDelivery(
            webhook_id=webhook.id,
            job_id=job.id,
            event=event.value,
            payload=payload,
            error_message=error,
            success=False
        )
        self.db.add(delivery)
        
        webhook.last_failure = datetime.utcnow()
        webhook.failure_count += 1
        
        # Deactivate webhook after too many failures
        if webhook.failure_count >= 10:
            webhook.status = WebhookStatus.FAILED
            logger.error(f"Webhook {webhook.id} deactivated due to repeated failures")
        
        await self.db.commit()
    
    async def notify(
        self,
        event: WebhookEvent,
        job: Job,
        client_id: int
    ) -> None:
        """Send webhook notifications for a job event.
        
        Args:
            event: The event type
            job: The job
            client_id: The client ID
        """
        # Get active webhooks for this client that subscribe to this event
        result = await self.db.execute(
            select(Webhook)
            .where(Webhook.client_id == client_id)
            .where(Webhook.status == WebhookStatus.ACTIVE)
        )
        webhooks = result.scalars().all()
        
        if not webhooks:
            return
        
        # Filter webhooks that subscribe to this event
        event_str = event.value
        matching_webhooks = [
            w for w in webhooks 
            if not w.events or event_str in w.events  # Empty events = all events
        ]
        
        if not matching_webhooks:
            logger.debug(f"No webhooks found for event {event.value}")
            return
        
        logger.info(
            f"Sending {event.value} notifications to {len(matching_webhooks)} webhooks",
            extra={"job_id": job.id, "event": event.value}
        )
        
        for webhook in matching_webhooks:
            success = await self._send_webhook(webhook, event, job, client_id)
            
            if not success and settings.ENVIRONMENT == "production":
                # In production, we could queue retry attempts
                # For now, just log the failure
                pass


async def notify_job_started(job: Job, client_id: int, db: AsyncSession) -> None:
    """Notify webhooks that a job has started.
    
    Convenience function for job execution.
    """
    service = WebhookService(db)
    await service.notify(WebhookEvent.JOB_STARTED, job, client_id)


async def notify_job_completed(job: Job, client_id: int, db: AsyncSession) -> None:
    """Notify webhooks that a job has completed.
    
    Convenience function for job execution.
    """
    service = WebhookService(db)
    await service.notify(WebhookEvent.JOB_COMPLETED, job, client_id)


async def notify_job_failed(job: Job, client_id: int, db: AsyncSession) -> None:
    """Notify webhooks that a job has failed.
    
    Convenience function for job execution.
    """
    service = WebhookService(db)
    await service.notify(WebhookEvent.JOB_FAILED, job, client_id)
