# PLAN-hybrid-platform.md - DRA Reconciliation Platform

> **Goal:** Transform the Manual/MVP tools into a full-fledged SaaS-like platform with Multi-client support, Admin/Client dashboards, and automated reconciliation engine.

**Architecture:** Hybrid Powerhouse
- **Frontend:** Next.js (Admin & Client Dashboards)
- **Backend:** Python FastAPI (Data Processing, Scheduling, Connectors)
- **Database:** PostgreSQL (via Supabase)
- **Auth:** Supabase Auth

---

## Phase 1: Foundation & Data Layer
**Objective:** Set up the shared database and authentication infrastructure.

- [ ] **1.1. Supabase Setup**
    - [ ] Create `clients` table (name, slug, logo_url).
    - [ ] Create `connectors` table (type: `ga4`|`woo`|`shopify`, credentials_encrypted).
    - [ ] Create `jobs` table (client_id, status, last_run).
    - [ ] Create `results` table (jsonb for flexible storage of discrepancy reports).
- [ ] **1.2. Backend (FastAPI) Core**
    - [ ] Initialize `dra-platform-backend`.
    - [ ] Implement Supabase Client connection.
    - [ ] Port `ingestors` from MVP to new backend structure.
    - [ ] Implement `EncryptionService` for storing API keys securely.

## Phase 2: The Core Engine (Python)
**Objective:** API endpoints to manage configurations and run audits.

- [ ] **2.1. Management APIs**
    - [ ] `POST /clients` (Create client)
    - [ ] `POST /clients/{id}/connectors` (Add/Update keys)
- [ ] **2.2. Execution Engine**
    - [ ] `POST /jobs/run/{client_id}`
    - [ ] Implement Background Worker (Celery or simple `BackgroundTasks`) for long-running reconciliations.
    - [ ] Update Logic: Fetch config from DB -> Decrypt keys -> Run Ingest/Reconcile -> Save to `results` DB.

## Phase 3: Frontend - Admin Panel
**Objective:** Interface for DRA staff to manage clients.

- [ ] **3.1. Next.js Architecture**
    - [ ] Initialize `dra-platform-frontend`.
    - [ ] Setup Supabase Auth (Login Page).
    - [ ] Admin Route Protection (`role: admin`).
- [ ] **3.2. Client Management**
    - [ ] Client List & Create Modal.
    - [ ] Connector Configuration Forms (GA4 JSON upload, Shopify Access Token input).
- [ ] **3.3. Job Control**
    - [ ] Button to manually trigger "Run Audit".
    - [ ] View Job Logs/Status.

## Phase 4: Frontend - Client Dashboard
**Objective:** Read-only view for Clients to see their stats.

- [ ] **4.1. Dashboard Layout (Pro Max)**
    - [ ] Sidebar Navigation (Overview, History, Settings).
    - [ ] Global Date Range Picker.
- [ ] **4.2. Visualization Components**
    - [ ] Hero Gradient Banner (Revenue Discrepancy).
    - [ ] Trend Charts (Match Rate over time) using Recharts.
    - [ ] Missing Transaction Table (Data Grid with export).
- [ ] **4.3. Client Access**
    - [ ] Client Login Flow.
    - [ ] Ensure RLS (Row Level Security) prevents seeing other clients' data.

## Phase 5: Polish & Deployment
- [ ] **5.1. Branding**
    - [ ] Apply `BRAND_GUIDELINES.md` strictly (Montserrat, Revolt Red).
- [ ] **5.2. Testing**
    - [ ] Integration test: Create Client -> Add Mock Keys -> Run Job -> Verify Dashboard.
- [ ] **5.3. Dockerization**
    - [ ] Dockerfile for Backend.
    - [ ] Dockerfile for Frontend.
    - [ ] `docker-compose.yml` for local orchestration.

---

## Open Questions
1. **Hosting:** Will Supabase free tier suffice for row limits? (Assuming yes for MVP).
2. **Encryption:** Should we use Vault or simple AES in Python for stored keys? (Suggest AES for MVP).
3. **Scheduler:** Do we need CRON right now or is "Click to Run" enough? (Plan assumes Click-to-Run initially).

---

## Agent Assignments
- `backend-specialist`: Phase 1, Phase 2
- `frontend-specialist`: Phase 3, Phase 4
- `database-architect`: Phase 1.1 (Schema Design)
- `orchestrator`: Project Management & Review
