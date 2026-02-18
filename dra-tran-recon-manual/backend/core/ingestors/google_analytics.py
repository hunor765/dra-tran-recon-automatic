"""Google Analytics 4 (GA4) ingestor for fetching transaction data."""
import json
import logging
from typing import Optional

import pandas as pd

from .base import BaseIngestor, ConfigurationError, APIError, DataValidationError
from core.cache import cached

logger = logging.getLogger(__name__)


class GA4Ingestor(BaseIngestor):
    """Ingestor for Google Analytics 4 transaction data."""
    
    REQUIRED_COLUMNS = ["clean_id", "value", "date"]
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.property_id = config.get("property_id")
        self.credentials = config.get("credentials_json")
        
        # Validate configuration
        if not self.property_id:
            raise ConfigurationError(
                "GA4 property_id is required",
                source="ga4",
                details={"missing": "property_id"}
            )
        
        if not self.credentials:
            raise ConfigurationError(
                "GA4 credentials_json is required",
                source="ga4",
                details={"missing": "credentials_json"}
            )

    @cached(ttl=600, key_prefix="ga4", skip_args=[0])  # Cache for 10 minutes, skip self
    async def fetch_data(
        self,
        days: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch GA4 purchase data for the specified date range.
        
        Args:
            days: Number of days to fetch (used if start_date not provided)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to today)
            
        Returns:
            DataFrame with columns: clean_id, value, date, browser, device
            
        Raises:
            ConfigurationError: If GA4 is not properly configured
            APIError: If the GA4 API call fails
            DataValidationError: If the returned data is invalid
        """
        # Calculate date range
        start_dt, end_dt = self._get_date_range(days, start_date, end_date)
        
        logger.info(
            f"Fetching GA4 data for property {self.property_id}",
            extra={
                "property_id": self.property_id,
                "start_date": start_dt.date().isoformat(),
                "end_date": end_dt.date().isoformat(),
            }
        )
        
        try:
            from google.analytics.data_v1beta import BetaAnalyticsDataClient
            from google.analytics.data_v1beta.types import (
                DateRange,
                Dimension,
                Metric,
                RunReportRequest,
            )
            
            # Parse credentials if string
            creds_info = self.credentials
            if isinstance(creds_info, str):
                try:
                    creds_info = json.loads(creds_info)
                except json.JSONDecodeError as e:
                    raise ConfigurationError(
                        "Invalid JSON in GA4 credentials",
                        source="ga4",
                        details={"error": str(e)}
                    ) from e

            client = BetaAnalyticsDataClient.from_service_account_info(creds_info)

            # Format dates for GA4 API (YYYY-MM-DD)
            start_date_str = start_dt.strftime("%Y-%m-%d")
            end_date_str = end_dt.strftime("%Y-%m-%d")

            # Build request
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[
                    Dimension(name="transactionId"),
                    Dimension(name="date"),
                    Dimension(name="browser"),
                    Dimension(name="deviceCategory"),
                ],
                metrics=[
                    Metric(name="purchaseRevenue"),
                ],
                date_ranges=[DateRange(start_date=start_date_str, end_date=end_date_str)],
            )

            response = client.run_report(request)
            
            # Check for API errors in response
            if hasattr(response, 'error') and response.error:
                raise APIError(
                    f"GA4 API error: {response.error}",
                    source="ga4",
                    details={"property_id": self.property_id}
                )

            data = []
            for row in response.rows:
                data.append({
                    "clean_id": row.dimension_values[0].value,
                    "date": row.dimension_values[1].value,  # YYYYMMDD
                    "browser": row.dimension_values[2].value,
                    "device": row.dimension_values[3].value,
                    "value": float(row.metric_values[0].value) if row.metric_values[0].value else 0.0
                })

            df = pd.DataFrame(data)
            
            # Date formatting (GA4 returns YYYYMMDD)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")
            
            # Validate result
            self._validate_dataframe(df, self.REQUIRED_COLUMNS)
            
            logger.info(
                f"Successfully fetched {len(df)} GA4 records",
                extra={"property_id": self.property_id, "records": len(df)}
            )
            
            return df

        except (ConfigurationError, APIError, DataValidationError):
            raise
        except Exception as e:
            logger.error(f"Error fetching GA4 data: {e}", exc_info=True)
            raise APIError(
                f"Failed to fetch GA4 data: {e}",
                source="ga4",
                details={"property_id": self.property_id}
            ) from e
