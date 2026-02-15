from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


class BaseIngestor(ABC):
    @abstractmethod
    async def fetch_data(
        self, 
        days: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch data from the source.
        
        Args:
            days: Number of days to fetch (used if start_date not provided)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to today)
        
        Returns:
            DataFrame with the fetched data
        """
        pass
    
    def _get_date_range(
        self, 
        days: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> tuple[datetime, datetime]:
        """
        Calculate start and end dates based on parameters.
        
        Returns:
            Tuple of (start_datetime, end_datetime)
        """
        # Parse end_date or use now
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
        else:
            end_dt = datetime.now()
        
        # Parse start_date or calculate from days
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            start_dt = start_dt.replace(hour=0, minute=0, second=0)
        else:
            start_dt = end_dt - timedelta(days=days)
        
        return start_dt, end_dt
