# PLAN-supabase-connect.md - Connect to Supabase

> **Goal:** Securely connect the local DRA Platform to your prod/dev Supabase project.

## Phase 1: Preparation (User Actions)
**Objective:** Gather necessary credentials from your Supabase Dashboard.

- [ ] **1.1. Gather Credentials**
    - [ ] **Project URL**: Found in Settings -> API | url: https://wwvhozhsdloceptyibhx.supabase.co
    - [ ] **Anon Key (Public)**: Found in Settings -> API | anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3dmhvemhzZGxvY2VwdHlpYmh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkyNTk2MzIsImV4cCI6MjA4NDgzNTYzMn0.9DzURBOHvElPIsaNLCYXl8QEjbZW2WB6ZYvuymHJ-T0
    - [ ] **Service Role Key (Secret)**: Found in Settings -> API (Used by Backend) | service key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3dmhvemhzZGxvY2VwdHlpYmh4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTI1OTYzMiwiZXhwIjoyMDg0ODM1NjMyfQ.6nEtXWXNIFYgalWAFZx6n5XTT3eGnBv6YdPtbMiH0ug
    - [ ] **Database Connection String**: Found in Settings -> Database -> Connection String (Mode: Transaction or Session) | connection string: postgresql://postgres.wwvhozhsdloceptyibhx:[iBrgnH7MSQ!]@aws-1-eu-west-1.pooler.supabase.com:5432/postgres
        - *Format:* `postgres://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`
    - [ ] **DB Password**: The one you set when creating the project. | password: iBrgnH7MSQ!

## Phase 2: Configuration Updates
**Objective:** Update local environment files with real credentials.

- [ ] **2.1. Backend Configuration**
    - [ ] Update `dra-platform/backend/core/config.py` (or create `.env`)
    - [ ] Set `DATABASE_URL` to the Supabase Connection String.
- [ ] **2.2. Frontend Configuration**
    - [ ] Create `dra-platform/frontend/.env.local`
    - [ ] Set `NEXT_PUBLIC_SUPABASE_URL`
    - [ ] Set `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## Phase 3: Schema Migration
**Objective:** Push the local schema design to the remote database.

- [ ] **3.1. Database Migration**
    - [ ] Connect to Supabase using a SQL client (TablePlus, DBeaver) or the Supabase SQL Editor.
    - [ ] Run the contents of `dra-platform/database/schema.sql`.
    - [ ] Verify tables `clients`, `connectors`, `jobs` are created.

## Phase 4: Verification
**Objective:** Test the full connection flow.

- [ ] **4.1. Test Backend Connection**
    - [ ] Start backend (`uvicorn`)
    - [ ] Check logs for successful DB connection.
- [ ] **4.2. Test Frontend Connection**
    - [ ] Start frontend.
    - [ ] Verify Supabase Auth works (Sign Up/Login).

---

## Agent Assignments
- `backend-specialist`: Phase 2.1 (Config update)
- `frontend-specialist`: Phase 2.2 (Env setup)
- `database-architect`: Phase 3 (Migration assistance)

---

## What I Need From You (User)

To proceed with **Step 2 (Configuration Updates)**, I need you to provide the following values (you can paste them here, I'll put them in `.env` files for you):

1.  **DATABASE_URL**: `postgres://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`
2.  **NEXT_PUBLIC_SUPABASE_URL**: `https://wwvhozhsdloceptyibhx.supabase.co`
3.  **NEXT_PUBLIC_SUPABASE_ANON_KEY**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3dmhvemhzZGxvY2VwdHlpYmh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkyNTk2MzIsImV4cCI6MjA4NDgzNTYzMn0.9DzURBOHvElPIsaNLCYXl8QEjbZW2WB6ZYvuymHJ-T0`

*Note: I do NOT need the Service Role Key yet unless we implement admin-only backend features right now.*
