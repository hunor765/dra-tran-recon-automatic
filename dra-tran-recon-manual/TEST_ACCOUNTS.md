# DRA Platform - Test Accounts Setup

## ⚠️ IMPORTANT: Understanding the Data Model

There are **TWO SEPARATE SYSTEMS** for users:

1. **`auth.users`** (Supabase Auth) - Actual login accounts ⬅️ CREATE THESE HERE
2. **`clients`** table - Business entities/stores being monitored
3. **`user_clients`** table - Links users to clients

**Don't confuse them!** `clients` table is NOT for user accounts.

---

## Test Account Credentials

### Admin Account (for Admin Panel access)
```
Email: admin@dra.com
Password: AdminTest123!
Role: Administrator
Access: Full admin panel - can create clients, run jobs, view all data
```

### Client Account (for Client Dashboard access)
```
Email: client@example.com
Password: ClientTest123!
Role: Viewer
Access: Dashboard only - can view their assigned client's reconciliation data
```

---

## Step 1: Create Users in Supabase Auth

### Go to Supabase Dashboard:
```
https://supabase.com/dashboard/project/wwvhozhsdloceptyibhx/auth/users
```

### Create Admin User:
1. Click **"Add User"** → **"Create New User"**
2. Email: `admin@dra.com`
3. Password: `AdminTest123!`
4. ✅ **Email confirmed**: Check this box!
5. Click **"Create User"**

### Create Client User:
1. Click **"Add User"** → **"Create New User"**
2. Email: `client@example.com`
3. Password: `ClientTest123!`
4. ✅ **Email confirmed**: Check this box!
5. Click **"Create User"**

---

## Step 2: Run Database Setup

### Option A: Run Complete Setup Script

1. Go to **Supabase Dashboard** → **SQL Editor**
2. Copy contents of `database/COMPLETE_SETUP.sql`
3. Click **Run**

This creates:
- `clients` table (business entities)
- `connectors` table (API credentials)
- `jobs` table (reconciliation results)
- `user_clients` table (user-client linking)
- RLS policies (security)

### Option B: Run Just the User Links (If Tables Already Exist)

1. First, get the UUIDs of your created users:
```sql
SELECT id, email FROM auth.users 
WHERE email IN ('admin@dra.com', 'client@example.com');
```

2. Run `database/SETUP_USERS.sql` with the actual UUIDs

---

## Step 3: Create a Business Client

**Note**: This is NOT a user account! This is the store/company being monitored.

### Via SQL:
```sql
INSERT INTO public.clients (name, slug, is_active)
VALUES ('Test Store', 'test-store', true);
```

### Or via Admin Panel (after login):
1. Login as `admin@dra.com`
2. Go to **Clients** → **Add Client**
3. Name: "Test Store"
4. Slug: "test-store"

---

## Step 4: Link Users to Client

**Important**: This connects the login accounts (auth.users) to the business entity (clients)

### Get User UUIDs:
```sql
SELECT id, email FROM auth.users;
-- Copy the UUIDs for admin@dra.com and client@example.com
```

### Insert Links:
```sql
-- Link admin user (replace ADMIN_UUID with actual value)
INSERT INTO public.user_clients (user_id, client_id, email, role, status)
VALUES (
    'ADMIN_UUID_HERE',
    (SELECT id FROM public.clients WHERE slug = 'test-store'),
    'admin@dra.com',
    'admin',
    'active'
);

-- Link client user (replace CLIENT_UUID with actual value)
INSERT INTO public.user_clients (user_id, client_id, email, role, status)
VALUES (
    'CLIENT_UUID_HERE',
    (SELECT id FROM public.clients WHERE slug = 'test-store'),
    'client@example.com',
    'viewer',
    'active'
);
```

---

## Step 5: Verify Setup

### Check Users Exist:
```sql
-- Should show 2 users
SELECT email, created_at FROM auth.users;
```

### Check Client Exists:
```sql
-- Should show 1 client
SELECT * FROM public.clients;
```

### Check User-Client Links:
```sql
-- Should show 2 links
SELECT uc.email, uc.role, c.name as client_name
FROM public.user_clients uc
JOIN public.clients c ON uc.client_id = c.id;
```

---

## Visual Data Flow

```
┌────────────────────────────────────────────────────────────────┐
│ SUPABASE AUTH (User Accounts)                                   │
├────────────────────────────────────────────────────────────────┤
│ • admin@dra.com (UUID: abc-123)                                │
│ • client@example.com (UUID: xyz-789)                           │
└──────────────┬─────────────────────────────────┬───────────────┘
               │                                 │
               │ UUID reference                  │ UUID reference
               ▼                                 ▼
┌────────────────────────────────────────────────────────────────┐
│ YOUR DATABASE                                                   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  user_clients table (links users to clients)                    │
│  ├─ abc-123 → Test Store (role: admin)                         │
│  └─ xyz-789 → Test Store (role: viewer)                        │
│                                                                 │
│  clients table (business entities)                              │
│  └─ Test Store (slug: test-store)                              │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Login URLs

- **Admin Panel**: http://localhost:3001/login → Select **"Admin Login"**
- **Client Dashboard**: http://localhost:3001/login → Select **"Client Login (OTP)"**

---

## Troubleshooting

### "User doesn't exist"
- Check **Authentication** → **Users** in Supabase dashboard
- Make sure you created them there, not in SQL

### "User can't see client data"
- Check `user_clients` table has the link
- Verify `user_clients.status` = 'active'
- Verify `user_clients.user_id` matches `auth.users.id`

### "Admin can't access admin panel"
- Check email domain: must match `@dra.com`, `@datarevolt.ro`, or `@revolt.agency`
- Or add role to user_metadata in Supabase Auth

### "No clients table"
- Run `database/COMPLETE_SETUP.sql` first
- Then run `database/SETUP_USERS.sql`

---

## Quick Commands Summary

```bash
# 1. Create users in Supabase Auth dashboard
#    https://supabase.com/dashboard/project/wwvhozhsdloceptyibhx/auth/users

# 2. Run database setup (in Supabase SQL Editor)
-- \i database/COMPLETE_SETUP.sql

# 3. Create test client
INSERT INTO public.clients (name, slug) VALUES ('Test Store', 'test-store');

# 4. Get user UUIDs
SELECT id, email FROM auth.users WHERE email LIKE '%@dra.com' OR email LIKE '%@example.com';

# 5. Link users to client (use actual UUIDs from step 4)
-- See database/SETUP_USERS.sql

# 6. Verify
SELECT uc.email, uc.role, c.name 
FROM public.user_clients uc 
JOIN public.clients c ON uc.client_id = c.id;
```

---

## Files to Reference

| File | Purpose |
|------|---------|
| `SUPABASE_SETUP.md` | Detailed explanation of data model |
| `database/COMPLETE_SETUP.sql` | Creates all tables |
| `database/SETUP_USERS.sql` | Links users to clients |

---

## ✅ Checklist

Before trying to login:

- [ ] Created `admin@dra.com` in Supabase Auth
- [ ] Created `client@example.com` in Supabase Auth
- [ ] Ran `COMPLETE_SETUP.sql` to create tables
- [ ] Created a client in `public.clients` table
- [ ] Linked users to client in `public.user_clients` table
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3001

Then visit: http://localhost:3001/login
