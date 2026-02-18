"""Job execution and management endpoints.

Provides API endpoints for running, monitoring, and retrying reconciliation jobs.
"""
import asyncio
import json
import logging
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from core.auth import get_current_user, require_admin
from core.database import get_db, AsyncSessionLocal
from core.encryption import decrypt_config
from core.email_service import email_service
from core.ingestors.base import IngestorError, ConfigurationError, APIError, DataValidationError
from core.monitoring import capture_exception, PerformanceMonitor
from core.rate_limiter import limiter, RateLimits
from core.webhooks import notify_job_started, notify_job_completed, notify_job_failed
from models.client import Client as ClientModel
from models.connector import Connector as ConnectorModel
from models.job import Job as JobModel, JobStatus
from schemas.job import Job, JobConfig

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[Job])
@limiter.limit(RateLimits.LIST)
async def list_jobs(
    request: Request,
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """List jobs with optional filtering."""
    query = select(JobModel, ClientModel.name.label("client_name")).join(
        ClientModel, JobModel.client_id == ClientModel.id
    )
    
    if client_id:
        query = query.where(JobModel.client_id == client_id)
    
    if status:
        query = query.where(JobModel.status == status)
    
    query = query.order_by(JobModel.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    
    jobs = []
    for job, client_name in result.all():
        job_dict = {
            "id": job.id,
            "client_id": job.client_id,
            "client_name": client_name,
            "status": job.status,
            "last_run": job.last_run,
            "created_at": job.created_at,
            "result_summary": job.result_summary,
            "days": job.days,
            "start_date": job.start_date,
            "end_date": job.end_date,
            "config": job.config,
            "logs": job.logs,
            "completed_at": job.completed_at,
            "retry_count": job.retry_count,
            "max_retries": job.max_retries
        }
        jobs.append(job_dict)
    
    logger.debug(f"Listed {len(jobs)} jobs", extra={"filters": {"client_id": client_id, "status": status}})
    return jobs


async def execute_reconciliation(
    job_id: int,
    client_id: int,
    days: int = 30,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    attempt: int = 1
):
    """Execute reconciliation job with optional retry logic.
    
    This function creates its own database session to safely run in background tasks.
    
    Args:
        job_id: The job ID
        client_id: The client ID
        days: Number of days to fetch data for (default: 30)
        start_date: Explicit start date in YYYY-MM-DD format
        end_date: Explicit end date in YYYY-MM-DD format
        attempt: Current retry attempt number
    """
    # Import ingestors inside function to avoid circular imports
    from core.ingestors.google_analytics import GA4Ingestor
    from core.ingestors.shopify import ShopifyIngestor
    from core.ingestors.woocommerce import WooCommerceIngestor
    
    # Create a new session for this background task
    async with AsyncSessionLocal() as db:
        date_range_str = f"{start_date} to {end_date}" if start_date else f"last {days} days"
        log_ctx = {
            "job_id": job_id,
            "client_id": client_id,
            "date_range": date_range_str,
            "attempt": attempt,
        }
        
        logger.info(
            f"Starting reconciliation job {job_id} for client {client_id}",
            extra={**log_ctx, "event": "job.start"}
        )
        
        # Notify webhooks that job has started
        job = await db.get(JobModel, job_id)
        if job:
            await notify_job_started(job, client_id, db)
        
        try:
            # 1. Fetch Connectors
            result = await db.execute(
                select(ConnectorModel).where(ConnectorModel.client_id == client_id)
            )
            connectors = result.scalars().all()
            
            ga4_ingestor = None
            backend_ingestor = None
            
            for conn in connectors:
                # Decrypt the config first
                config_str = decrypt_config(conn.config_json)
                config = json.loads(config_str)
                if conn.type == 'ga4':
                    ga4_ingestor = GA4Ingestor(config)
                    logger.debug(f"Initialized GA4 ingestor for job {job_id}")
                elif conn.type == 'woocommerce':
                    backend_ingestor = WooCommerceIngestor(config)
                    logger.debug(f"Initialized WooCommerce ingestor for job {job_id}")
                elif conn.type == 'shopify':
                    backend_ingestor = ShopifyIngestor(config)
                    logger.debug(f"Initialized Shopify ingestor for job {job_id}")
            
            if not ga4_ingestor or not backend_ingestor:
                missing = []
                if not ga4_ingestor:
                    missing.append("GA4")
                if not backend_ingestor:
                    missing.append("Backend (Shopify/WooCommerce)")
                error_msg = f"Missing connectors: {', '.join(missing)}"
                
                logger.error(error_msg, extra={**log_ctx, "event": "job.failed"})
                
                job = await db.get(JobModel, job_id)
                job.status = JobStatus.FAILED
                job.logs = error_msg
                await db.commit()
                return
            
            # 2. Fetch Data with date range support
            logger.info(f"Fetching data for job {job_id}", extra={**log_ctx, "event": "job.fetch_data"})
            
            df_ga4 = await ga4_ingestor.fetch_data(
                days=days, start_date=start_date, end_date=end_date
            )
            df_backend = await backend_ingestor.fetch_data(
                days=days, start_date=start_date, end_date=end_date
            )
            
            logger.info(
                f"Data fetch complete for job {job_id}",
                extra={
                    **log_ctx,
                    "event": "job.data_fetched",
                    "ga4_records": len(df_ga4),
                    "backend_records": len(df_backend),
                }
            )
            
            # 3. Reconcile
            common = set(df_ga4['clean_id']) & set(df_backend['clean_id'])
            missing_ids = set(df_backend['clean_id']) - set(df_ga4['clean_id'])
            
            match_rate = len(common) / len(df_backend) * 100 if len(df_backend) > 0 else 0
            total_backend_val = df_backend['value'].sum() if not df_backend.empty else 0
            total_ga4_val = df_ga4['value'].sum() if not df_ga4.empty else 0
            
            # 4. Save Results
            summary = {
                "match_rate": round(match_rate, 2),
                "total_backend_value": float(total_backend_val),
                "total_ga4_value": float(total_ga4_val),
                "missing_count": len(missing_ids),
                "missing_ids": list(missing_ids),
                "days_analyzed": days,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "ga4_records": len(df_ga4),
                "backend_records": len(df_backend),
                "retry_attempt": attempt
            }
            
            job = await db.get(JobModel, job_id)
            job.status = JobStatus.COMPLETED
            job.result_summary = summary
            job.completed_at = func.now()
            await db.commit()
            
            # Notify webhooks
            await notify_job_completed(job, client_id, db)
            
            # Send email notification if configured
            await _send_job_notification(db, client_id, job, summary, success=True)
            
            logger.info(
                f"Job {job_id} completed successfully",
                extra={
                    **log_ctx,
                    "event": "job.completed",
                    "match_rate": match_rate,
                    "missing_count": len(missing_ids),
                }
            )
        
        except (ConfigurationError, DataValidationError) as e:
            # Non-retryable errors (configuration issues)
            error_msg = f"{e.__class__.__name__}: {e.message}"
            logger.error(
                f"Job {job_id} failed with configuration error: {error_msg}",
                extra={**log_ctx, "event": "job.error", "error_type": "configuration"}
            )
            
            job = await db.get(JobModel, job_id)
            job.status = JobStatus.FAILED
            job.logs = error_msg
            await db.commit()
            
            # Notify webhooks
            await notify_job_failed(job, client_id, db)
            
            # Send email notification
            await _send_job_notification(db, client_id, job, None, success=False, error_msg=error_msg)
            
            # Capture in Sentry
            capture_exception(e, extra={"job_id": job_id, "client_id": client_id})
            
        except APIError as e:
            # API errors - may be retryable depending on status code
            error_msg = f"{e.source} API Error: {e.message}"
            logger.error(
                f"Job {job_id} failed with API error: {error_msg}",
                extra={
                    **log_ctx,
                    "event": "job.error",
                    "error_type": "api",
                    "source": e.source,
                    "status_code": e.status_code
                }
            )
            
            job = await db.get(JobModel, job_id)
            job.retry_count = attempt
            
            # Don't retry client errors (4xx) except 429 (rate limit)
            is_retryable = e.status_code is None or e.status_code >= 500 or e.status_code == 429
            
            if is_retryable and attempt < job.max_retries:
                job.status = JobStatus.RETRYING
                job.logs = f"Attempt {attempt} failed (retryable): {error_msg}"
                await db.commit()
                
                # Exponential backoff
                backoff_seconds = 2 ** attempt
                logger.warning(
                    f"Retrying job {job_id} in {backoff_seconds}s (attempt {attempt + 1}/{job.max_retries})",
                    extra={**log_ctx, "event": "job.retrying", "backoff_seconds": backoff_seconds}
                )
                await asyncio.sleep(backoff_seconds)
                
                # Retry
                await execute_reconciliation(
                    job_id, client_id, days, start_date, end_date, attempt + 1
                )
            else:
                job.status = JobStatus.FAILED
                job.logs = f"Failed after {attempt} attempts. Last error: {error_msg}"
                await db.commit()
                logger.error(
                    f"Job {job_id} failed after {attempt} attempts",
                    extra={**log_ctx, "event": "job.failed_final"}
                )
                
                # Notify webhooks
                await notify_job_failed(job, client_id, db)
                
                # Send email notification
                await _send_job_notification(db, client_id, job, None, success=False, error_msg=error_msg)
                
                # Capture in Sentry
                capture_exception(e, extra={"job_id": job_id, "client_id": client_id})
            
        except Exception as e:
            # Unknown errors - retry with caution
            error_msg = str(e)
            logger.error(
                f"Job {job_id} failed with unexpected error: {error_msg}",
                extra={**log_ctx, "event": "job.error", "error_type": "unexpected"},
                exc_info=True
            )
            
            job = await db.get(JobModel, job_id)
            job.retry_count = attempt
            job.logs = f"Attempt {attempt} failed: {error_msg}"
            
            # Check if we should retry
            max_retries = job.max_retries
            if attempt < max_retries:
                job.status = JobStatus.RETRYING
                await db.commit()
                
                # Exponential backoff: wait 2^attempt seconds before retry
                backoff_seconds = 2 ** attempt
                logger.warning(
                    f"Retrying job {job_id} in {backoff_seconds}s (attempt {attempt + 1}/{max_retries})",
                    extra={**log_ctx, "event": "job.retrying", "backoff_seconds": backoff_seconds}
                )
                await asyncio.sleep(backoff_seconds)
                
                # Retry
                await execute_reconciliation(
                    job_id, client_id, days, start_date, end_date, attempt + 1
                )
            else:
                job.status = JobStatus.FAILED
                job.logs = f"Failed after {attempt} attempts. Last error: {error_msg}"
                await db.commit()
                logger.error(
                    f"Job {job_id} failed after {attempt} attempts",
                    extra={**log_ctx, "event": "job.failed_final"}
                )
                
                # Notify webhooks
                await notify_job_failed(job, client_id, db)
                
                # Send email notification
                await _send_job_notification(db, client_id, job, None, success=False, error_msg=error_msg)
                
                # Capture in Sentry
                capture_exception(e, extra={"job_id": job_id, "client_id": client_id})


async def _send_job_notification(
    db: AsyncSession,
    client_id: int,
    job: JobModel,
    summary: Optional[dict],
    success: bool,
    error_msg: Optional[str] = None
) -> None:
    """Send job completion/failure notification emails.
    
    Args:
        db: Database session
        client_id: Client ID
        job: The job that completed/failed
        summary: Job result summary (for success)
        success: Whether the job succeeded
        error_msg: Error message (for failure)
    """
    try:
        from core.config import settings
        from models.user_client import UserClient
        from models.client import Client
        
        # Get client info
        client_result = await db.execute(
            select(Client).where(Client.id == client_id)
        )
        client = client_result.scalar_one_or_none()
        
        if not client:
            return
        
        # Get users who should be notified
        users_result = await db.execute(
            select(UserClient)
            .where(UserClient.client_id == client_id)
            .where(UserClient.status == "active")
        )
        users = users_result.scalars().all()
        
        if not users:
            return
        
        # Get frontend URL
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        dashboard_url = f"{frontend_url}/dashboard/results/{job.id}"
        
        # Send notifications
        for user in users:
            if not user.email:
                continue
                
            try:
                if success and summary:
                    await email_service.send_job_completion_notification(
                        email=user.email,
                        client_name=client.name,
                        job_id=job.id,
                        match_rate=summary.get("match_rate", 0),
                        missing_count=summary.get("missing_count", 0),
                        dashboard_url=dashboard_url
                    )
                elif not success:
                    await email_service.send_job_failure_notification(
                        email=user.email,
                        client_name=client.name,
                        job_id=job.id,
                        error_msg=error_msg or "Unknown error",
                        dashboard_url=dashboard_url
                    )
            except Exception as e:
                logger.error(f"Failed to send notification to {user.email}: {e}")
                
    except Exception as e:
        logger.error(f"Failed to send job notifications: {e}")


@router.post("/run/{client_id}", response_model=Job)
@limiter.limit(RateLimits.JOB_RUN)
async def run_job(
    request: Request,
    client_id: int,
    background_tasks: BackgroundTasks,
    config: Optional[JobConfig] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Trigger a reconciliation job for a client.
    
    Runs asynchronously in the background.
    
    Args:
        client_id: The client ID to run the job for
        config: Optional job configuration (days, date range, max_retries, etc.)
    """
    # 1. Check client exists
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalars().first()
    if not client:
        logger.warning(f"Job run failed: Client {client_id} not found")
        raise HTTPException(status_code=404, detail="Client not found")
    
    # 2. Determine parameters
    days = config.days if config else 30
    start_date = config.start_date if config else None
    end_date = config.end_date if config else None
    max_retries = config.max_retries if config else 3
    
    # 3. Create Job Record
    job = JobModel(
        client_id=client_id,
        status=JobStatus.RUNNING,
        days=days,
        start_date=start_date,
        end_date=end_date,
        config=config.dict() if config else None,
        max_retries=max_retries
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    logger.info(
        f"Created job {job.id} for client {client_id}",
        extra={
            "job_id": job.id,
            "client_id": client_id,
            "user_id": user.get("id"),
            "event": "job.created",
        }
    )
    
    # 4. Run in background task (non-blocking)
    background_tasks.add_task(
        execute_reconciliation, job.id, client_id, days, start_date, end_date, 1
    )
    
    return job


@router.post("/{job_id}/retry", response_model=Job)
@limiter.limit(RateLimits.JOB_RUN)
async def retry_job(
    request: Request,
    job_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Manually retry a failed job."""
    # Get the job
    job = await db.get(JobModel, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.FAILED:
        raise HTTPException(
            status_code=400, detail=f"Cannot retry job with status: {job.status}"
        )
    
    if not job.can_retry:
        raise HTTPException(
            status_code=400,
            detail=f"Job has exceeded max retries ({job.retry_count}/{job.max_retries})"
        )
    
    # Reset status and increment retry count
    job.status = JobStatus.RUNNING
    job.retry_count += 1
    await db.commit()
    await db.refresh(job)
    
    logger.info(
        f"Retrying job {job_id} (manual)",
        extra={
            "job_id": job_id,
            "client_id": job.client_id,
            "user_id": user.get("id"),
            "attempt": job.retry_count,
            "event": "job.retry_manual",
        }
    )
    
    # Run in background
    background_tasks.add_task(
        execute_reconciliation,
        job.id,
        job.client_id,
        job.days,
        job.start_date,
        job.end_date,
        job.retry_count
    )
    
    return job


@router.get("/{job_id}")
@limiter.limit(RateLimits.GET)
async def get_job(
    request: Request,
    job_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get detailed job information."""
    result = await db.execute(
        select(JobModel, ClientModel.name.label("client_name"))
        .join(ClientModel, JobModel.client_id == ClientModel.id)
        .where(JobModel.id == job_id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job, client_name = row
    return {
        "id": job.id,
        "client_id": job.client_id,
        "client_name": client_name,
        "status": job.status,
        "last_run": job.last_run,
        "result_summary": job.result_summary,
        "logs": getattr(job, 'logs', None),
        "days": job.days,
        "start_date": job.start_date,
        "end_date": job.end_date,
        "config": job.config,
        "completed_at": job.completed_at,
        "started_at": job.started_at,
        "retry_count": job.retry_count,
        "max_retries": job.max_retries,
        "can_retry": job.can_retry
    }
