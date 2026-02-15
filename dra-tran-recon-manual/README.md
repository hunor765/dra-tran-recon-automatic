# DRA Transaction Reconciliation Platform

A platform for reconciling transaction data between e-commerce stores (Shopify, WooCommerce) and Google Analytics 4.

**Live URLs:**
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🚀 Quick Start

### 1. Start the Applications

```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend (on port 3001)
cd frontend
npm run dev -- -p 3001
```

### 2. Setup Test Accounts

**⚠️ IMPORTANT**: Read these first:
1. **[SUPABASE_SETUP.md](SUPABASE_SETUP.md)** - Explains `auth.users` vs `clients` table
2. **[TEST_ACCOUNTS.md](TEST_ACCOUNTS.md)** - Create login accounts
3. **[SETUP_SUMMARY.md](SETUP_SUMMARY.md)** - Complete setup checklist

### 3. Connect Your Store

**Shopify (Easiest):** See [SHOPIFY_SETUP.md](SHOPIFY_SETUP.md)

**WooCommerce:** See [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md)

**Google Analytics 4:** See [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md)

---

## 📚 Documentation

All guides are in this folder:

| File | Purpose |
|------|---------|
| **SUPABASE_SETUP.md** | ⭐ READ FIRST - Explains data model |
| **TEST_ACCOUNTS.md** | Test account setup (admin@dra.com, client@example.com) |
| **SETUP_SUMMARY.md** | Complete setup checklist |
| **QUICK_START.md** | Step-by-step from zero to reconciliation |
| **SHOPIFY_SETUP.md** | Shopify API setup (easiest option) |
| **API_INTEGRATION_GUIDE.md** | WooCommerce + GA4 setup |
| **UI_NAVIGATION.md** | Visual guide - where to click |
| **BACKEND_INTEGRATION_REFERENCE.md** | Technical details for customization |

---

## 📁 Project Structure

```
dra-tran-recon-manual/
├── backend/              # FastAPI application (Port 8000)
│   ├── core/
│   │   ├── ingestors/    # Shopify, WooCommerce, GA4 ingestors
│   │   └── reconciliation.py
│   └── api/v1/endpoints/ # REST API routes
├── frontend/             # Next.js application (Port 3001)
│   ├── src/app/
│   │   ├── admin/        # Admin panel
│   │   └── dashboard/    # Client dashboard
│   └── src/components/   # Shared UI components
└── database/             # SQL setup files
    ├── COMPLETE_SETUP.sql
    └── SETUP_USERS.sql
```

---

## 🔑 Test Account Credentials

After creating in Supabase Auth:

| Email | Password | Access |
|-------|----------|--------|
| `admin@dra.com` | `AdminTest123!` | Full admin panel |
| `client@example.com` | `ClientTest123!` | Dashboard only |

---

## 🔌 Supported Connectors

| Platform | Credentials Needed | Difficulty |
|----------|-------------------|------------|
| **Shopify** | shop_url, access_token (shpat_...) | ⭐ Easy |
| **WooCommerce** | url, consumer_key, consumer_secret | ⭐⭐ Medium |
| **Google Analytics 4** | property_id, service_account_json | ⭐⭐ Medium |

---

## ⚠️ Common Confusion

**`clients` table ≠ user accounts!**

- **`auth.users`** (Supabase Auth) = Login accounts (admin@dra.com)
- **`clients` table** = Business entities ("My Shopify Store")
- **`user_clients` table** = Links users to their assigned businesses

See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for detailed explanation.

---

## ✅ Pre-Launch Checklist

- [ ] Read `SUPABASE_SETUP.md` (understand data model)
- [ ] Create `admin@dra.com` in Supabase Auth
- [ ] Create `client@example.com` in Supabase Auth
- [ ] Run `database/COMPLETE_SETUP.sql`
- [ ] Create a business client
- [ ] Link users to client via `user_clients`
- [ ] Add real API credentials (Shopify OR WooCommerce)
- [ ] Add GA4 connector with real credentials
- [ ] Test both connectors (green checkmark)
- [ ] Click "Run Now" to start reconciliation

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't login | Check users in Supabase Auth dashboard |
| User sees no clients | Check `user_clients` table links |
| Connector test fails | Verify real API credentials |
| Admin can't access panel | Email must end with @dra.com, @datarevolt.ro, or @revolt.agency |

---

## 📝 Environment Variables

Backend (`backend/core/config.py`):
```python
DATABASE_URL=postgresql://postgres:[password]@db.wwvhozhsdloceptyibhx.supabase.co:5432/postgres
SUPABASE_URL=https://wwvhozhsdloceptyibhx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...
```

Frontend (`frontend/.env.local`):
```
NEXT_PUBLIC_SUPABASE_URL=https://wwvhozhsdloceptyibhx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

**Ready to start?** Read [SUPABASE_SETUP.md](SUPABASE_SETUP.md) → [TEST_ACCOUNTS.md](TEST_ACCOUNTS.md) → [QUICK_START.md](QUICK_START.md)
