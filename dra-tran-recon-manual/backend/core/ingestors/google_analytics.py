import pandas as pd
from typing import Optional
from datetime import datetime, timedelta
from .base import BaseIngestor
import json


class GA4Ingestor(BaseIngestor):
    def __init__(self, config: dict):
        self.property_id = config.get("property_id")
        self.credentials = config.get("credentials_json")

    async def fetch_data(
        self, 
        days: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch GA4 data for the specified date range.
        
        Args:
            days: Number of days to fetch (used if start_date not provided)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to today)
        """
        # Calculate date range
        start_dt, end_dt = self._get_date_range(days, start_date, end_date)
        
        print(f"Fetching GA4 data for property {self.property_id} ({start_dt.date()} to {end_dt.date()})...")
        
        # Fallback to mock if no credentials configured (for dev safety)
        if not self.property_id or not self.credentials:
            print("Missing GA4 configuration, returning mock data.")
            return pd.DataFrame([
                {"clean_id": "ORD-1001", "value": 150.00, "date": "2026-01-20", "browser": "Chrome", "device": "desktop"},
                {"clean_id": "ORD-1002", "value": 89.99, "date": "2026-01-20", "browser": "Safari", "device": "mobile"},
                {"clean_id": "ORD-1004", "value": 200.50, "date": "2026-01-21", "browser": "Edge", "device": "desktop"},
            ])

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
                except json.JSONDecodeError:
                    print("Invalid JSON in GA4 credentials")
                    return pd.DataFrame()

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

            data = []
            for row in response.rows:
                data.append({
                    "clean_id": row.dimension_values[0].value,
                    "date": row.dimension_values[1].value,  # YYYYMMDD
                    "browser": row.dimension_values[2].value,
                    "device": row.dimension_values[3].value,
                    "value": float(row.metric_values[0].value)
                })

            df = pd.DataFrame(data)
            
            # Date formatting (GA4 returns YYYYMMDD)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")

            return df

        except Exception as e:
            print(f"Error fetching GA4 data: {e}")
            return pd.DataFrame()
