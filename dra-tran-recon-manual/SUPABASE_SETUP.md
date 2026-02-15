# Supabase Database Setup Guide

## The Confusion Explained

You said you have a single `clients` table - that's **CORRECT**! But `clients` is NOT for user accounts. Here's the proper data model:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SUPABASE AUTH                                   │
│  (Managed by Supabase, NOT visible in your tables)                      │
│                                                                         │
│  auth.users = Actual user accounts for login                            │
│  ├── admin@dra.com (admin role)                                         │
│  ├── client@example.com (user role)                                     │
│  └── any other user emails                                              │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  │ UUID reference
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      YOUR DATABASE TABLES                               │
│                                                                         │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐          │
│  │   clients    │      │  connectors  │      │     jobs     │          │
│  │──────────────│      │──────────────│      │──────────────│          │
│  │ id           │◄─────│ client_id    │      │ client_id    │          │
│  │ name         │      │ type         │      │ status       │          │
│  │ slug         │      │ config_json  │      │ results      │          │
│  └──────────────┘      └──────────────┘      └──────────────┘          │
│       ▲                                                                 │
│       │                                                                 │
│       └──────────────────┐                                              │
│                          │                                              │
│  ┌───────────────────────┴──────────────┐                              │
│  │           user_clients               │                              │
│  │──────────────────────────────────────│                              │
│  │ user_id (UUID from auth.users)       │                              │
│  │ client_id (from clients table)       │                              │
│  │ role ('admin' or 'viewer')           │                              │
│  │ status ('invited' or 'active')       │                              │
│  └──────────────────────────────────────┘                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Model Explanation

### 1. `auth.users` (Supabase Built-in)
**Where**: Supabase Dashboard → Authentication → Users  
**What**: Actual login accounts  
**Created via**: Supabase Dashboard (NOT SQL)

```
┌────────────────────────────────────────┐
│ auth.users (Managed by Supabase)       │
├────────────────────────────────────────┤
│ id: uuid                               │
│ email: admin@dra.com                   │
│ encrypted_password: ***                │
│ email_confirmed: true                  │
│ user_metadata: { role: "admin" }       │
└────────────────────────────────────────┘
```

### 2. `clients` (Your Business Entities)
**Where**: Your database → public.clients  
**What**: Stores/Companies being monitored  
**Example**: "My Shopify Store", "WooCommerce Store #1"

```sql
INSERT INTO clients (name, slug) VALUES ('My Store', 'my-store');
```

### 3. `user_clients` (The Linking Table)
**Where**: Your database → public.user_clients  
**What**: Links users to clients (RBAC)  
**Purpose**: Controls who can see what

```sql
-- Link admin user to a client
INSERT INTO user_clients (user_id, client_id, email, role, status)
VALUES (
    'uuid-from-auth-users',  -- From auth.users table
    1,                        -- From clients table
    'admin@dra.com',
    'admin',
    'active'
);
```

---

## Setup Steps

### Step 1: Run the Database Schema

1. Go to **Supabase Dashboard** → **SQL Editor**
2. Open **COMPUTE_SETUP.sql** (provided)
3. Click **Run**
4. This creates: clients, connectors, jobs, user_clients tables + RLS policies

### Step 2: Create Users in Supabase Auth

1. Go to **Authentication** → **Users**
2. Click **Add User** → **Create New User**

**Admin User:**
- Email: `admin@dra.com`
- Password: `AdminTest123!`
- Email confirmed: ✅ Check this

**Client User:**
- Email: `client@example.com`
- Password: `ClientTest123!`
- Email confirmed: ✅ Check this

### Step 3: Create a Client (Business Entity)

```sql
INSERT INTO public.clients (name, slug)
VALUES ('Test Store', 'test-store');
```

### Step 4: Link Users to Client

Get the UUIDs from auth.users first, then:

```sql
-- Replace the UUIDs with actual values from auth.users
INSERT INTO public.user_clients (user_id, client_id, email, role, status)
VALUES 
    ('admin-user-uuid-here', 1, 'admin@dra.com', 'admin', 'active'),
    ('client-user-uuid-here', 1, 'client@example.com', 'viewer', 'active');
```

---

## Quick Reference

### Where Things Live

| What | Where | How to Access |
|------|-------|---------------|
| User Accounts | `auth.users` | Supabase Dashboard → Authentication → Users |
| Business Clients | `public.clients` | Your database table |
| User-Client Links | `public.user_clients` | Your database table |
| API Credentials | `public.connectors` | Your database table |
| Reconciliation Jobs | `public.jobs` | Your database table |

### What Each Table Does

| Table | Purpose | Example Row |
|-------|---------|-------------|
| `clients` | A store being monitored | `{id: 1, name: "My Shopify", slug: "my-shopify"}` |
| `connectors` | API keys for that store | `{client_id: 1, type: "shopify", config_json: "..."}` |
| `jobs` | Reconciliation results | `{client_id: 1, status: "completed", result_summary: {...}}` |
| `user_clients` | Who can access what | `{user_id: "uuid", client_id: 1, role: "admin"}` |

---

## The Key Point

**`clients` ≠ user accounts**

- **`clients`** = Business entities (stores you monitor)
- **`auth.users`** = Login accounts (created in Supabase Auth)
- **`user_clients`** = Permission links between them

Think of it like this:
- **Client** = A company (e.g., "Nike")
- **User** = A person (e.g., "John the analyst")
- **User-Client Link** = "John works for Nike and can see their data"

---

## Troubleshooting

### "I don't see auth.users table"
It's a Supabase system table. Go to **Authentication** → **Users** in the sidebar.

### "User can't login"
1. Check user exists in **Authentication** → **Users**
2. Check email is confirmed (toggle is on)
3. Check password is correct

### "User can't see client data"
1. Check user exists in `auth.users`
2. Check `user_clients` table has a row linking that user_id to the client_id
3. Check `user_clients.status` = 'active'

### "Admin can't access admin panel"
Check the email domain matches the patterns in `middleware.ts`:
- `@dra.com`
- `@datarevolt.ro`
- `@revolt.agency`

---

## One-Liner Setup

Run this SQL in Supabase SQL Editor to create everything:

```sql
-- 1. Run COMPUTE_SETUP.sql to create tables
-- 2. Create users in Supabase Auth dashboard
-- 3. Insert a test client
INSERT INTO public.clients (name, slug) VALUES ('Test Store', 'test-store');
-- 4. Link users (get UUIDs from auth.users first)
```

Then login at http://localhost:3001/login
