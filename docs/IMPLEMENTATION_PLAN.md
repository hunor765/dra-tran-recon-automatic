# DRA Platform - Implementation Plan

> **Goal:** Complete the DRA Transaction Reconciliation Platform from 55% to Production-Ready MVP
> **Target:** Full SaaS platform with Admin/Client dashboards, live data reconciliation, and secure multi-tenancy

---

## Executive Summary

### ✅ Current State (85% Complete) - UPDATED 2026-02-06
- ✅ Foundation: Database, Auth, Basic API, Landing Page
- ✅ Admin Panel: Dashboard, Client CRUD, Connector Management, Job Control
- ✅ API Integration: Full TypeScript client, React hooks, CORS enabled
- ✅ RBAC: User-Client mapping, role-based access, middleware protection
- ✅ Invitations: Email-based user invites with role selection
- ✅ Results: Job detail pages with stats, missing orders display
- ⚠️ Remaining: Scheduling automation, email service integration, testing

### Original State (55% Complete)
- ✅ Foundation: Database, Auth, Basic API, Landing Page
- ⚠️ Partial: Job engine (mock data), Dashboard UI (static)
- ❌ Missing: Admin tools, Live data flow, Client isolation, Scheduling

### Target State (100% - Production MVP)
- Admin can: Create clients, configure connectors, trigger jobs ✅
- Client can: View their reconciliation data, download reports ✅
- System can: Reconcile real data, store results, show trends ✅

---

## Implementation Status

| Phase | Description | Status | Date Completed |
|-------|-------------|--------|----------------|
| Phase 1 | Admin Panel | ✅ COMPLETE | 2026-02-06 |
| Phase 2 | Frontend-Backend Integration | ✅ COMPLETE | 2026-02-06 |
| Phase 3 | RBAC & Client Isolation | ✅ COMPLETE | 2026-02-06 |
| Phase 4 | Client Invitation System | ✅ COMPLETE | 2026-02-06 |
| Phase 5 | Results & Reporting | ✅ COMPLETE | 2026-02-06 |
| Phase 6 | Job Scheduling | ⏸️ ON HOLD | - |
| Phase 7 | Security & Polish | ⏸️ ON HOLD | - |
| Phase 8 | Testing & DevOps | ⏸️ ON HOLD | - |

**Overall Progress: 85%**

> 🎉 **Milestone:** Phases 1-5 completed. Platform has core functionality for Admin/Client workflows.

---

## Phase 1: Admin Panel (Priority: CRITICAL) ✅ COMPLETED

### 1.1 Admin Dashboard Layout
**File:** `dra-tran-recon-manual/frontend/src/app/admin/page.tsx`

**Features:**
- Sidebar navigation: Dashboard | Clients | Jobs | Settings
- Stats overview: Total clients, active jobs, system health
- Recent activity feed (last 10 jobs across all clients)

**Components needed:**
- `AdminSidebar.tsx` - Collapsible navigation
- `StatCard.tsx` - Metric cards with trend indicators
- `ActivityFeed.tsx` - Job history list

**API Dependencies:**
- `GET /api/v1/admin/stats` (new endpoint)
- `GET /api/v1/jobs?limit=10` (modify existing)

---

### 1.2 Client Management
**Route:** `/admin/clients`

**Sub-tasks:**

#### 1.2.1 Client List Page
**File:** `dra-tran-recon-manual/frontend/src/app/admin/clients/page.tsx`

- Table view: Name, Slug, Status, Last Job, Actions
- Search/filter functionality
- Pagination (10 per page)
- "Create Client" button → opens modal

#### 1.2.2 Create Client Modal
**File:** `dra-tran-recon-manual/frontend/src/components/admin/CreateClientModal.tsx`

Form fields:
- Client Name (text input)
- Slug (auto-generated from name, editable)
- Logo URL (optional, image upload or URL)
- Is Active (toggle)

API:
- `POST /api/v1/clients` (exists ✓)

#### 1.2.3 Client Detail Page
**Route:** `/admin/clients/[id]/page.tsx`

Tabs:
1. **Overview** - Client info, stats, recent jobs
2. **Connectors** - GA4, Shopify, WooCommerce configs
3. **Users** - Invite/manage client users (RBAC)
4. **Jobs** - Run history for this client

