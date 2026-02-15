from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date


class JobBase(BaseModel):
    pass


class JobCreate(BaseModel):
    """Schema for creating a new job"""
    client_id: int
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
    config: Optional[dict] = Field(
        default=None,
        description="Optional job-specific configuration"
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


class Job(BaseModel):
    id: int
    client_id: int
    client_name: Optional[str] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_run: Optional[datetime] = None  # Alias for started_at to match frontend expectations
    result_summary: Optional[dict] = None
    logs: Optional[str] = None
    days: int = 30  # Number of days the job was configured to fetch
    start_date: Optional[str] = None  # Explicit start date
    end_date: Optional[str] = None  # Explicit end date
    config: Optional[dict] = None
    retry_count: int = 0  # Number of retry attempts
    max_retries: int = 3  # Maximum retry attempts

    class Config:
        from_attributes = True


class JobConfig(BaseModel):
    """Schema for job configuration parameters"""
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


class JobRetryRequest(BaseModel):
    """Schema for retrying a failed job"""
    job_id: int
    max_retries: int = Field(default=3, ge=1, le=5, description="Maximum retry attempts")
