"""Base ingestor class for data sources."""
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class IngestorError(Exception):
    """Base exception for ingestor errors."""
    
    def __init__(self, message: str, source: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.source = source
        self.details = details or {}


class ConfigurationError(IngestorError):
    """Raised when ingestor configuration is invalid or missing."""
    pass


class APIError(IngestorError):
    """Raised when external API call fails."""
    
    def __init__(self, message: str, source: str = None, status_code: int = None, details: dict = None):
        super().__init__(message, source, details)
        self.status_code = status_code


class DataValidationError(IngestorError):
    """Raised when fetched data fails validation."""
    pass


class BaseIngestor(ABC):
    """Abstract base class for data ingestors.
    
    All ingestors must implement the fetch_data method and should
    raise appropriate exceptions rather than returning empty DataFrames.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _get_date_range(
        self,
        days: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[datetime, datetime]:
        """Calculate date range for data fetching.
        
        Args:
            days: Number of days to look back (used if start_date not provided)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to today)
            
        Returns:
            Tuple of (start_datetime, end_datetime)
            
        Raises:
            DataValidationError: If date format is invalid or range is invalid
        """
        try:
            if end_date:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                # Set to end of day
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            else:
                end_dt = datetime.now()
            
            if start_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                # Set to start of day
                start_dt = start_dt.replace(hour=0, minute=0, second=0)
            else:
                start_dt = end_dt - timedelta(days=days)
            
            # Validate range
            if start_dt > end_dt:
                raise DataValidationError(
                    "Start date must be before end date",
                    details={"start_date": start_date, "end_date": end_date}
                )
            
            # Validate not in future (allow 1 day buffer for timezone issues)
            if start_dt > datetime.now() + timedelta(days=1):
                raise DataValidationError(
                    "Start date cannot be in the future",
                    details={"start_date": start_date}
                )
            
            return start_dt, end_dt
            
        except ValueError as e:
            raise DataValidationError(
                f"Invalid date format. Use YYYY-MM-DD: {e}",
                details={"start_date": start_date, "end_date": end_date}
            ) from e
    
    def _validate_dataframe(self, df: pd.DataFrame, required_columns: list) -> pd.DataFrame:
        """Validate that DataFrame has required columns.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            
        Returns:
            The validated DataFrame
            
        Raises:
            DataValidationError: If validation fails
        """
        if df is None:
            raise DataValidationError("DataFrame is None")
        
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise DataValidationError(
                f"Missing required columns: {missing_cols}",
                details={"required": required_columns, "actual": list(df.columns)}
            )
        
        return df
    
    @abstractmethod
    async def fetch_data(
        self,
        days: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch data from the source.
        
        Args:
            days: Number of days to fetch (used if start_date not provided)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to today)
            
        Returns:
            DataFrame with standardized columns:
                - clean_id: Transaction ID
                - value: Transaction value
                - Additional columns as appropriate for the source
                
        Raises:
            ConfigurationError: If ingestor is not properly configured
            APIError: If the external API call fails
            DataValidationError: If the returned data is invalid
        """
        pass