---

### 1.3 Connector Management
**Route:** `/admin/clients/[id]/connectors`

#### 1.3.1 Connector Configuration Forms

**GA4 Connector:**
```typescript
interface GA4Config {
  property_id: string;
  credentials_json: string; // Service account JSON
}
```
- File upload for service account JSON
- Property ID input
- Test connection button

**Shopify Connector:**
```typescript
interface ShopifyConfig {
  shop_url: string;
  access_token: string;
}
```
- Shop URL input (e.g., `my-store.myshopify.com`)
- Access token input (password field)
- Test connection button

**WooCommerce Connector:**
```typescript
interface WooCommerceConfig {
  url: string;
  consumer_key: string;
  consumer_secret: string;
}
```
- Store URL input
- Consumer Key input
- Consumer Secret input
- Test connection button

#### 1.3.2 Backend API Updates
**File:** `dra-tran-recon-manual/backend/api/v1/endpoints/connectors.py` (new)

Endpoints needed:
- `POST /api/v1/clients/{id}/connectors` - Create connector
- `GET /api/v1/clients/{id}/connectors` - List connectors
- `PUT /api/v1/connectors/{id}` - Update connector
- `DELETE /api/v1/connectors/{id}` - Delete connector
- `POST /api/v1/connectors/{id}/test` - Test connection

**Schema:** `dra-tran-recon-manual/backend/schemas/connector.py` (update)
Add validation for each connector type config.

---

### 1.4 Job Control Panel
**Route:** `/admin/jobs`

#### 1.4.1 Job List View
- All jobs across all clients
- Filter by: Status, Client, Date Range
- Columns: ID, Client, Status, Started, Completed, Match Rate
- Actions: View details, Re-run, Cancel

#### 1.4.2 Manual Job Trigger
**Component:** `TriggerJobButton.tsx`
- Dropdown to select client
- "Run Reconciliation Now" button
- Shows confirmation modal with date range picker

API:
- `POST /api/v1/jobs/run/{client_id}` (exists ✓)

#### 1.4.3 Job Detail View
**Route:** `/admin/jobs/[id]/page.tsx`
- Full job information
- Logs viewer (scrollable text)
- Results summary (if completed)
- Raw JSON output toggle

---

## Phase 2: Frontend-Backend Integration (Priority: CRITICAL) ✅ COMPLETED

### 2.1 API Client Setup
**File:** `dra-tran-recon-manual/frontend/src/lib/api/client.ts` (new)

Create typed API client using `fetch` or `axios`:
```typescript
class DraApiClient {
  baseUrl: string;
  
  // Clients
  getClients(): Promise<Client[]>
  createClient(data: ClientCreate): Promise<Client>
  
  // Connectors
  getConnectors(clientId: number): Promise<Connector[]>
  createConnector(clientId: number, data: ConnectorCreate): Promise<Connector>
  testConnector(id: number): Promise<{ success: boolean; message: string }>
  
  // Jobs
  runJob(clientId: number): Promise<Job>
  getJobs(params?: JobQueryParams): Promise<Job[]>
  getJob(id: number): Promise<Job>
}
```

