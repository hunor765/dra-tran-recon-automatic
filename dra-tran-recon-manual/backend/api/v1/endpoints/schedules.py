from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, time, timedelta
import pytz

from core.database import get_db, AsyncSessionLocal
from core.auth import require_admin
from models.schedule import Schedule as ScheduleModel
from models.client import Client as ClientModel
from schemas.schedule import Schedule, ScheduleCreate, ScheduleUpdate
from schemas.job import JobConfig
from api.v1.endpoints.jobs import execute_reconciliation
from models.job import Job, JobStatus

router = APIRouter()


def compute_next_run(schedule: ScheduleModel) -> str:
    """Compute the next run time based on schedule configuration"""
    if not schedule.is_active:
        return "Schedule is inactive"
    
    try:
        tz = pytz.timezone(schedule.timezone)
    except pytz.UnknownTimeZoneError:
        tz = pytz.UTC
    
    now = datetime.now(tz)
    
    if schedule.frequency == "daily":
        # Get scheduled time
        scheduled_time = schedule.time_of_day or time(3, 0, 0)  # Default 3:00 AM
        next_run = now.replace(hour=scheduled_time.hour, minute=scheduled_time.minute, 
                               second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        return next_run.strftime("%Y-%m-%d at %H:%M %Z")
    
    elif schedule.frequency == "hourly":
        next_run = now + timedelta(hours=1)
        next_run = next_run.replace(minute=0, second=0, microsecond=0)
        return next_run.strftime("%Y-%m-%d at %H:%M %Z")
    
    elif schedule.frequency == "weekly":
        scheduled_time = schedule.time_of_day or time(3, 0, 0)
        next_run = now.replace(hour=scheduled_time.hour, minute=scheduled_time.minute,
                               second=0, microsecond=0)
        days_until_next = 7 - now.weekday() if now.weekday() != 0 else 0
        if days_until_next == 0 and next_run <= now:
            days_until_next = 7
        next_run += timedelta(days=days_until_next)
        return next_run.strftime("%Y-%m-%d at %H:%M %Z")
    
    return "Unknown frequency"


@router.post("/trigger/{client_id}")
async def trigger_job_now(
    client_id: int,
    background_tasks: BackgroundTasks,
    config: Optional[JobConfig] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """
    Manually trigger a reconciliation job for a client (admin only).
    This is an alias to /jobs/run/{client_id} for backward compatibility.
    
    Args:
        client_id: The client ID to run the job for
        config: Optional job configuration (days, date range, etc.)
    """
    # Verify client exists
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Determine parameters
    days = config.days if config else 30
    start_date = config.start_date if config else None
    end_date = config.end_date if config else None
    max_retries = config.max_retries if config else 3
    
    # Create job record
    job = Job(
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
    
    # Run in background task
    background_tasks.add_task(execute_reconciliation, job.id, client_id, days, start_date, end_date, 1)
    
    return {
        "message": "Job triggered successfully",
        "job_id": job.id,
        "client_id": client_id,
        "status": "running",
        "days": days,
        "start_date": start_date,
        "end_date": end_date
    }


@router.get("/clients/{client_id}/schedule", response_model=Schedule)
async def get_client_schedule(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Get schedule for a client"""
    # Verify client exists
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get schedule from database
    result = await db.execute(select(ScheduleModel).where(ScheduleModel.client_id == client_id))
    schedule = result.scalars().first()
    
    from schemas.schedule import ScheduleConfig
    
    if not schedule:
        # Return default schedule (not stored yet)
        return Schedule(
            id=0,  # Placeholder
            client_id=client_id,
            frequency="daily",
            time_of_day=time(3, 0, 0),
            timezone="Europe/Bucharest",
            is_active=True,
            config=ScheduleConfig(days=30),
            next_run="Not scheduled - create a schedule first"
        )
    
    # Parse config from database
    config = ScheduleConfig(**schedule.config) if schedule.config else ScheduleConfig(days=30, max_retries=3)
    
    # Build response with computed next_run
    schedule_data = Schedule(
        id=schedule.id,
        client_id=schedule.client_id,
        frequency=schedule.frequency,
        time_of_day=schedule.time_of_day,
        timezone=schedule.timezone,
        is_active=schedule.is_active,
        config=config,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at,
        next_run=compute_next_run(schedule)
    )
    
    return schedule_data


@router.post("/clients/{client_id}/schedule", response_model=Schedule)
async def create_or_update_schedule(
    client_id: int,
    schedule_data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Create or update schedule for a client"""
    # Verify client exists
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if schedule exists
    result = await db.execute(select(ScheduleModel).where(ScheduleModel.client_id == client_id))
    schedule = result.scalars().first()
    
    config_dict = schedule_data.config.dict() if schedule_data.config else {"days": 30, "max_retries": 3}
    
    if schedule:
        # Update existing
        schedule.frequency = schedule_data.frequency
        schedule.time_of_day = schedule_data.time_of_day
        schedule.timezone = schedule_data.timezone
        schedule.is_active = schedule_data.is_active
        schedule.config = config_dict
    else:
        # Create new
        schedule = ScheduleModel(
            client_id=client_id,
            frequency=schedule_data.frequency,
            time_of_day=schedule_data.time_of_day,
            timezone=schedule_data.timezone,
            is_active=schedule_data.is_active,
            config=config_dict
        )
        db.add(schedule)
    
    await db.commit()
    await db.refresh(schedule)
    
    from schemas.schedule import ScheduleConfig
    config = ScheduleConfig(**schedule.config) if schedule.config else ScheduleConfig(days=30, max_retries=3)
    
    # Build response
    return Schedule(
        id=schedule.id,
        client_id=schedule.client_id,
        frequency=schedule.frequency,
        time_of_day=schedule.time_of_day,
        timezone=schedule.timezone,
        is_active=schedule.is_active,
        config=config,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at,
        next_run=compute_next_run(schedule)
    )


@router.put("/clients/{client_id}/schedule", response_model=Schedule)
async def update_schedule(
    client_id: int,
    schedule_data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Update schedule for a client"""
    # Verify client exists
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get existing schedule
    result = await db.execute(select(ScheduleModel).where(ScheduleModel.client_id == client_id))
    schedule = result.scalars().first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found for this client")
    
    # Update fields
    if schedule_data.frequency is not None:
        schedule.frequency = schedule_data.frequency
    if schedule_data.time_of_day is not None:
        schedule.time_of_day = schedule_data.time_of_day
    if schedule_data.timezone is not None:
        schedule.timezone = schedule_data.timezone
    if schedule_data.is_active is not None:
        schedule.is_active = schedule_data.is_active
    if schedule_data.config is not None:
        schedule.config = schedule_data.config.dict()
    
    await db.commit()
    await db.refresh(schedule)
    
    from schemas.schedule import ScheduleConfig
    config = ScheduleConfig(**schedule.config) if schedule.config else ScheduleConfig(days=30, max_retries=3)
    
    # Build response
    return Schedule(
        id=schedule.id,
        client_id=schedule.client_id,
        frequency=schedule.frequency,
        time_of_day=schedule.time_of_day,
        timezone=schedule.timezone,
        is_active=schedule.is_active,
        config=config,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at,
        next_run=compute_next_run(schedule)
    )


@router.delete("/clients/{client_id}/schedule")
async def delete_schedule(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Delete schedule for a client"""
    # Verify client exists
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get and delete schedule
    result = await db.execute(select(ScheduleModel).where(ScheduleModel.client_id == client_id))
    schedule = result.scalars().first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found for this client")
    
    await db.delete(schedule)
    await db.commit()
    
    return {"message": "Schedule deleted successfully"}
