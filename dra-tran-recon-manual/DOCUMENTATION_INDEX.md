# DRA Platform - Documentation Index

## Quick Links

| Document | Purpose |
|----------|---------|
| **SUPABASE_SETUP.md** | Explains auth.users vs clients table (READ FIRST!) |
| **QUICK_START.md** | Step-by-step setup from zero to first reconciliation |
| **TEST_ACCOUNTS.md** | Test account credentials and creation instructions |
| **SHOPIFY_SETUP.md** | Complete Shopify API setup guide ⭐ |
| **API_INTEGRATION_GUIDE.md** | Detailed guide for connecting WooCommerce and GA4 |
| **UI_NAVIGATION.md** | Visual guide showing where to click in the UI |
| **BACKEND_INTEGRATION_REFERENCE.md** | Technical details on data flow and field mappings |
| **README_GUIDES.md** | Master index of all documentation |

---

## For First-Time Setup:

### 1. Understand the Data Model (IMPORTANT!)
📄 **SUPABASE_SETUP.md**
- Explains `auth.users` vs `clients` table confusion
- Visual diagram of data relationships
- **READ THIS FIRST** to avoid confusion

### 2. Create Test Accounts
📄 **TEST_ACCOUNTS.md**
- Admin: `admin@dra.com` / `AdminTest123!`
- Client: `client@example.com` / `ClientTest123!`
- Instructions for creating via Supabase dashboard

### 2. Connect Your Store

**For Shopify Stores:** 📄 **SHOPIFY_SETUP.md**
- Easiest setup option ⭐
- How to create a private app
- Get access token in 5 minutes

**For WooCommerce Stores:** 📄 **API_INTEGRATION_GUIDE.md**
- How to get WooCommerce API keys
- How to set up GA4 service account
- Where to enter credentials in the platform

### 3. Run First Reconciliation
📄 **QUICK_START.md**
- Start backend and frontend
- Create client in admin panel
- Add connectors
- Run reconciliation job

---

## Navigation Quick Reference

### Admin Panel Access
```
http://localhost:3000/login
→ Select "Admin Login"
→ Enter admin@dra.com
→ Go to Clients → Add Client → Connectors
```

### Client Dashboard Access
```
http://localhost:3000/login
→ Select "Client Login (OTP)"
→ Enter client@example.com
→ Check email for magic link
→ View reconciliation results
```

---

## Key Backend Files

| File | Purpose |
|------|---------|
| `backend/core/ingestors/woocommerce.py` | Fetches orders from WooCommerce |
| `backend/core/ingestors/google_analytics.py` | Fetches transactions from GA4 |
| `backend/core/ingestors/shopify.py` | Fetches orders from Shopify |
| `backend/api/v1/endpoints/jobs.py` | Runs reconciliation algorithm |
| `backend/core/encryption.py` | Encrypts connector credentials |

---

## Key Frontend Files

| File | Purpose |
|------|---------|
| `frontend/src/app/admin/clients/[id]/connectors/page.tsx` | Connector management UI |
| `frontend/src/app/admin/clients/[id]/page.tsx` | Client detail with "Run Now" |
| `frontend/src/app/dashboard/page.tsx` | Client dashboard (results) |
| `frontend/src/lib/api/client.ts` | API client for backend calls |

---

## API Endpoints

### Connectors
```
POST   /api/v1/clients/{id}/connectors     # Create
GET    /api/v1/clients/{id}/connectors     # List
POST   /api/v1/connectors/{id}/test        # Test connection
DELETE /api/v1/connectors/{id}             # Delete
```

### Jobs
```
POST   /api/v1/jobs/run/{client_id}        # Trigger reconciliation
GET    /api/v1/jobs/{id}                   # Get job details
GET    /api/v1/jobs?client_id=X            # List jobs
```

### Admin
```
GET    /api/v1/admin/stats                 # Dashboard stats
GET    /api/v1/admin/jobs                  # All jobs with filters
```

---

## Data Flow Summary

```
1. Admin adds connectors (WooCommerce + GA4) via UI
2. Credentials encrypted and stored in PostgreSQL
3. Admin clicks "Run Now" → Backend creates job
4. Backend fetches data from both sources
5. Backend compares transaction IDs
6. Results stored in job.result_summary (JSON)
7. Client views results in dashboard
```

---

## Need Help?

1. **Can't login?** → Check TEST_ACCOUNTS.md
2. **Can't add connector?** → Check API_INTEGRATION_GUIDE.md
3. **Don't know where to click?** → Check UI_NAVIGATION.md
4. **Want to customize data fields?** → Check BACKEND_INTEGRATION_REFERENCE.md
