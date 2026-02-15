# DRA Platform - API Integration Guide

This guide explains where and how to connect your WooCommerce store and Google Analytics 4 (GA4) account.

---

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   WooCommerce   │      │   DRA Platform   │      │      GA4        │
│     Store       │─────►│    (Backend)     │◄─────│   (Google)      │
│                 │      │                  │      │                 │
│ - Orders API    │      │ - Reconciliation │      │ - Transactions  │
│ - Products      │      │ - Analysis       │      │ - Revenue       │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   PostgreSQL     │
                       │   (Supabase)     │
                       └──────────────────┘
```

---

## PART 1: Where to Add API Credentials

### In the Admin Panel (Frontend)

1. **Login as Admin**: http://localhost:3001/login
   - Use your admin credentials

2. **Navigate to Client**: Admin → Clients → Select Client

3. **Go to Connectors Tab**: Click "Connectors" button

4. **Add Connectors**:
   
   You'll see 3 connector types:
   - **Google Analytics 4** (for GA4 data)
   - **WooCommerce** (for WordPress/WooCommerce stores)
   - **Shopify** (for Shopify stores)

> 💡 **Which one should I use?**
> - Use **WooCommerce** if your store is on WordPress
> - Use **Shopify** if your store is on Shopify
> - Both work the same way for reconciliation!

---

## PART 2: Option A - Shopify (Easiest)

### Step 1: Create a Private App

1. Login to your **Shopify Admin**: `https://your-store.myshopify.com/admin`
2. Go to **Settings** → **Apps and sales channels**
3. Click **Develop apps** → **Create an app**
4. Name it "DRA Reconciliation"

### Step 2: Enable Permissions

1. Go to **Configuration** tab
2. Click **Configure** on **Admin API access scopes**
3. Enable: ✅ `read_orders`
4. Click **Save**

### Step 3: Install & Get Token

1. Go to **API credentials** tab
2. Click **Install app**
3. Copy the **Admin API access token**: `shpat_xxxxxxxx...`
4. Note your **Shop URL**: `your-store.myshopify.com`

### Step 4: Enter in DRA

1. Click **"Add Connector"**
2. Select **"Shopify"**
3. Fill in:
   - **Shop URL**: `your-store.myshopify.com`
   - **Access Token**: `shpat_...` (paste token)
4. Click **"Test Connection"**
5. Click **"Create Connector"**

📄 **Full Shopify Guide**: See [SHOPIFY_SETUP.md](SHOPIFY_SETUP.md)

---

## PART 3: Option B - WooCommerce

### Step 1: Enable REST API in WooCommerce

1. Login to your WordPress admin: `https://your-store.com/wp-admin`
2. Go to **WooCommerce** → **Settings** → **Advanced** → **REST API**
3. Click **Add key**
4. Fill in:
   - **Description**: "DRA Reconciliation"
   - **User**: Select admin user
   - **Permissions**: **Read** (only need to read orders)
5. Click **Generate API key**

### Step 2: Save Credentials

You'll get:
- **Consumer Key**: `ck_xxxxxxxxxxxxxxxxxxxxxx`
- **Consumer Secret**: `cs_xxxxxxxxxxxxxxxxxxxxxx`

### Step 3: Enter in DRA Platform

In the DRA Admin Panel:
1. Click **"Add Connector"**
2. Select **"WooCommerce"**
3. Fill in:
   - **Store URL**: `https://your-store.com`
   - **Consumer Key**: (paste from WooCommerce)
   - **Consumer Secret**: (paste from WooCommerce)
4. Click **"Test Connection"** to verify
5. Click **"Create Connector"**

---

## PART 3: Getting GA4 API Credentials

### Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable the **Google Analytics Data API**:
   - Go to **APIs & Services** → **Library**
   - Search "Google Analytics Data API"
   - Click **Enable**

### Step 2: Create Service Account

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Fill in:
   - **Name**: `dra-reconciliation`
   - **Description**: "DRA Platform GA4 Access"
4. Click **Create and Continue**
5. For role, select: **Analytics Viewer** (or **Viewer**)
6. Click **Continue** → **Done**

### Step 3: Create and Download Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create New Key**
4. Select **JSON** format
5. Click **Create**
6. A JSON file will download (save it securely!)

### Step 4: Grant GA4 Access

1. Go to https://analytics.google.com/
2. Select your GA4 property
3. Go to **Admin** (bottom left)
4. Under **Property** column, click **Property Access Management**
5. Click **Add users**
6. Enter the **Service Account Email** (from step 2, looks like: `dra-reconciliation@project-id.iam.gserviceaccount.com`)
7. Role: **Viewer** (or **Analyst**)
8. Click **Add**

