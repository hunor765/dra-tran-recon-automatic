"""
DRA Platform - Dynamic Job Scheduler
Runs reconciliation jobs based on client schedules stored in database
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job as APJob
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import AsyncSessionLocal, engine
from models.client import Client
from models.schedule import Schedule
from models.job import Job, JobStatus
from api.v1.endpoints.jobs import execute_reconciliation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None


def get_cron_trigger_from_schedule(schedule: Schedule) -> CronTrigger:
    """Convert a Schedule model to an APScheduler CronTrigger"""
    try:
        import pytz
        tz = pytz.timezone(schedule.timezone)
    except (ImportError, pytz.UnknownTimeZoneError):
        logger.warning(f"Unknown timezone {schedule.timezone}, using Europe/Bucharest")
        tz = "Europe/Bucharest"
    
    if schedule.frequency == "hourly":
        return CronTrigger(minute=0, timezone=tz)
    elif schedule.frequency == "daily":
        hour = schedule.time_of_day.hour if schedule.time_of_day else 3
        minute = schedule.time_of_day.minute if schedule.time_of_day else 0
        return CronTrigger(hour=hour, minute=minute, timezone=tz)
    elif schedule.frequency == "weekly":
        hour = schedule.time_of_day.hour if schedule.time_of_day else 3
        minute = schedule.time_of_day.minute if schedule.time_of_day else 0
        return CronTrigger(day_of_week="mon", hour=hour, minute=minute, timezone=tz)
    else:
        # Default to daily at 3 AM
        return CronTrigger(hour=3, minute=0, timezone="Europe/Bucharest")


async def run_job_for_client(client_id: int, days: int = 30, start_date: str = None, end_date: str = None):
    """Run reconciliation job for a specific client"""
    async with AsyncSessionLocal() as db:
        logger.info(f"Running scheduled job for client {client_id}")
        
        try:
            # Create job record
            job = Job(
                client_id=client_id,
                status=JobStatus.RUNNING,
                days=days,
                start_date=start_date,
                end_date=end_date
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)
            
            logger.info(f"  Created job ID: {job.id}")
            
            # Run reconciliation in background
            asyncio.create_task(execute_reconciliation(job.id, client_id, days, start_date, end_date, 1))
            
            logger.info(f"  Job {job.id} started in background")
            
        except Exception as e:
            logger.error(f"  Error starting job for client {client_id}: {e}")
            await db.rollback()


async def load_schedules():
    """Load schedules from database and update scheduler jobs"""
    global scheduler
    
    if not scheduler:
        logger.error("Scheduler not initialized")
        return
    
    logger.info("Loading schedules from database...")
    
    async with AsyncSessionLocal() as db:
        # Get all active schedules
        result = await db.execute(
            select(Client, Schedule)
            .join(Schedule, Client.id == Schedule.client_id)
            .where(Client.is_active == True)
            .where(Schedule.is_active == True)
        )
        client_schedules = result.all()
        
        logger.info(f"Found {len(client_schedules)} active schedules")
        
        # Track current job IDs
        current_job_ids = set()
        
        for client, schedule in client_schedules:
            job_id = f"client_schedule_{client.id}"
            current_job_ids.add(job_id)
            
            # Get config
            days = schedule.config.get('days', 30) if schedule.config else 30
            start_date = schedule.config.get('start_date') if schedule.config else None
            end_date = schedule.config.get('end_date') if schedule.config else None
            
            # Check if job already exists
            existing_job = scheduler.get_job(job_id)
            
            if existing_job:
                # Update existing job if trigger changed
                trigger = get_cron_trigger_from_schedule(schedule)
                # Note: APScheduler doesn't allow easy trigger updates, so we remove and re-add
                scheduler.remove_job(job_id)
                logger.info(f"Updated schedule for client {client.id} ({schedule.frequency})")
            else:
                logger.info(f"Adding new schedule for client {client.id} ({schedule.frequency})")
            
            # Add job to scheduler
            trigger = get_cron_trigger_from_schedule(schedule)
            scheduler.add_job(
                run_job_for_client,
                trigger=trigger,
                id=job_id,
                name=f"Reconciliation for {client.name}",
                replace_existing=True,
                args=[client.id],
                kwargs={
                    'days': days,
                    'start_date': start_date,
                    'end_date': end_date
                }
            )
        
        # Remove jobs for schedules that no longer exist or are inactive
        for job in scheduler.get_jobs():
            if job.id.startswith('client_schedule_') and job.id not in current_job_ids:
                scheduler.remove_job(job.id)
                logger.info(f"Removed schedule {job.id}")
    
    logger.info("Schedule loading complete")


async def refresh_schedules_loop():
    """Background task to periodically refresh schedules from database"""
    while True:
        try:
            await load_schedules()
        except Exception as e:
            logger.error(f"Error loading schedules: {e}")
        
        # Refresh every 5 minutes
        await asyncio.sleep(300)


def start_scheduler():
    """Start the APScheduler with database-backed schedules"""
    global scheduler
    
    scheduler = AsyncIOScheduler()
    
    # Add a job to refresh schedules periodically
    scheduler.add_job(
        lambda: asyncio.create_task(load_schedules()),
        trigger='interval',
        minutes=5,
        id='schedule_refresh',
        name='Refresh schedules from database',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started - Dynamic schedules enabled")
    logger.info("Current time: " + str(datetime.now()))
    
    # Initial load of schedules
    asyncio.create_task(load_schedules())
    
    return scheduler


def shutdown_scheduler():
    """Shutdown the scheduler"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler stopped")


# Legacy function for backward compatibility
async def run_scheduled_jobs():
    """Run reconciliation jobs for all active clients with active schedules (legacy)"""
    logger.info("=" * 60)
    logger.info(f"Starting scheduled reconciliation jobs at {datetime.now()}")
    logger.info("=" * 60)
    
    async with AsyncSessionLocal() as db:
        # Get all active clients with active schedules
        result = await db.execute(
            select(Client, Schedule)
            .join(Schedule, Client.id == Schedule.client_id)
            .where(Client.is_active == True)
            .where(Schedule.is_active == True)
        )
        client_schedules = result.all()
        
        logger.info(f"Found {len(client_schedules)} active clients with schedules")
        
        for client, schedule in client_schedules:
            # Get days from schedule config or use default
            days = schedule.config.get('days', 30) if schedule.config else 30
            start_date = schedule.config.get('start_date') if schedule.config else None
            end_date = schedule.config.get('end_date') if schedule.config else None
            
            logger.info(f"Processing client: {client.name} (ID: {client.id}), schedule: {schedule.frequency}, days: {days}")
            
            try:
                # Create job record
                job = Job(
                    client_id=client.id, 
                    status=JobStatus.RUNNING,
                    days=days,
                    start_date=start_date,
                    end_date=end_date
                )
                db.add(job)
                await db.commit()
                await db.refresh(job)
                
                logger.info(f"  Created job ID: {job.id}")
                
                # Run reconciliation in background
                asyncio.create_task(execute_reconciliation(job.id, client.id, days, start_date, end_date, 1))
                
                logger.info(f"  Job {job.id} started in background")
                
            except Exception as e:
                logger.error(f"  Error starting job for client {client.id}: {e}")
                await db.rollback()
    
    logger.info("Scheduled job run completed")
    logger.info("=" * 60)


async def run_now():
    """Run jobs immediately (for testing)"""
    await run_scheduled_jobs()


if __name__ == "__main__":
    # Start the scheduler
    scheduler = start_scheduler()
    
    # Keep the script running
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        shutdown_scheduler()
        logger.info("Scheduler stopped")
