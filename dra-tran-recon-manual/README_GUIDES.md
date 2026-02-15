# 📚 DRA Platform - Setup Guides

This folder contains all the documentation you need to set up and use the DRA Reconciliation Platform.

---

## 🚀 Start Here

| Guide | Read This If... |
|-------|-----------------|
| **SUPABASE_SETUP.md** | ⚠️ **Read first!** Explains auth.users vs clients table - avoids common confusion |
| **QUICK_START.md** | You want a complete step-by-step setup |
| **TEST_ACCOUNTS.md** | You need login credentials for testing |

---

## 🔌 Connecting Your Store

Choose your platform:

| Platform | Guide | Difficulty |
|----------|-------|------------|
| **Shopify** ⭐ | [SHOPIFY_SETUP.md](SHOPIFY_SETUP.md) | Easy - 5 minutes |
| **WooCommerce** | [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md) | Medium - 10 minutes |
| **Google Analytics 4** | [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md) | Medium - 15 minutes |

**Recommendation**: If you have a Shopify store, start with that - it's the easiest to set up!

---

## 📖 All Documentation Files

### Setup Guides
| File | Description |
|------|-------------|
| `SUPABASE_SETUP.md` | ⚠️ **Essential!** Explains data model: auth.users vs clients table |
| `QUICK_START.md` | Complete setup from zero to working reconciliation |
| `TEST_ACCOUNTS.md` | Admin and client test account credentials |
| `SHOPIFY_SETUP.md` | Shopify API setup (easiest option) ⭐ |
| `API_INTEGRATION_GUIDE.md` | WooCommerce + GA4 setup instructions |
| `UI_NAVIGATION.md` | Visual guide showing where to click |

### Technical Reference
| File | Description |
|------|-------------|
| `BACKEND_INTEGRATION_REFERENCE.md` | Data flow, field mappings, code locations |
| `DOCUMENTATION_INDEX.md` | Index of all documentation |
| `README_GUIDES.md` | This file - overview of all guides |

---

## 🎯 Quick Start Path

### 1. Understand the Data Model ⚠️
📄 **SUPABASE_SETUP.md**
- **IMPORTANT**: `auth.users` ≠ `clients` table
- `auth.users` = Login accounts (admin@dra.com, client@example.com)
- `clients` = Business entities (your stores)
- `user_clients` = Links users to their stores

**Don't confuse them!** Read this first to avoid setup issues.

### 2. Create Test Accounts
📄 **TEST_ACCOUNTS.md**
```
Admin: admin@dra.com / AdminTest123!
Client: client@example.com / ClientTest123!
```

### 2. Start the Apps
```bash
# Terminal 1 - Backend
cd dra-tran-recon-manual/backend
python main.py

# Terminal 2 - Frontend
cd dra-tran-recon-manual/frontend
npm run dev -- -p 3001
```

### 4. Connect Your Store

**Shopify (Easiest):**
1. Go to **Settings** → **Apps** → **Develop apps**
2. Create app → Enable `read_orders`
3. Install app → Copy `shpat_...` token
4. In DRA: Add Connector → Shopify → Paste credentials

**WooCommerce:**
1. Go to **WooCommerce** → **Settings** → **REST API**
2. Add key → Copy `ck_...` and `cs_...`
3. In DRA: Add Connector → WooCommerce → Paste credentials

### 5. Add GA4
1. Google Cloud → Service Account → Download JSON
2. GA4 → Admin → Add service account
3. In DRA: Add Connector → GA4 → Paste Property ID + JSON

### 6. Run Reconciliation
1. In DRA: Click **"Run Now"**
2. View results in Jobs page or Client Dashboard

---

## ❓ Need Help?

| Question | See This File |
|----------|---------------|
| **Confused about users vs clients?** | **SUPABASE_SETUP.md** ⚠️ |
| Can't login? | TEST_ACCOUNTS.md |
| Don't know where to click? | UI_NAVIGATION.md |
| Shopify setup issues? | SHOPIFY_SETUP.md |
| WooCommerce API issues? | API_INTEGRATION_GUIDE.md |
| GA4 setup issues? | API_INTEGRATION_GUIDE.md |
| Want to customize code? | BACKEND_INTEGRATION_REFERENCE.md |
| What data gets compared? | BACKEND_INTEGRATION_REFERENCE.md |

---

## 📁 File Locations

### Backend Code (for customization)
```
dra-tran-recon-manual/backend/
├── core/ingestors/
│   ├── shopify.py          # Shopify API integration
│   ├── woocommerce.py      # WooCommerce API integration
│   └── google_analytics.py # GA4 API integration
└── api/v1/endpoints/
    └── jobs.py             # Reconciliation algorithm
```

### Frontend Code (for UI customization)
```
dra-tran-recon-manual/frontend/
└── src/app/
    ├── admin/clients/[id]/
    │   ├── page.tsx        # Client detail with "Run Now"
    │   └── connectors/     # Connector management
    └── dashboard/          # Client dashboard
```

---

## ✅ Checklist

Before running your first reconciliation:

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3001
- [ ] Read SUPABASE_SETUP.md (understand auth.users vs clients)
- [ ] Test accounts created in Supabase Auth
- [ ] Business client created in Admin Panel
- [ ] Users linked to client via user_clients table
- [ ] **Store connector added** (Shopify OR WooCommerce)
- [ ] **GA4 connector added**
- [ ] Both connectors tested successfully
- [ ] Clicked "Run Now" to start reconciliation

---

## 🎉 You're Ready!

Once you've completed the checklist above, your DRA Platform is fully configured and ready to detect tracking gaps between your store and Google Analytics!

**Access URLs:**
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
