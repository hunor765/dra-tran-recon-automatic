# PLAN-secure-otp-auth.md - Secure Client OTP Login

> **Goal:** implement secure Passwordless (OTP/Magic Link) authentication for clients with RBAC linking users to specific clients.

## Phase 1: Database Schema (RBAC)
**Objective:** Link Supabase Users to Clients.

- [ ] **1.1. Create `user_clients` Table**
    - [ ] Columns: `id`, `email` (Unique per client), `client_id` (FK), `role` (admin/viewer), `created_at`.
    - [ ] *Why Email?* Allows mapping *before* the user actually signs up (Invitation style).
    - [ ] Enable RLS Policy: Users can only read rows matching their `auth.email()`.

## Phase 2: User Invite Flow (Admin)
**Objective:** Allow Admins to invite users to a specific client.

- [ ] **2.1. Update Client Details Page** (`/admin/clients/[id]`)
    - [ ] Add "Users" tab/section.
    - [ ] Add "Invite User" button.
- [ ] **2.2. Implement Invite Logic**
    - [ ] Add row to `user_clients`.
    - [ ] (Optional for MVP): Trigger Supabase Admin Invite API to send the actual email, OR just tell the admin "Tell them to log in with this email".
    - [ ] *Implementation:* We'll rely on the standard "Sign In" flow initiating the email sequence for simplicity first.

## Phase 3: Login UX Update
**Objective:** Support OTP Login flow.

- [ ] **3.1. Update Login Page** (`/login`)
    - [ ] Add Switch: "Password Login" (Admin) vs "Send Magic Link" (Client).
    - [ ] Implement `supabase.auth.signInWithOtp({ email })`.
    - [ ] Add "Verify OTP" UI state (Enter 6-digit code).

## Phase 4: Authorization & Routing
**Objective:** Ensure logged-in users see THEIR data.

- [ ] **4.1. Middleware Update**
    - [ ] Check if user is Admin (by email domain or specific flag) -> `/admin`.
    - [ ] If Client User -> Check `user_clients` table for valid mapping.
    - [ ] Redirect to `/dashboard`.
- [ ] **4.2. Dashboard Interaction**
    - [ ] Update `createClient()` usage to filter data by the `client_id` retrieved from `user_clients` mapping (RLS simulation or explicit query filter).

---

## Agent Assignments
- `database-architect`: Phase 1 (Schema).
- `frontend-specialist`: Phase 2 & 3 (UI).
- `backend-specialist`: Phase 4 (Middleware & Data Logic).
