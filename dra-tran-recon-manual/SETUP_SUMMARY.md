# DRA Platform - Setup Summary

## ✅ What's Already Configured

### Applications Running

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | http://localhost:3001 | ✅ Running |
| **Backend API** | http://localhost:8000 | ✅ Running |
| **API Docs** | http://localhost:8000/docs | ✅ Swagger UI |
| **Supabase** | https://supabase.com/dashboard/project/wwvhozhsdloceptyibhx | ✅ Online |

---

## 📊 Database Tables

### Already Created in Supabase

| Table | Purpose |
|-------|---------|
| `clients` | Business entities (stores like "My Shopify Store") |
| `connectors` | API credentials (Shopify, WooCommerce, GA4) |
| `jobs` | Reconciliation run results |
| `user_clients` | Links Supabase Auth users to their assigned clients |

---

## 🔐 Authentication & RBAC

### Data Model (IMPORTANT!)

```
┌────────────────────────────────────────────────────────────────┐
│ SUPABASE AUTH (Login Accounts)                                  │
├────────────────────────────────────────────────────────────────┤
│ • Created in: Supabase Dashboard → Authentication → Users       │
│ • Stores: Email, password, email confirmation                   │
│ • Not: Business clients!                                        │
└──────────────┬─────────────────────────────────┬───────────────┘
               │                                 │
               │ user_id (UUID)                  │ user_id (UUID)
               ▼                                 ▼
┌────────────────────────────────────────────────────────────────┐
│ YOUR DATABASE                                                   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  user_clients table (the "link" between users and businesses)   │
│  ├─ user_id + client_id + role (admin/viewer)                  │
│  └─ status: invited / active / inactive                        │
│                                                                 │
│  clients table (business entities being monitored)              │
│  └─ name, slug, logo_url, is_active                            │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Test Account Credentials

| Email | Password | Role | Access |
|-------|----------|------|--------|
| `admin@dra.com` | `AdminTest123!` | Admin | Admin Panel + All Clients |
| `client@example.com` | `ClientTest123!` | Viewer | Dashboard Only (assigned clients) |

---

## 📝 Next Steps to Complete Setup

### Step 1: Create Test Users in Supabase Auth

**Go to**: https://supabase.com/dashboard/project/wwvhozhsdloceptyibhx/auth/users

1. Click **"Add User"** → **"Create New User"**
2. Create **admin@dra.com** with password `AdminTest123!`
3. ✅ Check "Email confirmed"
4. Create **client@example.com** with password `ClientTest123!`
5. ✅ Check "Email confirmed"

### Step 2: Run Database Setup (If Not Done)

**Go to**: https://supabase.com/dashboard/project/wwvhozhsdloceptyibhx/sql

1. Open `database/COMPLETE_SETUP.sql`
2. Copy all content
3. Paste in SQL Editor and click **Run**

This creates all tables with proper RLS policies.

### Step 3: Link Users to Clients

After creating users, get their UUIDs:
```sql
SELECT id, email FROM auth.users 
WHERE email IN ('admin@dra.com', 'client@example.com');
```

Then run `database/SETUP_USERS.sql` with actual UUIDs (already in file, just update if needed).

---

## 🔌 Connector Types Supported

### 1. Shopify (Easiest!)

**Fields Required**:
- `shop_url`: `my-store.myshopify.com` (without https://)
- `access_token`: `shpat_xxxxxxxxxxxxxxxx`

**How to Get**: See `SHOPIFY_SETUP.md`

### 2. WooCommerce

**Fields Required**:
- `url`: `https://my-store.com`
- `consumer_key`: `ck_xxxxxxxx`
- `consumer_secret`: `cs_xxxxxxxx`

**How to Get**: See `API_INTEGRATION_GUIDE.md`

### 3. Google Analytics 4

**Fields Required**:
- `property_id`: `123456789`
- `credentials_json`: Full Service Account JSON

**How to Get**: See `API_INTEGRATION_GUIDE.md`

---

## 📂 Documentation Files

| File | Purpose | Priority |
|------|---------|----------|
| **SUPABASE_SETUP.md** | Explains auth.users vs clients table confusion | ⭐⭐⭐ READ FIRST |
| **TEST_ACCOUNTS.md** | Detailed test account setup instructions | ⭐⭐⭐ Essential |
| **QUICK_START.md** | Complete step-by-step setup from zero | ⭐⭐⭐ Essential |
| **SHOPIFY_SETUP.md** | Shopify API setup (easiest option) | ⭐⭐ Recommended |
| **API_INTEGRATION_GUIDE.md** | WooCommerce + GA4 setup | ⭐⭐ Recommended |
| **UI_NAVIGATION.md** | Visual guide showing where to click | ⭐ Helpful |
| **BACKEND_INTEGRATION_REFERENCE.md** | Technical details for customization | ⭐ Technical |

