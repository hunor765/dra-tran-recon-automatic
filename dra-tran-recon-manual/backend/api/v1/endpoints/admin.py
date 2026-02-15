from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any

from core.database import get_db
from core.auth import require_admin
from models.client import Client
from models.job import Job
from models.connector import Connector

router = APIRouter()


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
