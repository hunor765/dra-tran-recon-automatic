# DRA Platform - Test Accounts Setup

## Test Account Credentials

### Admin Account
```
Email: admin@dra.com
Password: AdminTest123!
Role: Administrator
Access: Full admin panel access
```

### Client Account
```
Email: client@example.com
Password: ClientTest123!
Role: Client Viewer
Access: Dashboard only, can view their reconciliation data
```

---

## How to Create These Accounts

### Option 1: Via Supabase Dashboard (Recommended)

1. Go to https://supabase.com/dashboard
2. Sign in with your account
3. Select project: `wwvhozhsdloceptyibhx`
4. Go to **Authentication** → **Users**
5. Click **Add User** → **Create New User**

**Create Admin User:**
- Email: `admin@dra.com`
- Password: `AdminTest123!`
- Email confirmed: ✅ (check this box)

**Create Client User:**
- Email: `client@example.com`
- Password: `ClientTest123!`
- Email confirmed: ✅ (check this box)

### Option 2: Via SQL (if you have DB access)

```sql
-- Create admin user (will need to set password via auth)
-- This is handled by Supabase Auth, use the dashboard instead
```

---

## After Creating Accounts

### Step 1: Create a Client in Admin Panel
1. Login as `admin@dra.com`
2. Go to **Clients** → **Add Client**
3. Create a test client:
   - Name: "Test Store"
   - Slug: "test-store"

### Step 2: Link Client User to Client
1. Go to the client detail page
2. Click **Users** tab
3. Click **Invite User**
4. Enter: `client@example.com`
5. Role: `viewer`

### Step 3: Add Connectors (see API_INTEGRATION_GUIDE.md)

---

## Login URLs

- **Admin Panel**: http://localhost:3000/login → Select "Admin Login"
- **Client Dashboard**: http://localhost:3000/login → Select "Client Login (OTP)"

