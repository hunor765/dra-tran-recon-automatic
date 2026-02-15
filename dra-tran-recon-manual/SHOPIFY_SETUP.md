# Shopify API Setup Guide

Yes! You can absolutely connect a Shopify store to the DRA platform. Here's how to get your API credentials.

---

## Overview

| Platform | API Type | Difficulty | Data Available |
|----------|----------|------------|----------------|
| **WooCommerce** | REST API | Easy | Orders, customers, products |
| **Shopify** | REST API | Easy | Orders, transactions, customers |
| **GA4** | Google Data API | Medium | Transactions, revenue, attribution |

---

## Method 1: Private App (Recommended for DRA)

### Step 1: Create a Private App

1. Login to your **Shopify Admin**: `https://your-store.myshopify.com/admin`
2. Go to **Settings** (bottom left)
3. Scroll down to **Apps and sales channels**
4. Click **Develop apps** (or **Private apps** on older Shopify)
5. Click **Create an app**

### Step 2: Configure App Permissions

1. Click on your new app
2. Go to **Configuration** tab
3. Click **Configure** next to **Admin API access scopes**
4. Enable these permissions:
   - ✅ `read_orders` - Read order data
   - ✅ `read_transactions` - Read payment transactions
   - ✅ `read_customers` - Read customer data (optional)
5. Click **Save**

### Step 3: Install the App

1. Go to **API credentials** tab
2. Click **Install app**
3. Confirm by clicking **Install**

### Step 4: Get Your Credentials

After installation, you'll see:

```
Admin API access token: shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Copy this token** - you'll only see it once!

Also note your:
- **Shop URL**: `your-store.myshopify.com` (without https://)

---

## Method 2: Custom App (Alternative)

If you can't access "Develop apps" (some Shopify plans restrict this):

1. Go to **Settings** → **Notifications** → **Webhooks** (not ideal)
2. Or use a **Custom App** via Shopify Partners

For most stores, **Method 1 (Private App)** is the easiest.

---

## Enter Credentials in DRA Platform

### In the Admin Panel:

1. Go to your **Client** → **Connectors**
2. Click **Add Connector**
3. Select **Shopify**
4. Fill in:

| Field | Value | Example |
|-------|-------|---------|
| **Shop URL** | your-store.myshopify.com | `my-store.myshopify.com` |
| **Access Token** | shpat_... | `shpat_a1b2c3d4e5f6...` |

5. Click **Test** to verify
6. Click **Create Connector**

---

## What Data Gets Fetched?

### From Shopify Orders API:

| Shopify Field | DRA Field | Description |
|---------------|-----------|-------------|
| `order.id` | `clean_id` | Order ID (e.g., "1001") |
| `order.total_price` | `value` | Total order value |
| `order.financial_status` | `status` | paid/pending/refunded |
| `order.gateway` | `payment_method` | Payment provider |
| `order.created_at` | `date` | Order date |

### Sample Shopify Order:
```json
{
  "id": 1001,
  "total_price": "149.99",
  "financial_status": "paid",
  "gateway": "shopify_payments",
  "created_at": "2026-01-15T10:30:00-05:00"
}
```

---

## Backend Code Location

**File**: `backend/core/ingestors/shopify.py`

```python
class ShopifyIngestor(BaseIngestor):
    def __init__(self, config: dict):
        self.shop_url = config.get("shop_url")  # your-store.myshopify.com
        self.access_token = config.get("access_token")  # shpat_...
    
    async def fetch_data(self, days: int) -> pd.DataFrame:
        # Fetches from: https://your-store.myshopify.com/admin/api/2024-01/orders.json
        # Returns: clean_id, value, status, payment_method
```

---

## Testing Your Connection

### Via cURL:
```bash
curl -H "X-Shopify-Access-Token: shpat_xxxxxxxxxxxxxxxx" \
  "https://your-store.myshopify.com/admin/api/2024-01/orders.json?limit=1"
```

### Expected Response:
```json
{
  "orders": [
    {
      "id": 1001,
      "total_price": "149.99",
      "financial_status": "paid"
    }
  ]
}
```

If you get a 200 response with order data, your credentials work!

---

## Troubleshooting

### "Authentication Failed"
- Check that the access token starts with `shpat_`
- Verify the app is **Installed** (not just created)
- Ensure you copied the entire token (it's long!)

### "No orders returned"
- Check that your Shopify store actually has orders
- Verify the date range (default is last 30 days)
- Make sure `read_orders` permission is enabled

### "Access denied"
- Your Shopify plan might restrict API access
- Contact Shopify Support to enable API access
- Or upgrade to a plan that supports custom apps

### "Invalid shop domain"
- Use only the subdomain: `my-store.myshopify.com`
- Don't include `https://`
- Don't include `/admin` or paths

---

## Comparison: WooCommerce vs Shopify

| Feature | WooCommerce | Shopify |
|---------|-------------|---------|
| **API Key Location** | WooCommerce → Settings → Advanced → REST API | Settings → Apps → Develop apps |
| **Key Format** | `ck_...` / `cs_...` | `shpat_...` |
| **Shop URL** | Full URL with https | Subdomain only |
| **Permissions** | Read/Write/Read-Write | Granular scopes |
| **Rate Limits** | Unlimited (your server) | 2 requests/second |
| **Data Available** | Orders, products, customers | Orders, products, customers |

---

## Full Setup Flow for Shopify

```
1. Create Shopify Private App
   └── Settings → Apps → Develop apps → Create app
   
2. Enable Permissions
   └── Configuration → Admin API → Enable read_orders
   
3. Install App
   └── API credentials → Install app
   
4. Copy Access Token
   └── Admin API access token: shpat_...
   
5. Add to DRA
   └── Admin → Clients → Your Client → Connectors
   └── Select "Shopify"
   └── Shop URL: your-store.myshopify.com
   └── Access Token: shpat_...
   
6. Test Connection
   └── Click "Test" button
   
7. Run Reconciliation
   └── Click "Run Now"
```

---

## Need More Help?

- **Shopify API Docs**: https://shopify.dev/docs/api/admin-rest
- **DRA Support**: Check BACKEND_INTEGRATION_REFERENCE.md for code details
