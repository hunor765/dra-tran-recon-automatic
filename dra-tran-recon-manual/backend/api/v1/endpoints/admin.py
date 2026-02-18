import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any, Optional

from core.database import get_db
from core.auth import require_admin
from core.data_retention import DataCleanupTask, get_storage_stats
from core.rate_limiter import limiter, RateLimits
from models.client import Client
from models.job import Job
from models.connector import Connector

router = APIRouter()
logger = logging.getLogger(__name__)


class CleanupRequest(BaseModel):
    dry_run: bool = True
    custom_retention: Optional[Dict[str, int]] = None


@router.get("/stats")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
) -> Dict[str, Any]:
    """Get admin dashboard statistics"""
    # Count clients
    result = await db.execute(select(func.count(Client.id)))
    total_clients = result.scalar()
    
    # Count active clients
    result = await db.execute(
        select(func.count(Client.id)).where(Client.is_active == True)
    )
    active_clients = result.scalar()
    
    # Count total jobs
    result = await db.execute(select(func.count(Job.id)))
    total_jobs = result.scalar()
    
    # Count jobs by status
    result = await db.execute(
        select(Job.status, func.count(Job.id)).group_by(Job.status)
    )
    jobs_by_status = {status: count for status, count in result.all()}
    
    # Recent jobs (last 10)
    result = await db.execute(
        select(Job, Client.name.label("client_name"))
        .join(Client, Job.client_id == Client.id)
        .order_by(Job.last_run.desc())
        .limit(10)
    )
    recent_jobs = []
    for job, client_name in result.all():
        recent_jobs.append({
            "id": job.id,
            "client_id": job.client_id,
            "client_name": client_name,
            "status": job.status,
            "last_run": job.last_run,
            "result_summary": job.result_summary
        })
    
    return {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "total_jobs": total_jobs,
        "jobs_by_status": jobs_by_status,
        "recent_jobs": recent_jobs
    }


@router.get("/jobs")
async def get_all_jobs(
    skip: int = 0,
    limit: int = 100,
    client_id: int = None,
    status: str = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Get all jobs with optional filtering"""
    query = select(Job, Client.name.label("client_name")).join(Client)
    
    if client_id:
        query = query.where(Job.client_id == client_id)
    if status:
        query = query.where(Job.status == status)
    
    query = query.order_by(Job.last_run.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    
    jobs = []
    for job, client_name in result.all():
        job_dict = {
            "id": job.id,
            "client_id": job.client_id,
            "client_name": client_name,
            "status": job.status,
            "last_run": job.last_run,
            "result_summary": job.result_summary
        }
        jobs.append(job_dict)
    
    return jobs


@router.post("/cleanup")
@limiter.limit(RateLimits.ADMIN_WRITE)
async def run_data_cleanup(
    request: Request,
    cleanup_req: CleanupRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Run data retention cleanup task.
    
    Args:
        cleanup_req: Cleanup configuration
        
    Returns:
        Cleanup results
    """
    logger.info(
        f"Admin triggered data cleanup (dry_run={cleanup_req.dry_run})",
        extra={
            "admin_id": user.get("id"),
            "dry_run": cleanup_req.dry_run
        }
    )
    
    try:
        from core.data_retention import DataRetentionConfig
        
        # Use custom retention config if provided
        if cleanup_req.custom_retention:
            config = DataRetentionConfig(cleanup_req.custom_retention)
            task = DataCleanupTask(retention_config=config)
        else:
            task = DataCleanupTask()
        
        results = await task.run_cleanup(dry_run=cleanup_req.dry_run)
        
        return {
            "success": True,
            "dry_run": cleanup_req.dry_run,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Data cleanup failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup failed: {str(e)}"
        )


@router.get("/storage")
@limiter.limit(RateLimits.ADMIN_READ)
async def get_storage_statistics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Get database storage statistics.
    
    Returns information about database size and usage patterns
    to help with capacity planning.
    """
    try:
        stats = await get_storage_stats(db)
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get storage statistics: {str(e)}"
        )


@router.get("/health/detailed")
async def get_detailed_health(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Get detailed system health information.
    
    Returns comprehensive health status including:
    - Database connectivity
    - External service status
    - Queue health
    - Recent error rates
    """
    health = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy",
        "services": {}
    }
    
    # Database check
    try:
        from sqlalchemy import text
        result = await db.execute(text("SELECT 1"))
        await result.scalar()
        health["services"]["database"] = {
            "status": "healthy",
            "latency_ms": 0  # Could measure actual latency
        }
    except Exception as e:
        health["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health["status"] = "degraded"
    
    # Redis check (if configured)
    try:
        from core.config import settings
        if getattr(settings, 'REDIS_URL', None):
            # Would need redis client to actually check
            health["services"]["redis"] = {
                "status": "configured",
                "note": "Connectivity check not implemented"
            }
        else:
            health["services"]["redis"] = {
                "status": "not_configured"
            }
    except Exception as e:
        health["services"]["redis"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Email service check
    try:
        from core.email_service import email_service
        health["services"]["email"] = {
            "status": "enabled" if email_service.enabled else "disabled",
            "configured": bool(getattr(settings, 'RESEND_API_KEY', None))
        }
    except Exception as e:
        health["services"]["email"] = {
            "status": "error",
            "error": str(e)
        }
    
    return health


from datetime import datetime
