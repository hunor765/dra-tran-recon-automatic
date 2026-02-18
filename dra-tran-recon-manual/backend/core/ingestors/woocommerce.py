"""WooCommerce ingestor for fetching order data."""
import logging
from typing import Optional

import pandas as pd

from .base import BaseIngestor, ConfigurationError, APIError, DataValidationError
from core.cache import cached

logger = logging.getLogger(__name__)


class WooCommerceIngestor(BaseIngestor):
    """Ingestor for WooCommerce order data."""
    
    REQUIRED_COLUMNS = ["clean_id", "value"]
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.url = config.get("url")
        self.key = config.get("consumer_key")
        self.secret = config.get("consumer_secret")
        
        # Validate configuration
        if not self.url:
            raise ConfigurationError(
                "WooCommerce url is required",
                source="woocommerce",
                details={"missing": "url"}
            )
        
        if not self.key:
            raise ConfigurationError(
                "WooCommerce consumer_key is required",
                source="woocommerce",
                details={"missing": "consumer_key"}
            )
        
        if not self.secret:
            raise ConfigurationError(
                "WooCommerce consumer_secret is required",
                source="woocommerce",
                details={"missing": "consumer_secret"}
            )

    @cached(ttl=600, key_prefix="woocommerce", skip_args=[0])
    async def fetch_data(
        self,
        days: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch WooCommerce orders for the specified date range.
        
        Args:
            days: Number of days to fetch (used if start_date not provided)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to today)
            
        Returns:
            DataFrame with columns: clean_id, value, status, payment_method
            
        Raises:
            ConfigurationError: If WooCommerce is not properly configured
            APIError: If the WooCommerce API call fails
            DataValidationError: If the returned data is invalid
        """
        # Calculate date range
        start_dt, end_dt = self._get_date_range(days, start_date, end_date)
        
        logger.info(
            f"Fetching WooCommerce orders from {self.url}",
            extra={
                "url": self.url,
                "start_date": start_dt.date().isoformat(),
                "end_date": end_dt.date().isoformat(),
            }
        )
        
        try:
            import httpx
            
            # Format dates for WooCommerce API (ISO 8601)
            after_date = start_dt.isoformat()
            before_date = end_dt.isoformat()
            
            orders = []
            page = 1
            base_url = self.url.rstrip("/")
            endpoint = f"{base_url}/wp-json/wc/v3/orders"
            
            max_pages = 100  # Safety limit
            
            async with httpx.AsyncClient() as client:
                while page <= max_pages:
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
                    
                    if response.status_code == 401:
                        raise APIError(
                            "WooCommerce API authentication failed. Check your consumer key and secret.",
                            source="woocommerce",
                            status_code=401,
                            details={"url": self.url}
                        )
                    elif response.status_code == 403:
                        raise APIError(
                            "WooCommerce API access forbidden. Check your permissions and ensure the REST API is enabled.",
                            source="woocommerce",
                            status_code=403,
                            details={"url": self.url}
                        )
                    elif response.status_code == 429:
                        raise APIError(
                            "WooCommerce API rate limit exceeded. Please try again later.",
                            source="woocommerce",
                            status_code=429,
                            details={"url": self.url}
                        )
                    elif response.status_code != 200:
                        raise APIError(
                            f"WooCommerce API error: {response.status_code} - {response.text}",
                            source="woocommerce",
                            status_code=response.status_code,
                            details={"url": self.url}
                        )
                        
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
                
                if page >= max_pages:
                    logger.warning(
                        f"Reached maximum page limit ({max_pages}) for WooCommerce orders",
                        extra={"url": self.url}
                    )
            
            df = pd.DataFrame(orders)
            
            # Validate result
            self._validate_dataframe(df, self.REQUIRED_COLUMNS)
            
            logger.info(
                f"Successfully fetched {len(df)} WooCommerce orders",
                extra={
                    "url": self.url,
                    "orders_count": len(df),
                    "pages": page
                }
            )
            
            return df

        except (ConfigurationError, APIError, DataValidationError):
            raise
        except Exception as e:
            logger.error(f"Error fetching WooCommerce data: {e}", exc_info=True)
            raise APIError(
                f"Failed to fetch WooCommerce data: {e}",
                source="woocommerce",
                details={"url": self.url}
            ) from e
