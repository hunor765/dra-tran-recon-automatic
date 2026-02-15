from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from core.database import get_db, AsyncSessionLocal
from core.auth import get_current_user, require_admin
from core.encryption import decrypt_config
from models.job import Job as JobModel, JobStatus
from models.connector import Connector as ConnectorModel
from models.client import Client as ClientModel
from schemas.job import Job, JobCreate, JobConfig, JobRetryRequest
import json
import pandas as pd
from typing import List, Optional
import asyncio

router = APIRouter()


@router.get("/", response_model=List[Job])
async def list_jobs(
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """List jobs with optional filtering"""
    query = select(JobModel, ClientModel.name.label("client_name")).join(ClientModel, JobModel.client_id == ClientModel.id)
    
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
        
    return jobs


async def execute_reconciliation(
    job_id: int, 
    client_id: int, 
    days: int = 30,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    attempt: int = 1
):
    """
    Execute reconciliation job with optional retry logic.
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
    from core.ingestors.woocommerce import WooCommerceIngestor
    from core.ingestors.shopify import ShopifyIngestor
    
    # Create a new session for this background task
    async with AsyncSessionLocal() as db:
        date_range_str = f"{start_date} to {end_date}" if start_date else f"last {days} days"
        print(f"--- STARTING JOB {job_id} for Client {client_id} ({date_range_str}) [attempt {attempt}] ---")
        
        try:
            # 1. Fetch Connectors
            result = await db.execute(select(ConnectorModel).where(ConnectorModel.client_id == client_id))
            connectors = result.scalars().all()
            
            ga4_ingestor = None
            backend_ingestor = None
            
            for conn in connectors:
                # Decrypt the config first
                config_str = decrypt_config(conn.config_json)
                config = json.loads(config_str)
                if conn.type == 'ga4':
                    ga4_ingestor = GA4Ingestor(config)
                elif conn.type == 'woocommerce':
                    backend_ingestor = WooCommerceIngestor(config)
                elif conn.type == 'shopify':
                    backend_ingestor = ShopifyIngestor(config)
            
            if not ga4_ingestor or not backend_ingestor:
                 print("❌ Job Failed: Missing connectors")
                 job = await db.get(JobModel, job_id)
                 job.status = JobStatus.FAILED
                 job.logs = "Missing GA4 or Backend connector"
                 await db.commit()
                 return

            # 2. Fetch Data with date range support
            df_ga4 = await ga4_ingestor.fetch_data(days=days, start_date=start_date, end_date=end_date)
            df_backend = await backend_ingestor.fetch_data(days=days, start_date=start_date, end_date=end_date)
            
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
            
            print(f"✅ Job {job_id} Completed. Match Rate: {match_rate}%")

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Job Failed: {error_msg}")
            
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
                print(f"⏳ Retrying job {job_id} in {backoff_seconds} seconds... (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(backoff_seconds)
                
                # Retry
                await execute_reconciliation(job_id, client_id, days, start_date, end_date, attempt + 1)
            else:
                job.status = JobStatus.FAILED
                job.logs = f"Failed after {attempt} attempts. Last error: {error_msg}"
                await db.commit()
                print(f"❌ Job {job_id} failed after {attempt} attempts")


@router.post("/run/{client_id}", response_model=Job)
async def run_job(
    client_id: int,
    background_tasks: BackgroundTasks,
    config: Optional[JobConfig] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """
    Trigger a reconciliation job for a client.
    Runs asynchronously in the background.
    
    Args:
        client_id: The client ID to run the job for
        config: Optional job configuration (days, date range, max_retries, etc.)
    """
    # 1. Check client exists
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalars().first()
    if not client:
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

    # 4. Run in background task (non-blocking)
    background_tasks.add_task(execute_reconciliation, job.id, client_id, days, start_date, end_date, 1)
    
    return job


@router.post("/{job_id}/retry", response_model=Job)
async def retry_job(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """
    Manually retry a failed job.
    """
    # Get the job
    job = await db.get(JobModel, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.FAILED:
        raise HTTPException(status_code=400, detail=f"Cannot retry job with status: {job.status}")
    
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
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get detailed job information"""
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