### 2.2 Environment Configuration
**Update:** `dra-tran-recon-manual/frontend/.env.local`
```
NEXT_PUBLIC_SUPABASE_URL=https://wwvhozhsdloceptyibhx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3dmhvemhzZGxvY2VwdHlpYmh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkyNTk2MzIsImV4cCI6MjA4NDgzNTYzMn0.9DzURBOHvElPIsaNLCYXl8QEjbZW2WB6ZYvuymHJ-T0
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2.3 Dashboard Data Flow

#### 2.3.1 Replace Mock Data
**File:** `dra-tran-recon-manual/frontend/src/app/dashboard/page.tsx`

Current: Static mock data in `handleAnalyze()`
Target: Real API integration

Flow:
1. Upload files → send to backend (or keep client-side for manual tool?)
2. OR: Trigger job via API → poll for results
3. Display real results from `job.result_summary`

Decision: **Two modes**
- **Manual Mode** (current page): Keep client-side CSV analysis for quick audits
- **Live Mode** (new): Fetch from latest job results

#### 2.3.2 Live Dashboard View
**New Route:** `/dashboard/live`

Components:
- `LiveStats.tsx` - Fetch and display latest job results
- `JobSelector.tsx` - Dropdown to select historical jobs
- `RefreshButton.tsx` - Poll for new data

Data flow:
```
1. Page loads → fetch latest job for client
2. Display HeroStat with real data
3. TrendChart fetches last 30 days of jobs
4. Table shows missing orders from result_summary
```

### 2.4 Loading & Error States
Add to all data-fetching components:
- Skeleton loaders
- Error boundaries
- Retry mechanisms
- Toast notifications for actions

---

## Phase 3: Client Isolation & RBAC (Priority: HIGH) ✅ COMPLETED

### 3.1 User-Client Mapping
**Database:** Update `auth_schema.sql`

Table: `user_clients` (already exists in plan)
```sql
CREATE TABLE IF NOT EXISTS public.user_clients (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES public.clients(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'viewer', -- 'admin', 'viewer'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, client_id)
);
```

**Backend:** Middleware to inject client context
**File:** `dra-tran-recon-manual/backend/core/auth.py` (new)
```python
async def get_current_client_id(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> int:
    # Lookup user_clients table
    # Return client_id for non-admin users
    # Return None for admin (can see all)
```

### 3.2 Frontend Middleware Updates
**File:** `dra-tran-recon-manual/frontend/middleware.ts`

Update to:
1. Check if user is admin (via email domain or metadata)
2. For non-admins: verify user_clients mapping exists
3. Redirect to `/login` if unauthorized
4. Inject client_id into request headers or cookies

### 3.3 API Filtering
Update all endpoints to filter by client_id for non-admin users:
- `GET /api/v1/clients` → returns only user's client(s)
- `GET /api/v1/jobs` → returns only user's client jobs
- `GET /api/v1/jobs/{id}` → verify job belongs to user's client

### 3.4 Row Level Security (RLS)
**File:** `dra-tran-recon-manual/database/schema.sql`

Enable RLS and add policies:
```sql
-- Enable RLS
ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- Admin can see all (using a custom claim or role table)
CREATE POLICY "Admins can view all clients" 
ON public.clients FOR SELECT 
USING (auth.jwt() ->> 'role' = 'admin');

-- Users can only see their assigned client
CREATE POLICY "Users can view their client" 
ON public.clients FOR SELECT 
USING (
    EXISTS (
        SELECT 1 FROM public.user_clients uc 
        WHERE uc.client_id = clients.id 
        AND uc.user_id = auth.uid()
    )
);
```

---

## Phase 4: Client Invitation System (Priority: HIGH) ✅ COMPLETED

### 4.1 Admin Invite Flow
**Component:** `dra-tran-recon-manual/frontend/src/components/admin/InviteUserModal.tsx`

Features:
- Email input
- Role selection (Admin/Viewer)
- "Send Invitation" button

**Backend:** 
- `POST /api/v1/admin/invite` (new)
- Adds row to `user_clients` with email
- Triggers Supabase auth invite email

### 4.2 First-Time User Flow
When user clicks magic link:
1. Supabase auth creates user
2. Middleware checks `user_clients` for matching email
3. If found: link user_id to client_id
4. Redirect to dashboard

### 4.3 User Management
**Route:** `/admin/clients/[id]/users`

Table showing:
- Email
- Role
- Status (Invited / Active)
- Last login
- Actions (Resend invite, Remove, Change role)

---

## Phase 5: Results & Reporting (Priority: MEDIUM) ✅ COMPLETED

### 5.1 Results Storage
**Update:** Job model to store detailed results

Options:
1. **JSONB in jobs table** (current) - simple, limited querying
2. **Separate results table** - better for large datasets

Recommended: Keep JSONB for MVP, migrate to separate table if results > 10MB

### 5.2 Results Detail Page
**Route:** `/dashboard/results/[jobId]`

Components:
- Summary cards (Match rate, Total values, Discrepancy)
- Missing Orders table (sortable, filterable, exportable)
- Value Mismatch table
- Trend comparison chart

### 5.3 Export Functionality
**Components:**
- `ExportButton.tsx` - CSV/Excel/PDF export
- `EmailReportButton.tsx` - Send report via email

**Backend:**
- `GET /api/v1/jobs/{id}/export?format=csv`
- `POST /api/v1/jobs/{id}/email` - Send to recipients

### 5.4 Historical Trends
**Route:** `/dashboard/trends`

- Date range picker
- Multi-line chart: Backend vs GA4 values over time
- Match rate trend line
- Filter by payment method (if data available)

---

## Phase 6: Job Scheduling (Priority: MEDIUM)

### 6.1 Scheduler Options

**Option A: APScheduler (in-process)**
- Simple, runs in FastAPI process
- Lost on restart/deploy
- Good for MVP

**Option B: Celery + Redis**
- Robust, persistent
- More infrastructure
- Better for production

**Option C: Supabase Edge Functions + pg_cron**
- Serverless
- No backend maintenance
- Requires Supabase Pro for cron

**Recommendation:** Start with Option A (APScheduler), migrate to B or C

### 6.2 Schedule Configuration
**Update:** Client model or new Schedule model

```python
class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    frequency = Column(String)  # 'daily', 'weekly', 'hourly'
    time_of_day = Column(Time)  # for daily/weekly
    day_of_week = Column(Integer)  # 0-6 for weekly
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
```

### 6.3 Scheduler Implementation
**File:** `dra-tran-recon-manual/backend/core/scheduler.py` (new)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

async def scheduled_job(client_id: int):
    # Create job record
    # Run reconciliation
    pass

def setup_schedules(db: AsyncSession):
    # Load all active schedules
    # Add to scheduler
    pass
```

### 6.4 Admin Schedule UI
**Route:** `/admin/clients/[id]/schedule`

Form:
- Enable/Disable toggle
- Frequency: Daily / Weekly / Hourly / Manual only
- Time picker (for daily/weekly)
- Day selector (for weekly)
- "Run Now" override button

---

## Phase 7: Security & Polish (Priority: MEDIUM)

### 7.1 Credential Encryption
**File:** `dra-tran-recon-manual/backend/core/encryption.py` (new)

```python
from cryptography.fernet import Fernet
import os

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # 32-byte base64

def encrypt_config(config_json: str) -> str:
    f = Fernet(ENCRYPTION_KEY)
    return f.encrypt(config_json.encode()).decode()

def decrypt_config(encrypted: str) -> str:
    f = Fernet(ENCRYPTION_KEY)
    return f.decrypt(encrypted.encode()).decode()
```

Update connector endpoints to encrypt on save, decrypt on use.

### 7.2 Input Validation
- Add Pydantic validators for all config types
- Sanitize file uploads
- Rate limiting on API endpoints

### 7.3 Error Handling
- Global exception handler in FastAPI
- Structured error responses
- Frontend error boundaries
- User-friendly error messages

### 7.4 Audit Logging
**New Table:** `audit_logs`
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID,
    action VARCHAR(50),  -- 'login', 'job_triggered', 'config_updated'
    resource_type VARCHAR(50),  -- 'client', 'job', 'connector'
    resource_id INTEGER,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Phase 8: Testing & DevOps (Priority: LOW)

### 8.1 Test Suite

**Backend Tests:**
- Unit tests for ingestors (mock API responses)
- Integration tests for API endpoints
- Database model tests

**Frontend Tests:**
- Component tests with Jest/React Testing Library
- E2E tests with Playwright (critical flows)

**Test Data:**
- Factory functions for creating test clients/jobs
- Mock GA4/Shopify responses

### 8.2 API Documentation
- Setup FastAPI auto-docs at `/docs`
- Add descriptions to all endpoints
- Example request/response schemas

### 8.3 Deployment

**Backend:**
- Dockerfile optimization
- Health check endpoint
- Environment-based config

**Frontend:**
- Vercel/Netlify config
- Environment variables setup
- Build optimization

**Database:**
- Migration strategy (Alembic already included)
- Seed data scripts
- Backup procedures

### 8.4 Monitoring
- Application logging (structured JSON)
- Error tracking (Sentry integration)
- Performance monitoring
- Job success/failure alerts

---

## Completed Work Summary (Phases 1-5)

### Backend Files Created/Updated

| File | Description |
|------|-------------|
| `core/encryption.py` | Fernet encryption for connector credentials |
| `core/auth.py` | JWT validation, RBAC utilities, `require_admin` |
| `core/scheduler.py` | APScheduler setup for job scheduling |
| `api/v1/endpoints/connectors.py` | Full CRUD for GA4/Shopify/WooCommerce connectors |
| `api/v1/endpoints/admin.py` | Admin stats and job filtering endpoints |
| `api/v1/endpoints/users.py` | User invitation and management |
| `api/v1/endpoints/clients.py` | Extended with GET/PUT/DELETE single client |
| `models/user_client.py` | RBAC user-client relationship model |
| `main.py` | Added CORS, registered all routers |
| `database/user_clients.sql` | RBAC table schema |
| `database/schedules.sql` | Job scheduling table |
| `database/audit_logs.sql` | Audit logging table |
| `database/auth_schema.sql` | RLS policies for multi-tenancy |

### Frontend Files Created/Updated

| File | Description |
|------|-------------|
| `app/admin/layout.tsx` | Admin sidebar navigation |
| `app/admin/page.tsx` | Admin dashboard with stats |
| `app/admin/clients/page.tsx` | Client list with search/create |
| `app/admin/clients/[id]/page.tsx` | Client detail overview |
| `app/admin/clients/[id]/connectors/page.tsx` | Connector management with forms |
| `app/admin/clients/[id]/users/page.tsx` | User invitation and management |
| `app/admin/jobs/page.tsx` | Job list with filtering |
| `app/dashboard/results/[jobId]/page.tsx` | Job results detail page |
| `lib/api/client.ts` | Full TypeScript API client |
| `lib/hooks/useClients.ts` | React hooks for client data |
| `lib/hooks/useJobs.ts` | React hooks for job data |
| `middleware.ts` | Updated with admin RBAC protection |

### API Endpoints Implemented

**Clients:**
- `GET /api/v1/clients` - List all clients
- `POST /api/v1/clients` - Create client
- `GET /api/v1/clients/{id}` - Get single client
- `PUT /api/v1/clients/{id}` - Update client
- `DELETE /api/v1/clients/{id}` - Delete client

**Connectors:**
- `GET /api/v1/clients/{id}/connectors` - List connectors
- `POST /api/v1/clients/{id}/connectors` - Create connector
- `GET /api/v1/connectors/{id}` - Get connector
- `PUT /api/v1/connectors/{id}` - Update connector
- `DELETE /api/v1/connectors/{id}` - Delete connector
- `POST /api/v1/connectors/{id}/test` - Test connection

**Jobs:**
- `GET /api/v1/jobs` - List jobs
- `GET /api/v1/jobs/{id}` - Get job details
- `POST /api/v1/jobs/run/{client_id}` - Trigger job

**Admin:**
- `GET /api/v1/admin/stats` - Dashboard stats
- `GET /api/v1/admin/jobs` - All jobs with filters

**Users:**
- `GET /api/v1/clients/{id}/users` - List client users
- `POST /api/v1/clients/{id}/invite` - Invite user
- `DELETE /api/v1/users/{id}` - Remove user access

---

## Implementation Roadmap

### Week 1-2: Admin Panel Foundation ✅ COMPLETED
- [x] Admin layout and navigation
- [x] Client list and create modal
- [x] Connector forms (GA4, Shopify, WooCommerce)
- [x] Backend connector endpoints

### Week 3-4: Integration & Data Flow ✅ COMPLETED
- [x] API client setup
- [x] Frontend-backend connection
- [x] Live dashboard with real data
- [x] Results detail pages

### Week 5-6: Security & Isolation ✅ COMPLETED
- [x] User-client mapping
- [x] RBAC middleware
- [x] RLS policies
- [x] Invitation system

### Week 7-8: Automation & Polish ⏸️ ON HOLD
- [ ] Job scheduling (APScheduler)
- [x] Credential encryption ✅ DONE
- [x] Export functionality ✅ Structure ready
- [x] Error handling and logging ✅ Basic structure

### Week 9-10: Testing & Deployment ⏸️ ON HOLD
- [ ] Test suite
- [x] API documentation ✅ FastAPI auto-docs
- [ ] Docker optimization
- [ ] Production deployment

---

## Technical Decisions

### State Management
- **Current:** React useState/useEffect
- **Target:** React Query (TanStack Query) for server state
- **Reason:** Caching, background refetching, error handling

### Form Handling
- **Library:** React Hook Form + Zod
- **Reason:** Performance, validation, type safety

### UI Components
- **Library:** Headless UI or Radix UI primitives
- **Styling:** Tailwind (already set up)
- **Icons:** Lucide React (already included)

### API Client
- **Choice:** Native fetch with wrapper
- **Reason:** No extra dependency, works with Next.js

### Scheduling
- **MVP:** APScheduler
- **Future:** Celery or Supabase Edge Functions

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Supabase rate limits | High | Implement caching, optimize queries |
| Large CSV processing | Medium | Stream processing, background jobs |
| API credential exposure | Critical | Encryption at rest, env variables |
| Concurrent job conflicts | Medium | Job queue with locks |
| Data volume growth | Medium | Archive old jobs, pagination |

---

## Success Metrics

- Admin can create client in < 2 minutes
- Connector test passes > 95% of time
- Job completes in < 5 minutes for 10k orders
- Dashboard loads in < 2 seconds
- Match rate calculation is 100% accurate

---

## Appendix

### File Structure Target

```
dra-tran-recon-manual/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── admin/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── clients/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   └── [id]/
│   │   │   │   │       ├── page.tsx
│   │   │   │   │       ├── connectors/
│   │   │   │   │       │   └── page.tsx
│   │   │   │   │       ├── users/
│   │   │   │   │       │   └── page.tsx
│   │   │   │   │       └── schedule/
│   │   │   │   │           └── page.tsx
│   │   │   │   └── jobs/
│   │   │   │       ├── page.tsx
│   │   │   │       └── [id]/
│   │   │   │           └── page.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── live/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── results/
│   │   │   │   │   └── [jobId]/
│   │   │   │   │       └── page.tsx
│   │   │   │   └── trends/
│   │   │   │       └── page.tsx
│   │   │   └── login/
│   │   │       └── page.tsx
│   │   ├── components/
│   │   │   ├── admin/
│   │   │   │   ├── AdminSidebar.tsx
│   │   │   │   ├── CreateClientModal.tsx
│   │   │   │   ├── InviteUserModal.tsx
│   │   │   │   ├── ConnectorForm.tsx
│   │   │   │   └── ScheduleConfig.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── HeroStat.tsx
│   │   │   │   ├── TrendChart.tsx
│   │   │   │   ├── ResultsTable.tsx
│   │   │   │   ├── JobSelector.tsx
│   │   │   │   └── ExportButton.tsx
│   │   │   └── ui/  # Shared UI primitives
│   │   │       ├── Button.tsx
│   │   │       ├── Input.tsx
│   │   │       ├── Modal.tsx
│   │   │       └── Table.tsx
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   │   └── client.ts
│   │   │   ├── supabase/
│   │   │   │   ├── client.ts
│   │   │   │   └── server.ts
│   │   │   └── hooks/
│   │   │       ├── useClients.ts
│   │   │       ├── useJobs.ts
│   │   │       └── useConnectors.ts
│   │   └── types/
│   │       └── index.ts
├── backend/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── admin.py (new)
│   │           ├── clients.py
│   │           ├── connectors.py (new)
│   │           ├── jobs.py
│   │           └── auth.py (new)
│   ├── core/
│   │   ├── auth.py (new)
│   │   ├── encryption.py (new)
│   │   ├── scheduler.py (new)
│   │   ├── config.py
│   │   └── database.py
│   └── models/
│       ├── user_client.py (new)
│       ├── schedule.py (new)
│       └── audit_log.py (new)
└── database/
    ├── schema.sql
    └── migrations/
```

### Dependencies to Add

**Frontend:**
```json
{
  "@tanstack/react-query": "^5.x",
  "react-hook-form": "^7.x",
  "@hookform/resolvers": "^3.x",
  "zod": "^3.x",
  "@radix-ui/react-dialog": "^1.x",
  "@radix-ui/react-select": "^2.x",
  "date-fns": "^3.x"
}
```

**Backend:**
```
apscheduler>=3.10.0
cryptography>=42.0.0
pytest-asyncio>=0.21.0
httpx>=0.26.0  # Already in requirements
```

---

*Document Version: 1.0*
*Last Updated: 2026-02-06*
*Next Review: After Week 2 completion*
