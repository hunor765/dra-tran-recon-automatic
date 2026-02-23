# Admin UI Access Guide - Root Cause & Solutions

> **Issue**: Admin role is set in Supabase, but no admin UI is visible after login  
> **Status**: DIAGNOSED - Not a bug, missing navigation  
> **Last Updated**: 2026-02-23

---

## The Problem

After successfully setting the admin role in Supabase, you log in and see:
- ✅ The dashboard loads
- ✅ System status bar shows
- ❌ **NO "Add Client" button**
- ❌ **NO "Add Job" button**
- ❌ **NO Admin Panel link**

**What you're seeing**: The `/dashboard` page (client view)  
**What you need to see**: The `/admin` page (admin view)

---

## Root Cause Analysis

### 1. Two Separate Interfaces Exist

The app has TWO completely different UIs:

#### A) Client Dashboard (`/dashboard`)
- **URL**: `https://your-app.com/dashboard`
- **Purpose**: View reconciliation results for assigned clients
- **Features**: 
  - System status bar
  - Job results visualization
  - Historical data
  - "No Jobs Yet" message (when empty)
- **Theme**: Light/white background

#### B) Admin Panel (`/admin`)
- **URL**: `https://your-app.com/admin`
- **Purpose**: Manage clients, users, jobs, system settings
- **Features**:
  - **Sidebar navigation**: Dashboard, Clients, Jobs, Users, Analytics, Settings
  - **"Add Client" button** (in `/admin/clients`)
  - **Job management** (in `/admin/jobs`)
  - **User management** (in `/admin/users`)
  - Dark theme UI

### 2. The Missing Link

**Critical Finding**: There is **NO navigation link** from the client dashboard to the admin panel!

From `/admin` → `/dashboard`: ✅ "Back to Dashboard" link exists  
From `/dashboard` → `/admin`: ❌ No "Admin Panel" link exists

### 3. After Login Behavior

When you log in:
1. Supabase authenticates successfully
2. Middleware checks if you're admin
3. **Redirects to `/dashboard`** (default for all users)
4. You're stuck on client view with no way to access admin

---

## Immediate Solutions (No Code Changes)

### Solution 1: Manual URL Navigation (Quickest)

Simply type the admin URL in your browser:

```
https://your-app.com/admin
```

Or if running locally:
```
http://localhost:3000/admin
```

**You should see**:
- Dark-themed interface
- Left sidebar with: Dashboard, Clients, Jobs, Users, Analytics, Settings
- "DRA Admin" logo

### Solution 2: Check Your Current URL

If you're on:
- `/dashboard` → You're on client view (light theme, no admin controls)
- `/admin` → You're on admin view (dark theme, full controls)

### Solution 3: First-Time Admin Setup Steps

Once you access `/admin`, here's what to do:

1. **Navigate to `/admin/clients`**
   - Click "Clients" in left sidebar
   - Click "Add Client" button
   - Create your first client (e.g., "Test Store")

2. **Navigate to `/admin/clients/[id]/connectors`**
   - Click on the client you just created
   - Click "Connectors" tab
   - Add GA4 connector
   - Add Shopify/WooCommerce connector

3. **Navigate to `/admin/jobs`**
   - Click "Jobs" in sidebar
   - Run a reconciliation job

---

## Code Changes (Permanent Fix)

To add proper admin navigation, you need to modify these files:

### 1. Add "Admin Panel" Link to Dashboard

**File**: `apps/platform/frontend/src/app/dashboard/layout.tsx` or `dashboard/page.tsx`

Add a button/link in the dashboard header that only shows for admins:

```tsx
// In dashboard layout or page, add this to the header area:
import { useUser } from '@/lib/hooks/useUser' // or however you get user data

// ...

const { user } = useUser() // Get current user
const isAdmin = user?.role === 'admin' // Check if admin

// In the JSX, add:
{isAdmin && (
  <Link href="/admin">
    <Button variant="outline" size="sm">
      Admin Panel
    </Button>
  </Link>
)}
```

### 2. Redirect Admins to /admin on Login

**File**: `apps/platform/frontend/middleware.ts`

Update the middleware to redirect admins to `/admin` instead of `/dashboard`:

```typescript
// Current behavior (around line 70):
return response // Allows access to requested page

// New behavior - redirect admins to admin dashboard:
if (isAdmin && pathname === '/dashboard') {
  return NextResponse.redirect(new URL('/admin', request.url))
}
```

### 3. Add Admin Link to Navigation Menu

**File**: `apps/platform/frontend/src/app/dashboard/layout.tsx`

Add an "Admin" link to the dashboard navigation if user is admin.

---

## File Structure Reference

```
apps/platform/frontend/src/app/
├── admin/                          # Admin Panel (dark theme)
│   ├── page.tsx                   # Admin dashboard stats
│   ├── layout.tsx                 # Admin sidebar navigation
│   ├── clients/
│   │   ├── page.tsx              # List clients + "Add Client" button
│   │   └── [id]/
│   │       ├── page.tsx          # Client details
│   │       ├── connectors/       # Manage connectors
│   │       └── users/            # Manage client users
│   ├── jobs/
│   │   └── page.tsx              # All jobs + run new job
│   └── users/
│       └── page.tsx              # User management
│
└── dashboard/                      # Client Dashboard (light theme)
    ├── page.tsx                   # Shows job results/status
    ├── layout.tsx                 # Dashboard layout
    └── history/                   # Job history
```

---

## Verification Checklist

After navigating to `/admin`:

- [ ] Dark-themed interface loads
- [ ] Left sidebar shows: Dashboard, Clients, Jobs, Users, Analytics, Settings
- [ ] "DRA Admin" logo visible
- [ ] `/admin/clients` shows "Add Client" button
- [ ] `/admin/jobs` shows job management interface
- [ ] Can create a new client
- [ ] Can add connectors to a client
- [ ] Can run a reconciliation job

---

## Common Issues

### Issue: "Access Denied" when accessing /admin

**Cause**: Middleware still checking old email patterns OR role not detected  
**Fix**: 
1. Check browser console for auth errors
2. Verify `app_metadata.role = "admin"` is set correctly
3. Log out and log back in (to refresh JWT token)

### Issue: /admin shows blank page

**Cause**: API calls failing (401 errors)  
**Fix**: 
1. Check `/debug` page - Token Validation should show `role: "admin"`
2. If not, the JWT token wasn't refreshed after role change
3. Clear browser cookies/cache and login again

### Issue: "Add Client" button doesn't work

**Cause**: API endpoint might require additional permissions  
**Fix**:
1. Check browser console for API errors
2. Verify `user_clients` table has entry linking your user to a client
3. Check if backend logs show permission errors

---

## Backend API Endpoints for Admin

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/admin/stats` | GET | Admin dashboard statistics |
| `/api/v1/clients/` | GET | List all clients |
| `/api/v1/clients/` | POST | Create new client |
| `/api/v1/clients/{id}` | PUT | Update client |
| `/api/v1/clients/{id}` | DELETE | Delete client |
| `/api/v1/jobs/` | GET | List all jobs |
| `/api/v1/jobs/run/{client_id}` | POST | Trigger reconciliation job |

---

## Summary

**The admin UI exists and works** - you just need to navigate to `/admin` manually.

**Quick Fix**: Type `/admin` in your URL bar  
**Proper Fix**: Add navigation link from dashboard to admin panel

The app architecture separates client and admin views intentionally, but the navigation between them is incomplete.

---

*Document for reference - no code changes required unless you want to add permanent navigation.*
