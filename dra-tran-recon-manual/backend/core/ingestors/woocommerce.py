import pandas as pd
from typing import Optional
from datetime import datetime, timedelta
from .base import BaseIngestor


class WooCommerceIngestor(BaseIngestor):
    def __init__(self, config: dict):
        self.url = config.get("url")
        self.key = config.get("consumer_key")
        self.secret = config.get("consumer_secret")

    async def fetch_data(
        self, 
        days: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch WooCommerce orders for the specified date range.
        
        Args:
            days: Number of days to fetch (used if start_date not provided)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to today)
        """
        # Calculate date range
        start_dt, end_dt = self._get_date_range(days, start_date, end_date)
        
        print(f"Fetching WooCommerce orders from {self.url} ({start_dt.date()} to {end_dt.date()})...")
        
        # Fallback to mock
        if not self.url or not self.key or not self.secret:
             print("Missing WooCommerce configuration, returning mock data.")
             return pd.DataFrame([
                {"clean_id": "ORD-1001", "value": 150.00, "status": "completed", "payment_method": "stripe"},
                {"clean_id": "ORD-1002", "value": 45.00, "status": "completed", "payment_method": "paypal"},
                {"clean_id": "ORD-1003", "value": 45.00, "status": "completed", "payment_method": "stripe"},
            ])

        try:
            import httpx
            
            # Format dates for WooCommerce API (ISO 8601)
            after_date = start_dt.isoformat()
            before_date = end_dt.isoformat()
            
            async with httpx.AsyncClient() as client:
                orders = []
                page = 1
                base_url = self.url.rstrip("/")
                endpoint = f"{base_url}/wp-json/wc/v3/orders"
                
                while True:
                    response = await client.get(
                        endpoint,
                        auth=(self.key, self.secret),
                        params={
                            "after": after_date,
                            "before": before_date,
                            "per_page": 100,
                            "page": page
                        },
                        timeout=30.0
                    )
                    
                    if response.status_code != 200:
                        print(f"WooCommerce API Error: {response.status_code} - {response.text}")
                        break
                        
                    page_orders = response.json()
                    if not page_orders:
                        break
                        
                    for order in page_orders:
                        orders.append({
                            "clean_id": str(order.get("id")),
                            "value": float(order.get("total", 0)),
                            "status": order.get("status"),
                            "payment_method": order.get("payment_method_title") or order.get("payment_method")
                        })
                    
                    # Check pagination
                    if len(page_orders) < 100:
                        break
                    
                    page += 1
            
            return pd.DataFrame(orders)

        except Exception as e:
            print(f"Error fetching WooCommerce data: {e}")
            return pd.DataFrame()
