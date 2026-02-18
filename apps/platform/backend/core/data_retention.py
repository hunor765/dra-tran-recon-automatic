"""Data retention and cleanup utilities.

Manages automatic cleanup of old data to prevent database bloat
and ensure compliance with data retention policies.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from core.scheduler import get_scheduler

logger = logging.getLogger(__name__)


class DataRetentionConfig:
    """Configuration for data retention policies."""
    
    # Default retention periods (in days)
    DEFAULTS = {
        "job_results": 90,          # Keep job results for 90 days
        "job_logs": 30,             # Keep detailed logs for 30 days
        "failed_jobs": 180,         # Keep failed jobs longer for debugging
        "audit_logs": 365,          # Keep audit logs for 1 year
        "old_jobs": 365,            # Delete old job records after 1 year
    }
    
    def __init__(self, config: Optional[Dict[str, int]] = None):
        """Initialize with custom config or defaults.
        
        Args:
            config: Optional dict with custom retention periods
        """
        self.config = {**self.DEFAULTS, **(config or {})}
    
    def get_retention_days(self, data_type: str) -> int:
        """Get retention period for a data type.
        
        Args:
            data_type: Type of data (job_results, audit_logs, etc.)
            
        Returns:
            Number of days to retain
        """
        return self.config.get(data_type, self.DEFAULTS.get(data_type, 90))


class DataCleanupTask:
    """Background task for cleaning up old data."""
    
    def __init__(self, retention_config: Optional[DataRetentionConfig] = None):
        self.config = retention_config or DataRetentionConfig()
        self.logger = logging.getLogger(__name__)
    
    async def run_cleanup(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run all cleanup tasks.
        
        Args:
            dry_run: If True, only count what would be deleted without actually deleting
            
        Returns:
            Dict with cleanup statistics
        """
        results = {
            "dry_run": dry_run,
            "started_at": datetime.utcnow().isoformat(),
            "tasks": {}
        }
        
        async with AsyncSessionLocal() as db:
            # Clean up old job results (remove detailed data)
            results["tasks"]["job_results"] = await self._cleanup_job_results(db, dry_run)
            
            # Clean up old job logs
            results["tasks"]["job_logs"] = await self._cleanup_job_logs(db, dry_run)
            
            # Clean up old completed jobs entirely
            results["tasks"]["old_jobs"] = await self._cleanup_old_jobs(db, dry_run)
            
            # Clean up old audit logs
            results["tasks"]["audit_logs"] = await self._cleanup_audit_logs(db, dry_run)
            
            if not dry_run:
                await db.commit()
        
        results["completed_at"] = datetime.utcnow().isoformat()
        
        # Log summary
        total_deleted = sum(
            task.get("deleted", 0) for task in results["tasks"].values()
        )
        self.logger.info(
            f"Data cleanup completed{' (dry run)' if dry_run else ''}: "
            f"{total_deleted} records affected",
            extra={
                "dry_run": dry_run,
                "total_deleted": total_deleted,
                "tasks": results["tasks"]
            }
        )
        
        return results
    
    async def _cleanup_job_results(self, db: AsyncSession, dry_run: bool) -> Dict[str, Any]:
        """Clean up detailed job results while keeping summary.
        
        For old completed jobs, we remove the detailed missing_ids list
        but keep the summary statistics.
        
        Args:
            db: Database session
            dry_run: If True, only count
            
        Returns:
            Cleanup statistics
        """
        from models.job import Job as JobModel, JobStatus
        
        retention_days = self.config.get_retention_days("job_results")
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Find old completed jobs with detailed results
        result = await db.execute(
            select(JobModel).where(
                JobModel.status == JobStatus.COMPLETED,
                JobModel.completed_at < cutoff_date,
                JobModel.result_summary.isnot(None)
            )
        )
        jobs = result.scalars().all()
        
        count = 0
        for job in jobs:
            if job.result_summary and "missing_ids" in job.result_summary:
                if not dry_run:
                    # Keep summary but remove detailed list
                    summary = dict(job.result_summary)
                    summary["missing_ids"] = f"[{len(summary.get('missing_ids', []))} items archived]"
                    summary["archived"] = True
                    summary["archived_at"] = datetime.utcnow().isoformat()
                    job.result_summary = summary
                count += 1
        
        return {
            "retention_days": retention_days,
            "cutoff_date": cutoff_date.isoformat(),
            "affected": count
        }
    
    async def _cleanup_job_logs(self, db: AsyncSession, dry_run: bool) -> Dict[str, Any]:
        """Clean up old job logs.
        
        Args:
            db: Database session
            dry_run: If True, only count
            
        Returns:
            Cleanup statistics
        """
        from models.job import Job as JobModel
        
        retention_days = self.config.get_retention_days("job_logs")
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Find jobs with logs older than retention period
        result = await db.execute(
            select(JobModel).where(
                JobModel.created_at < cutoff_date,
                JobModel.logs.isnot(None)
            )
        )
        jobs = result.scalars().all()
        
        count = 0
        for job in jobs:
            if job.logs:
                if not dry_run:
                    job.logs = f"[Log archived after {retention_days} days]"
                count += 1
        
        return {
            "retention_days": retention_days,
            "cutoff_date": cutoff_date.isoformat(),
            "affected": count
        }
    
    async def _cleanup_old_jobs(self, db: AsyncSession, dry_run: bool) -> Dict[str, Any]:
        """Delete very old job records entirely.
        
        Args:
            db: Database session
            dry_run: If True, only count
            
        Returns:
            Cleanup statistics
        """
        from models.job import Job as JobModel, JobStatus
        
        retention_days = self.config.get_retention_days("old_jobs")
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Count old completed jobs
        count_result = await db.execute(
            select(func.count()).select_from(JobModel).where(
                JobModel.status == JobStatus.COMPLETED,
                JobModel.completed_at < cutoff_date
            )
        )
        count = count_result.scalar()
        
        # Keep failed jobs longer for debugging
        failed_retention = self.config.get_retention_days("failed_jobs")
        failed_cutoff = datetime.utcnow() - timedelta(days=failed_retention)
        
        failed_count_result = await db.execute(
            select(func.count()).select_from(JobModel).where(
                JobModel.status == JobStatus.FAILED,
                JobModel.created_at < failed_cutoff
            )
        )
        failed_count = failed_count_result.scalar()
        
        total = count + failed_count
        
        if not dry_run and total > 0:
            # Delete old completed jobs
            if count > 0:
                await db.execute(
                    delete(JobModel).where(
                        JobModel.status == JobStatus.COMPLETED,
                        JobModel.completed_at < cutoff_date
                    )
                )
            
            # Delete very old failed jobs
            if failed_count > 0:
                await db.execute(
                    delete(JobModel).where(
                        JobModel.status == JobStatus.FAILED,
                        JobModel.created_at < failed_cutoff
                    )
                )
        
        return {
            "retention_days": retention_days,
            "failed_retention_days": failed_retention,
            "cutoff_date": cutoff_date.isoformat(),
            "deleted": count,
            "failed_deleted": failed_count,
            "total_deleted": total
        }
    
    async def _cleanup_audit_logs(self, db: AsyncSession, dry_run: bool) -> Dict[str, Any]:
        """Clean up old audit logs.
        
        Args:
            db: Database session
            dry_run: If True, only count
            
        Returns:
            Cleanup statistics
        """
        # Check if audit_logs table exists
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.bind)
            if "audit_logs" not in inspector.get_table_names():
                return {"status": "table_not_found", "deleted": 0}
        except Exception:
            return {"status": "error_checking_table", "deleted": 0}
        
        retention_days = self.config.get_retention_days("audit_logs")
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Import audit log model if it exists
        try:
            from models.audit_log import AuditLog
            
            count_result = await db.execute(
                select(func.count()).select_from(AuditLog).where(
                    AuditLog.created_at < cutoff_date
                )
            )
            count = count_result.scalar()
            
            if not dry_run and count > 0:
                await db.execute(
                    delete(AuditLog).where(
                        AuditLog.created_at < cutoff_date
                    )
                )
            
            return {
                "retention_days": retention_days,
                "cutoff_date": cutoff_date.isoformat(),
                "deleted": count
            }
        except Exception as e:
            self.logger.warning(f"Could not clean up audit logs: {e}")
            return {"status": "error", "error": str(e), "deleted": 0}


