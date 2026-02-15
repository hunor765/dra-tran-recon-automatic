import pandas as pd
# import shopify

class ShopifyIngestor:
    def __init__(self, shop_url, access_token):
        self.shop_url = shop_url
        self.token = access_token

    def fetch_orders(self, days=2):
        print(f"Fetching Shopify orders from {self.shop_url} (last {days} days)...")
        # Mock Data
        return pd.DataFrame([
            {"clean_id": "SH-5001", "value": 199.99, "status": "paid", "payment_method": "shopify_payments"},
            {"clean_id": "SH-5002", "value": 29.50, "status": "paid", "payment_method": "paypal"},
        ])
