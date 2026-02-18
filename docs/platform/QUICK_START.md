# DRA Platform - Quick Start Guide

## Step 1: Create Test Accounts

### Via Supabase Dashboard
1. Go to https://supabase.com/dashboard/project/wwvhozhsdloceptyibhx/auth/users
2. Add two users:

**Admin User:**
- Email: `admin@dra.com`
- Password: `AdminTest123!`
- Email confirmed: ✅

**Client User:**
- Email: `client@example.com`
- Password: `ClientTest123!`
- Email confirmed: ✅

---

## Step 2: Start the Applications

### Backend (Terminal 1)
```bash
cd dra-tran-recon-manual/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```
Backend runs on: http://localhost:8000

### Frontend (Terminal 2)
```bash
cd dra-tran-recon-manual/frontend
npm run dev
```
Frontend runs on: http://localhost:3000

---

## Step 3: Initial Setup

### 3.1 Login as Admin
1. Open http://localhost:3000/login
2. Select **"Admin Login"**
3. Enter: `admin@dra.com` / `AdminTest123!`

### 3.2 Create a Client
1. Go to **Clients** page
2. Click **"Add Client"**
3. Enter:
   - Name: `Test Store`
   - Slug: `test-store`
4. Click **Create**

### 3.3 Assign Client User
1. Click on the new client
2. Click **"Users"** tab
3. Click **"Invite User"**
4. Enter: `client@example.com`
5. Role: `viewer`
6. Click **Send Invite**

---

## Step 4: Connect APIs (Choose Your Store Type)

### Option A: Shopify Store (Easiest)

#### Get Shopify Credentials:
1. Login to Shopify admin: `https://your-store.myshopify.com/admin`
2. Go to **Settings** → **Apps and sales channels**
3. Click **Develop apps** → **Create an app**
4. Name: "DRA Reconciliation"
5. **Configuration** → Enable `read_orders` permission
6. **API credentials** → **Install app**
7. Copy **Admin API access token**: `shpat_xxxxxxxx...`

#### Add to DRA:
1. Select **Shopify** connector type
2. Fill in:
   - Shop URL: `your-store.myshopify.com`
   - Access Token: `shpat_...`

📄 **Detailed Shopify Guide**: See [SHOPIFY_SETUP.md](SHOPIFY_SETUP.md)

---

### Option B: WooCommerce Store

#### Get WooCommerce Credentials:
1. Login to WordPress admin: `https://your-store.com/wp-admin`
2. Go to **WooCommerce** → **Settings** → **Advanced** → **REST API**
3. Click **Add key**
4. Description: `DRA Reconciliation`
5. User: Select admin
6. Permissions: **Read**
7. Click **Generate API key**
8. Copy:
   - Consumer Key (starts with `ck_`)
   - Consumer Secret (starts with `cs_`)

#### Add to DRA:
1. In DRA Admin, go to your client
2. Click **"Connectors"**
3. Click **"Add Connector"**
4. Select **WooCommerce**
5. Fill in:
   - Store URL: `https://your-store.com`
   - Consumer Key: (paste)
   - Consumer Secret: (paste)
6. Click **Test** to verify
7. Click **Create**

---

### Option B: Shopify Store

#### Get Shopify Credentials:
1. Login to Shopify admin
2. Go to **Settings** → **Apps and sales channels**
3. Click **Develop apps**
4. Create private app
5. Enable read access to **Orders**
6. Copy Admin API access token

#### Add to DRA:
1. Select **Shopify** connector type
2. Fill in:
   - Shop URL: `your-store.myshopify.com`
   - Access Token: (paste)

---

### Step 5: Connect Google Analytics 4

#### Get GA4 Credentials:

1. **Create Google Cloud Project**:
   - Go to https://console.cloud.google.com/
   - Create new project
   - Enable **Google Analytics Data API**

2. **Create Service Account**:
   - Go to **IAM & Admin** → **Service Accounts**
   - Click **Create Service Account**
   - Name: `dra-reconciliation`
   - Role: **Analytics Viewer**

3. **Download JSON Key**:
   - Click service account → **Keys** → **Add Key** → **Create New Key**
   - Select **JSON**
   - Save the downloaded file

4. **Grant GA4 Access**:
   - Go to https://analytics.google.com/
   - Select your property
   - **Admin** → **Property Access Management**
   - Add user: `dra-reconciliation@project-id.iam.gserviceaccount.com`
   - Role: **Viewer**

5. **Get Property ID**:
   - In GA4 Admin, look for 9-digit number at top
   - Example: `123456789`

#### Add to DRA:
1. Click **"Add Connector"**
2. Select **Google Analytics 4**
3. Fill in:
   - Property ID: `123456789` (your 9-digit ID)
   - Service Account JSON: (paste entire contents of downloaded JSON file)
4. Click **Test** to verify
5. Click **Create**

---

## Step 6: Run First Reconciliation

### Via Admin Panel:
1. Go to your client detail page
2. Click **"Run Now"** button
3. Wait for job to complete (refresh Jobs page)

### Or via API:
```bash
curl -X POST http://localhost:8000/api/v1/jobs/run/1
```

---

## Step 7: View Results

### As Admin:
- Go to **Jobs** page
- See reconciliation results

### As Client:
1. Logout from admin
2. Login as `client@example.com` (OTP login)
3. View **Dashboard** for reconciliation results

---

## Data Flow Summary

```
WooCommerce/Shopify ──┐
                      ├──► DRA Backend ──► Analysis ──► Results
Google Analytics 4 ───┘
```

### What Gets Compared:

| Field | WooCommerce | GA4 |
|-------|-------------|-----|
| Transaction ID | `order.id` | `transactionId` |
| Value | `order.total` | `purchaseRevenue` |
| Status | `order.status` | (implied) |

### Match Logic:
- Transaction IDs match → **Matched**
- Transaction in WooCommerce but NOT in GA4 → **Missing Order** (tracking gap!)
- Transaction in GA4 but NOT in WooCommerce → **Phantom Order** (duplicate/test)

---

## Troubleshooting

### "Test Connection Failed"
- Check URL format (needs `https://`)
- Verify credentials are correct
- Check if API is enabled

### "No Data Returned"
- Check date range (default: last 30 days)
- Verify transactions exist in both systems
- Check backend logs for errors

### "Permission Denied"
- Verify user roles in Supabase
- Check middleware.ts admin patterns

---

## Files You Might Need to Modify

| File | Purpose |
|------|---------|
| `backend/core/ingestors/woocommerce.py` | WooCommerce API integration |
| `backend/core/ingestors/google_analytics.py` | GA4 API integration |
| `backend/core/ingestors/shopify.py` | Shopify API integration |
| `backend/api/v1/endpoints/jobs.py` | Reconciliation logic |

---

## Next Steps

1. ✅ Create accounts
2. ✅ Add connectors
3. ✅ Run first reconciliation
4. 📊 Review results in dashboard
5. 🔧 Fine-tune based on discrepancies found
