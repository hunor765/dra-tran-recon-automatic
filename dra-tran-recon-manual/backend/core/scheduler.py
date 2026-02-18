"""Job scheduler for automated reconciliation.

Manages scheduled jobs using APScheduler with Redis-backed persistence.

In production, use Redis for job store persistence to survive restarts.
In development, in-memory storage is sufficient.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from core.config import settings

logger = logging.getLogger(__name__)

scheduler: Optional[AsyncIOScheduler] = None


def init_scheduler():
    """Initialize the job scheduler.
    
    Uses Redis for job store persistence in production if available.
    Falls back to in-memory storage for development.
    """
    global scheduler
    
    jobstores = {}
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }
    job_defaults = {
        "coalesce": True,  # Run once if multiple executions are missed
        "max_instances": 1,  # Only one instance of each job at a time
        "misfire_grace_time": 3600,  # 1 hour grace period
    }
    
    # Check for Redis configuration
    redis_url = getattr(settings, 'REDIS_URL', None)
    
    if redis_url:
        try:
            from apscheduler.jobstores.redis import RedisJobStore
            
            jobstores['default'] = RedisJobStore(
                jobs_key='apscheduler.jobs',
                run_times_key='apscheduler.run_times',
                host=redis_url,
                # Parse Redis URL if needed
                # For simple host:port format
            )
            
            logger.info("Scheduler initialized with Redis persistence")
        except ImportError:
            logger.warning(
                "RedisJobStore not available. "
                "Install with: pip install 'apscheduler[redis]'"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Redis job store: {e}")
    
    # If no Redis or Redis failed, use memory store
    if not jobstores:
        logger.info(
            "Scheduler initialized with in-memory storage. "
            "Schedules will be lost on restart. "
            "Set REDIS_URL for persistence."
        )
    
    scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone="UTC",
    )
    
    return scheduler


def get_scheduler() -> AsyncIOScheduler:
    """Get the scheduler instance."""
    global scheduler
    if scheduler is None:
        return init_scheduler()
    return scheduler


def shutdown_scheduler():
    """Shutdown the scheduler."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler shut down")


async def run_scheduled_reconciliation(schedule_id: int, client_id: int):
    """Execute a scheduled reconciliation job.
    
    This function is called by the scheduler when a job is triggered.
    
    Args:
        schedule_id: The schedule configuration ID
        client_id: The client ID to run the job for
    """
    logger.info(
        f"Running scheduled reconciliation for client {client_id} (schedule {schedule_id})"
    )
    
    async with AsyncSessionLocal() as db:
        try:
            # Get schedule configuration
            from models.schedule import Schedule
            result = await db.execute(
                select(Schedule).where(Schedule.id == schedule_id)
            )
            schedule = result.scalar_one_or_none()
            
            if not schedule or not schedule.is_active:
                logger.warning(f"Schedule {schedule_id} not found or inactive, skipping")
                return
            
            # Import job execution logic
            from api.v1.endpoints.jobs import execute_reconciliation
            from models.job import Job as JobModel, JobStatus
            
            # Create job record
            config = schedule.config or {}
            job = JobModel(
                client_id=client_id,
                status=JobStatus.RUNNING,
                days=config.get("days", 30),
                start_date=config.get("start_date"),
                end_date=config.get("end_date"),
                max_retries=config.get("max_retries", 3),
                config={"scheduled": True, "schedule_id": schedule_id}
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)
            
            logger.info(f"Created scheduled job {job.id} for client {client_id}")
            
            # Run the reconciliation (this will handle its own session)
            await execute_reconciliation(
                job_id=job.id,
                client_id=client_id,
                days=job.days,
                start_date=job.start_date,
                end_date=job.end_date
            )
            
        except Exception as e:
            logger.error(f"Error running scheduled job: {e}", exc_info=True)


