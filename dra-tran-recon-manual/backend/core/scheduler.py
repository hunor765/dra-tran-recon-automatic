from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

scheduler: Optional[AsyncIOScheduler] = None


def init_scheduler():
    """Initialize the job scheduler"""
    global scheduler
    scheduler = AsyncIOScheduler()
    return scheduler


def get_scheduler() -> AsyncIOScheduler:
    """Get the scheduler instance"""
    global scheduler
    if scheduler is None:
        return init_scheduler()
    return scheduler


def shutdown_scheduler():
    """Shutdown the scheduler"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
