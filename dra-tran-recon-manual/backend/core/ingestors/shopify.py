"""Shopify ingestor for fetching order data."""
import logging
import re
from typing import Optional

import pandas as pd

from .base import BaseIngestor, ConfigurationError, APIError, DataValidationError
from core.cache import cached

logger = logging.getLogger(__name__)


class ShopifyIngestor(BaseIngestor):
    """Ingestor for Shopify order data."""
    
    REQUIRED_COLUMNS = ["clean_id", "value"]
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.shop_url = config.get("shop_url")
        self.token = config.get("access_token")
        
        # Validate configuration
        if not self.shop_url:
            raise ConfigurationError(
                "Shopify shop_url is required",
                source="shopify",
                details={"missing": "shop_url"}
            )
        
        if not self.token:
            raise ConfigurationError(
                "Shopify access_token is required",
                source="shopify",
                details={"missing": "access_token"}
            )
        
        # Normalize shop URL
        self.shop_domain = self.shop_url.replace("https://", "").replace("http://", "").rstrip("/")

    @cached(ttl=600, key_prefix="shopify", skip_args=[0])
    async def fetch_data(
        self,
        days: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch Shopify orders for the specified date range.
        
        Args:
            days: Number of days to fetch (used if start_date not provided)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to today)
            
        Returns:
            DataFrame with columns: clean_id, value, status, payment_method
            
        Raises:
            ConfigurationError: If Shopify is not properly configured
            APIError: If the Shopify API call fails
            DataValidationError: If the returned data is invalid
        """
        # Calculate date range
        start_dt, end_dt = self._get_date_range(days, start_date, end_date)
        
        logger.info(
            f"Fetching Shopify orders from {self.shop_domain}",
            extra={
                "shop_domain": self.shop_domain,
                "start_date": start_dt.date().isoformat(),
                "end_date": end_dt.date().isoformat(),
            }
        )
        
        try:
            import httpx
            
            # Format dates for Shopify API (ISO 8601)
            created_at_min = start_dt.isoformat()
            created_at_max = end_dt.isoformat()
            
            orders = []
            url = f"https://{self.shop_domain}/admin/api/2023-10/orders.json"
            
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
            
            page_count = 0
            max_pages = 100  # Safety limit to prevent infinite loops
            
            async with httpx.AsyncClient() as client:
                while page_count < max_pages:
                    page_count += 1
                    
                    response = await client.get(
                        url,
                        headers=headers,
                        params=params,
                        timeout=30.0
                    )
                    
                    if response.status_code == 401:
                        raise APIError(
                            "Shopify API authentication failed. Check your access token.",
                            source="shopify",
                            status_code=401,
                            details={"shop_domain": self.shop_domain}
                        )
                    elif response.status_code == 403:
                        raise APIError(
                            "Shopify API access forbidden. Check your permissions.",
                            source="shopify",
                            status_code=403,
                            details={"shop_domain": self.shop_domain}
                    )
                    elif response.status_code == 429:
                        raise APIError(
                            "Shopify API rate limit exceeded. Please try again later.",
                            source="shopify",
                            status_code=429,
                            details={"shop_domain": self.shop_domain}
                        )
                    elif response.status_code != 200:
                        raise APIError(
                            f"Shopify API error: {response.status_code} - {response.text}",
                            source="shopify",
                            status_code=response.status_code,
                            details={"shop_domain": self.shop_domain}
                        )
                        
                    data = response.json()
                    page_orders = data.get("orders", [])
                    
                    if not page_orders:
                        break
                    
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
                
                if page_count >= max_pages:
                    logger.warning(
                        f"Reached maximum page limit ({max_pages}) for Shopify orders",
                        extra={"shop_domain": self.shop_domain}
                    )
            
            df = pd.DataFrame(orders)
            
            # Validate result
            self._validate_dataframe(df, self.REQUIRED_COLUMNS)
            
            logger.info(
                f"Successfully fetched {len(df)} Shopify orders",
                extra={
                    "shop_domain": self.shop_domain,
                    "orders_count": len(df),
                    "pages": page_count
                }
            )
            
            return df

        except (ConfigurationError, APIError, DataValidationError):
            raise
        except Exception as e:
            logger.error(f"Error fetching Shopify data: {e}", exc_info=True)
            raise APIError(
                f"Failed to fetch Shopify data: {e}",
                source="shopify",
                details={"shop_domain": self.shop_domain}
            ) from e
