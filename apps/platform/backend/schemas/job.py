from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional
from datetime import datetime, date, timedelta


class JobBase(BaseModel):
    pass


def validate_date_string(v: Optional[str], field_name: str) -> Optional[str]:
    """Validate date string format and logic.
    
    Args:
        v: Date string to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated date string
        
    Raises:
        ValueError: If date format is invalid or date is in the future
    """
    if v is None:
        return v
    
    # Validate format
    try:
        parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{field_name} must be in YYYY-MM-DD format (e.g., 2024-01-15)")
    
    # Validate not too far in the future (allow 1 day buffer for timezones)
    max_future = date.today() + timedelta(days=1)
    if parsed_date > max_future:
        raise ValueError(f"{field_name} cannot be more than 1 day in the future")
    
    # Validate not too old (limit to 2 years for performance)
    min_date = date.today() - timedelta(days=730)
    if parsed_date < min_date:
        raise ValueError(f"{field_name} cannot be more than 2 years in the past")
    
    return v


class JobCreate(BaseModel):
    """Schema for creating a new job"""
    client_id: int = Field(..., gt=0, description="Client ID must be a positive integer")
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
    
    @validator('start_date')
    def validate_start_date(cls, v):
        return validate_date_string(v, "start_date")
    
    @validator('end_date')
    def validate_end_date(cls, v):
        return validate_date_string(v, "end_date")
    
    @root_validator(skip_on_failure=True)
    def validate_date_range(cls, values):
        """Validate that start_date <= end_date if both are provided."""
        start = values.get('start_date')
        end = values.get('end_date')
        
        if start and end:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
            
            if start_date > end_date:
                raise ValueError("start_date must be before or equal to end_date")
            
            # Validate date range is not too large (max 365 days)
            date_range_days = (end_date - start_date).days
            if date_range_days > 365:
                raise ValueError("Date range cannot exceed 365 days")
        
        return values


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
    
    @validator('start_date')
    def validate_start_date(cls, v):
        return validate_date_string(v, "start_date")
    
    @validator('end_date')
    def validate_end_date(cls, v):
        return validate_date_string(v, "end_date")
    
    @root_validator(skip_on_failure=True)
    def validate_date_range(cls, values):
        """Validate that start_date <= end_date if both are provided."""
        start = values.get('start_date')
        end = values.get('end_date')
        
        if start and end:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
            
            if start_date > end_date:
                raise ValueError("start_date must be before or equal to end_date")
            
            # Validate date range is not too large (max 365 days)
            date_range_days = (end_date - start_date).days
            if date_range_days > 365:
                raise ValueError("Date range cannot exceed 365 days")
        
        return values


class JobRetryRequest(BaseModel):
    """Schema for retrying a failed job"""
    job_id: int
    max_retries: int = Field(default=3, ge=1, le=5, description="Maximum retry attempts")
