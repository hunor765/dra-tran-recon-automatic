from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime, time


class ScheduleConfig(BaseModel):
    """Configuration for scheduled job runs"""
    days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of days to fetch data for (1-365). Used if start_date not provided."
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date (YYYY-MM-DD). If provided, days is ignored"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date (YYYY-MM-DD). Defaults to today"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=5,
        description="Maximum number of retry attempts for failed jobs (0-5)"
    )
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class ScheduleBase(BaseModel):
    frequency: str = "daily"  # daily, weekly, hourly
    time_of_day: Optional[time] = None  # HH:MM:SS format
    timezone: str = "Europe/Bucharest"
    is_active: bool = True
    config: Optional[ScheduleConfig] = Field(
        default=None,
        description="Job configuration for scheduled runs"
    )


class ScheduleCreate(ScheduleBase):
    client_id: int


class ScheduleUpdate(BaseModel):
    frequency: Optional[str] = None
    time_of_day: Optional[time] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[ScheduleConfig] = None


class Schedule(ScheduleBase):
    id: int
    client_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    next_run: Optional[str] = None  # Computed field

    class Config:
        from_attributes = True