def build_trigger(schedule) -> Optional[Any]:
    """Build an APScheduler trigger from a schedule configuration.
    
    Args:
        schedule: The Schedule model instance
        
    Returns:
        Trigger instance or None if invalid
    """
    frequency = schedule.frequency
    
    if frequency == "hourly":
        return IntervalTrigger(hours=1)
    
    elif frequency == "daily":
        if schedule.time_of_day:
            hour, minute = schedule.time_of_day.hour, schedule.time_of_day.minute
            return CronTrigger(
                hour=hour,
                minute=minute,
                timezone=schedule.timezone or "UTC"
            )
        else:
            return CronTrigger(hour=3, minute=0)  # Default to 3 AM
    
    elif frequency == "weekly":
        if schedule.time_of_day:
            hour, minute = schedule.time_of_day.hour, schedule.time_of_day.minute
            return CronTrigger(
                day_of_week="mon",
                hour=hour,
                minute=minute,
                timezone=schedule.timezone or "UTC"
            )
        else:
            return CronTrigger(day_of_week="mon", hour=3, minute=0)
    
    else:
        logger.error(f"Unknown frequency: {frequency}")
        return None


async def load_schedules_from_db():
    """Load active schedules from database and add to scheduler."""
    global scheduler
    
    if scheduler is None:
        logger.error("Scheduler not initialized")
        return
    
    async with AsyncSessionLocal() as db:
        from models.schedule import Schedule
        
        result = await db.execute(
            select(Schedule).where(Schedule.is_active == True)
        )
        schedules = result.scalars().all()
        
        logger.info(f"Loading {len(schedules)} schedules from database")
        
        for schedule in schedules:
            job_id = f"scheduled_job_{schedule.id}"
            
            # Remove existing job if present
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
            
            trigger = build_trigger(schedule)
            if trigger is None:
                continue
            
            scheduler.add_job(
                func=run_scheduled_reconciliation,
                trigger=trigger,
                id=job_id,
                args=[schedule.id, schedule.client_id],
                replace_existing=True,
                misfire_grace_time=3600  # 1 hour grace period
            )
            
            logger.info(
                f"Scheduled job for client {schedule.client_id}: "
                f"{schedule.frequency} at {schedule.time_of_day or 'default'}"
            )


async def add_schedule_to_scheduler(schedule):
    """Add a new schedule to the running scheduler.
    
    Args:
        schedule: The Schedule model instance
    """
    global scheduler
    
    if scheduler is None or not schedule.is_active:
        return
    
    job_id = f"scheduled_job_{schedule.id}"
    trigger = build_trigger(schedule)
    
    if trigger is None:
        return
    
    # Remove existing job if present
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    scheduler.add_job(
        func=run_scheduled_reconciliation,
        trigger=trigger,
        id=job_id,
        args=[schedule.id, schedule.client_id],
        replace_existing=True,
        misfire_grace_time=3600
    )
    
    logger.info(f"Added schedule {schedule.id} to scheduler")


def remove_schedule_from_scheduler(schedule_id: int):
    """Remove a schedule from the running scheduler.
    
    Args:
        schedule_id: The schedule ID to remove
    """
    global scheduler
    
    if scheduler is None:
        return
    
    job_id = f"scheduled_job_{schedule_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"Removed schedule {schedule_id} from scheduler")


async def start_scheduler():
    """Start the scheduler and load all schedules."""
    global scheduler
    
    if scheduler is None:
        init_scheduler()
    
    # Load schedules from database
    await load_schedules_from_db()
    
    # Schedule data retention cleanup
    from core.data_retention import schedule_cleanup_tasks
    schedule_cleanup_tasks()
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started")


async def reload_schedules():
    """Reload all schedules from database (useful after configuration changes)."""
    global scheduler
    
    if scheduler is None:
        return
    
    # Remove all scheduled jobs
    for job in scheduler.get_jobs():
        if job.id.startswith("scheduled_job_"):
            job.remove()
    
    # Reload from database
    await load_schedules_from_db()
    logger.info("Schedules reloaded")