---

## 🔧 Code Structure

### Backend (`dra-tran-recon-manual/backend/`)
```
core/ingestors/
├── shopify.py          # Shopify API integration
├── woocommerce.py      # WooCommerce API integration
├── google_analytics.py # GA4 API integration
└── reconciliation.py   # Comparison algorithm

api/v1/endpoints/
├── clients.py          # Client CRUD
├── connectors.py       # Connector CRUD + test
└── jobs.py             # Run reconciliation
```

### Frontend (`dra-tran-recon-manual/frontend/`)
```
src/app/
├── admin/
│   ├── clients/        # Client management
│   │   ├── page.tsx    # List all clients
│   │   └── [id]/       # Client detail
│   │       ├── page.tsx              # "Run Now" button
│   │       └── connectors/
│   │           └── page.tsx          # Add/test connectors
│   ├── jobs/           # Jobs history
│   └── history/        # Detailed history
└── dashboard/          # Client dashboard
    └── page.tsx        # View assigned client data

src/components/
├── ui/
│   ├── Toast.tsx           # Toast notifications
│   ├── StatusBadge.tsx     # Status display
│   └── LoadingSkeleton.tsx # Loading states
└── layout/
    └── AdminNav.tsx        # Navigation
```

---

## ✅ Pre-Launch Checklist

Before running first reconciliation:

### Infrastructure
- [x] Backend running on port 8000
- [x] Frontend running on port 3001
- [x] CORS configured (allows localhost:3000 and 3001)

### Authentication
- [ ] Created `admin@dra.com` in Supabase Auth
- [ ] Created `client@example.com` in Supabase Auth
- [ ] Read `SUPABASE_SETUP.md` to understand data model

### Database
- [ ] Ran `COMPLETE_SETUP.sql` to create tables
- [ ] Created a business client in `clients` table
- [ ] Linked users to client via `user_clients` table

### Connectors (Need Real Credentials!)
- [ ] **Shopify** OR **WooCommerce** connector added with real API credentials
- [ ] **GA4** connector added with real Property ID + Service Account JSON
- [ ] Both connectors tested successfully (green checkmark)

### First Reconciliation
- [ ] Clicked "Run Now" on client detail page
- [ ] Viewed results in Jobs page or Client Dashboard

---

## 🐛 Troubleshooting

### "Cannot login"
- Check users exist in **Supabase Dashboard → Authentication → Users**
- Make sure email is confirmed
- Passwords: `AdminTest123!` and `ClientTest123!`

### "User can't see any clients"
- Check `user_clients` table has links
- Verify `user_clients.status` = 'active'
- Verify `user_clients.user_id` matches `auth.users.id`

### "Admin can't access admin panel"
- Email must end with: `@dra.com`, `@datarevolt.ro`, or `@revolt.agency`
- OR add role to user_metadata in Supabase

### "No connectors configured"
- Need REAL API credentials - mock mode shows data but doesn't connect
- Shopify: Get `shpat_...` token from private app
- WooCommerce: Get `ck_...` and `cs_...` from REST API settings
- GA4: Create service account, download JSON, add to GA4 property

### "Connector test failed"
- Check credentials are correct
- Verify API permissions (read_orders for Shopify, etc.)
- Check CORS (backend already configured)
- Look at browser console for detailed error

---

## 📞 Quick Commands

```bash
# Start backend
cd dra-tran-recon-manual/backend && python main.py

# Start frontend (port 3001)
cd dra-tran-recon-manual/frontend && npm run dev -- -p 3001

# Verify running
curl http://localhost:8000/docs  # Should show Swagger UI
curl http://localhost:3001       # Should show Next.js app
```

---

## 🎉 You're Almost Ready!

Once you complete the checklist above:

1. **Login** as admin: http://localhost:3001/login
2. **Add connectors** with real API credentials
3. **Click "Run Now"** to start reconciliation
4. **View results** showing tracking gaps between store and GA4

---

**Documentation Location**: `dra-tran-recon-manual/*.md`

**Next Step**: Read `SUPABASE_SETUP.md` then `TEST_ACCOUNTS.md`
