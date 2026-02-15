import pandas as pd
from typing import Optional
from datetime import datetime, timedelta
from .base import BaseIngestor


class ShopifyIngestor(BaseIngestor):
    def __init__(self, config: dict):
        self.shop_url = config.get("shop_url")
        self.token = config.get("access_token")

    async def fetch_data(
        self, 
        days: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch Shopify orders for the specified date range.
        
        Args:
            days: Number of days to fetch (used if start_date not provided)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to today)
        """
        # Calculate date range
        start_dt, end_dt = self._get_date_range(days, start_date, end_date)
        
        print(f"Fetching Shopify orders from {self.shop_url} ({start_dt.date()} to {end_dt.date()})...")
        
        if not self.shop_url or not self.token:
            print("Missing Shopify configuration, returning mock data.")
            return pd.DataFrame([
                {"clean_id": "SH-5001", "value": 199.99, "status": "paid", "payment_method": "shopify_payments"},
                {"clean_id": "SH-5002", "value": 29.50, "status": "paid", "payment_method": "paypal"},
            ])
            
        try:
            import httpx
            import re
            
            # Format dates for Shopify API (ISO 8601)
            created_at_min = start_dt.isoformat()
            created_at_max = end_dt.isoformat()
            
            async with httpx.AsyncClient() as client:
                orders = []
                # Ensure protocol
                shop_domain = self.shop_url.replace("https://", "").replace("http://", "").rstrip("/")
                url = f"https://{shop_domain}/admin/api/2023-10/orders.json"
                
                params = {
                    "status": "any",
                    "created_at_min": created_at_min,
                    "created_at_max": created_at_max,
                    "limit": 250
                }
                
                headers = {
                    "X-Shopify-Access-Token": self.token,
                    "Content-Type": "application/json"
                }
                
                while True:
                    response = await client.get(
                        url,
                        headers=headers,
                        params=params,
                        timeout=30.0
                    )
                    
                    if response.status_code != 200:
                        print(f"Shopify API Error: {response.status_code} - {response.text}")
                        break
                        
                    data = response.json()
                    page_orders = data.get("orders", [])
                    
                    for order in page_orders:
                        # Extract payment method (can be list)
                        payment_gateways = order.get("payment_gateway_names", [])
                        payment_method = payment_gateways[0] if payment_gateways else "unknown"
                        
                        orders.append({
                            "clean_id": str(order.get("name")),
                            "value": float(order.get("total_price", 0)),
                            "status": order.get("financial_status"),
                            "payment_method": payment_method
                        })
                    
                    # Handle Pagination via Link Header
                    link_header = response.headers.get("Link")
                    if not link_header:
                        break
                        
                    # Parse Link header to find rel="next"
                    next_link = None
                    links = link_header.split(",")
                    for link in links:
                        if 'rel="next"' in link:
                            match = re.search(r'<(.*)>', link)
                            if match:
                                next_link = match.group(1)
                                break
                    
                    if next_link:
                        url = next_link
                        params = {}
                    else:
                        break
                        
            return pd.DataFrame(orders)

        except Exception as e:
            print(f"Error fetching Shopify data: {e}")
            return pd.DataFrame()