### Step 5: Get Property ID

1. In GA4 Admin, look at the top navigation
2. You'll see: `Property` → `XXXXXX` (9-digit number)
3. This is your **Property ID**

### Step 6: Enter in DRA Platform

In the DRA Admin Panel:
1. Click **"Add Connector"**
2. Select **"Google Analytics 4"**
3. Fill in:
   - **Property ID**: (your 9-digit GA4 property ID)
   - **Service Account JSON**: (paste the entire contents of the downloaded JSON file)
4. Click **"Test Connection"** to verify
5. Click **"Create Connector"**

---

## Supported Platforms Summary

| Platform | Connector Type | What You Need |
|----------|----------------|---------------|
| **Shopify** | `shopify` | Shop URL + Access Token (`shpat_...`) |
| **WooCommerce** | `woocommerce` | Store URL + Consumer Key/Secret (`ck_...` / `cs_...`) |
| **Google Analytics 4** | `ga4` | Property ID (9 digits) + Service Account JSON |

You can add **ONE store connector** (Shopify OR WooCommerce) + **GA4** for reconciliation.

---

## PART 4: Backend Code Locations

If you need to modify how data is fetched, here are the key files:

### WooCommerce Ingestor
**File**: `backend/core/ingestors/woocommerce.py`

```python
class WooCommerceIngestor(BaseIngestor):
    async def fetch_data(self, days: int) -> pd.DataFrame:
        # Fetches orders from WooCommerce REST API
        # Returns: DataFrame with columns: clean_id, value, date, status
```

### GA4 Ingestor
**File**: `backend/core/ingestors/google_analytics.py`

```python
class GA4Ingestor(BaseIngestor):
    async def fetch_data(self, days: int) -> pd.DataFrame:
        # Fetches transactions from GA4 Data API
        # Returns: DataFrame with columns: clean_id, date, browser, device, value
```

### Reconciliation Logic
**File**: `backend/api/v1/endpoints/jobs.py`

```python
async def execute_reconciliation(job_id: int, client_id: int, db: AsyncSession):
    # 1. Fetch connectors for client
    # 2. Get data from both sources
    # 3. Compare and calculate match rate
    # 4. Store results
```

---

## PART 5: Running Your First Reconciliation

### Option 1: Manual Trigger (Admin Panel)

1. Login as Admin
2. Go to **Clients** → Select your client
3. Click **"Run Now"** button
4. Wait for job to complete (check Jobs page for status)

### Option 2: Via API

```bash
curl -X POST http://localhost:8000/api/v1/jobs/run/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## PART 6: Viewing Results

### Admin View
- Go to **Jobs** page
- See list of all reconciliation jobs
- Click **"View"** to see detailed results

### Client View
- Login as client user
- Go to **Dashboard**
- See match rate, missing orders, discrepancies
- Go to **History** to see past reconciliations

---

## Troubleshooting

### WooCommerce Connection Fails
- Check if store URL has `https://`
- Verify API credentials haven't expired
- Ensure WooCommerce version is 3.5+ (has REST API)
- Check if permalinks are enabled in WordPress

### GA4 Connection Fails
- Verify Property ID is correct (9 digits)
- Ensure service account email has been added to GA4 property
- Check if JSON key is valid (not expired)
- Verify Google Analytics Data API is enabled in Cloud Console

### No Data Returned
- Check date range (default is last 30 days)
- Verify there are transactions in both systems
- Check backend logs for errors

---

## API Endpoints Reference

### Connectors
```
POST   /api/v1/clients/{id}/connectors     # Create connector
GET    /api/v1/clients/{id}/connectors     # List connectors
POST   /api/v1/connectors/{id}/test        # Test connection
DELETE /api/v1/connectors/{id}             # Delete connector
```

### Jobs
```
POST   /api/v1/jobs/run/{client_id}        # Trigger reconciliation
GET    /api/v1/jobs/{id}                   # Get job details
GET    /api/v1/jobs?client_id=X            # List jobs for client
```

### Data Flow
```
1. Create connectors (GA4 + WooCommerce)
2. Trigger job via POST /api/v1/jobs/run/{client_id}
3. Backend fetches data from both sources
4. Backend compares and calculates metrics
5. Results stored in database
6. Frontend displays results
```

---

## Need Help?

If you encounter issues:
1. Check browser console for frontend errors
2. Check backend logs: `docker logs dra-backend` or terminal running FastAPI
3. Verify all environment variables are set
4. Ensure Supabase is accessible
