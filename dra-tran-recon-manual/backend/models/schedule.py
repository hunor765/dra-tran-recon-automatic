from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from core.database import Base


class Schedule(Base):
    """Client schedule configuration for automated reconciliation jobs"""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), unique=True, nullable=False)
    
    # Schedule configuration
    frequency = Column(String, default="daily")  # daily, weekly, hourly
    time_of_day = Column(Time, nullable=True)  # For daily/weekly: 03:00:00
    timezone = Column(String, default="Europe/Bucharest")
    is_active = Column(Boolean, default=True)
    
    # Job configuration for scheduled runs
    config = Column(JSONB, nullable=True)  # e.g., {"days": 30}
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    client = relationship("Client", back_populates="schedule")