def schedule_cleanup_tasks() -> None:
    """Schedule periodic cleanup tasks in the scheduler."""
    scheduler = get_scheduler()
    
    if scheduler is None:
        logger.warning("Scheduler not initialized, cannot schedule cleanup tasks")
        return
    
    from apscheduler.triggers.cron import CronTrigger
    
    # Schedule daily cleanup at 3 AM
    scheduler.add_job(
        func=run_scheduled_cleanup,
        trigger=CronTrigger(hour=3, minute=0),
        id="data_cleanup",
        name="Data retention cleanup",
        replace_existing=True,
        misfire_grace_time=3600
    )
    
    logger.info("Scheduled daily data cleanup task for 3:00 AM")


async def run_scheduled_cleanup() -> None:
    """Run cleanup as a scheduled task."""
    logger.info("Running scheduled data cleanup")
    
    try:
        task = DataCleanupTask()
        results = await task.run_cleanup(dry_run=False)
        
        logger.info(
            f"Scheduled cleanup completed: {results['tasks']}",
            extra={"cleanup_results": results}
        )
    except Exception as e:
        logger.error(f"Scheduled cleanup failed: {e}", exc_info=True)


async def get_storage_stats(db: AsyncSession) -> Dict[str, Any]:
    """Get database storage statistics.
    
    Args:
        db: Database session
        
    Returns:
        Storage statistics
    """
    from models.job import Job as JobModel
    
    stats = {
        "timestamp": datetime.utcnow().isoformat(),
        "tables": {}
    }
    
    # Job counts by status
    status_counts = {}
    for status in JobStatus:
        count_result = await db.execute(
            select(func.count()).select_from(JobModel).where(
                JobModel.status == status
            )
        )
        status_counts[status] = count_result.scalar()
    
    stats["tables"]["jobs"] = {
        "total": sum(status_counts.values()),
        "by_status": status_counts
    }
    
    # Recent jobs (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_result = await db.execute(
        select(func.count()).select_from(JobModel).where(
            JobModel.created_at >= thirty_days_ago
        )
    )
    stats["tables"]["jobs"]["last_30_days"] = recent_result.scalar()
    
    # Estimate data size (rough approximation)
    # This could be made more accurate with database-specific queries
    stats["estimated_size_mb"] = "unknown"  # Would need DB-specific implementation
    
    return stats


# Backwards compatibility
JobStatus = None  # Will be imported when needed
