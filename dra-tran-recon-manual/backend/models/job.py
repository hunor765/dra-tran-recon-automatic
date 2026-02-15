from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from core.database import Base
import enum


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    status = Column(String, default=JobStatus.PENDING)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    result_summary = Column(JSONB, nullable=True)
    logs = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Date range configuration
    days = Column(Integer, default=30, nullable=False)
    start_date = Column(String, nullable=True)  # YYYY-MM-DD format
    end_date = Column(String, nullable=True)  # YYYY-MM-DD format
    
    # Configuration
    config = Column(JSONB, nullable=True)
    
    # Retry configuration
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Relationship
    client = relationship("Client", back_populates="jobs")

    @property
    def last_run(self):
        """Alias for started_at to match frontend expectations"""
        return self.started_at
    
    @property
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.status == JobStatus.FAILED.value and self.retry_count < self.max_retries
