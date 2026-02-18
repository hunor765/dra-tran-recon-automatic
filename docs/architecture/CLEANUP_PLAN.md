# Project Restructuring & Cleanup Plan

This document outlines the strategy to modernize and clean up the `dra-tran-recon-automatic-1` codebase.

## 🎯 Objective
Transform the current flat/mixed directory structure into a modular, monorepo-style architecture. This will improve maintainability, separation of concerns, and onboarding speed.

## 📂 New Directory Structure

```text
/
├── apps/                       # Application source code
│   ├── platform/               # The main web application (formerly dra-tran-recon-manual)
│   │   ├── backend/            # FastAPI backend
│   │   └── frontend/           # Next.js frontend
│   │
│   └── scheduler/              # Automated reconciliation worker (formerly dra-tran-recon-ultra)
│       └── src/                # Source scripts
│
├── docs/                       # Centralized documentation
│   ├── platform/               # Platform-specific guides (setup, API, deployment)
│   ├── scheduler/              # Scheduler documentation
│   └── architecture/           # High-level architecture docs
│
├── scripts/                    # Utility and maintenance scripts
│   ├── dev/                    # Development helpers
│   └── analysis/               # Ad-hoc analysis scripts
│
├── .gitignore
├── README.md
└── docker-compose.yml          # Root orchestration (optional/future)
```

## 📋 Step-by-Step Execution Plan

### Phase 1: Preparation
1.  **Backup**: Ensure all code is committed to git.
2.  **Create Directories**:
    ```bash
    mkdir -p apps/platform apps/scheduler docs/platform docs/scheduler scripts/analysis
    ```

### Phase 2: Relocation

#### 1. Web Platform
Move the main application parts to `apps/platform`.
-   `dra-tran-recon-manual/backend` -> `apps/platform/backend`
-   `dra-tran-recon-manual/frontend` -> `apps/platform/frontend`
-   `dra-tran-recon-manual/database` -> `apps/platform/database`
-   `dra-tran-recon-manual/docker-compose.yml` -> `apps/platform/docker-compose.yml`

#### 2. Scheduler
Move the automation tool to `apps/scheduler`.
-   `dra-tran-recon-ultra/*` -> `apps/scheduler/`

#### 3. Documentation
Consolidate documentation into `docs/`.
-   **Root Docs**:
    -   `BRAND_GUIDELINES.md` -> `docs/BRAND_GUIDELINES.md`
    -   `AGENTS.md` -> `docs/DEVELOPER_GUIDE.md`
-   **Platform Docs** (from `dra-tran-recon-manual/`):
    -   `*.md` files -> `docs/platform/`
    -   e.g., `SUPABASE_SETUP.md`, `API_INTEGRATION_GUIDE.md`
-   **Scheduler Docs**:
    -   `apps/scheduler/README.md` -> `docs/scheduler/README.md` (optional, or keep generic)

#### 4. Scripts
Move ad-hoc scripts to `scripts/`.
-   `generate_test_data.py`, `inspect_excel.py` -> `scripts/`
-   `reconciliation_analysis*.py` -> `scripts/analysis/`

### Phase 3: Cleanup & Fixes
1.  **Remove Empty Folders**: Delete `dra-tran-recon-manual`, `dra-tran-recon-ultra`, `dra-tran-recon-manual_backup`.
2.  **Fix References**:
    -   Update any paths in `docker-compose.yml`.
    -   Review `next.config.ts` or `frontend` scripts if they rely on relative paths (usually fine).
3.  **Update Root README**: Create a new root `README.md` that points to the new locations.

## 🧪 Verification
1.  **Backend**: `cd apps/platform/backend && python main.py` triggers successfully.
2.  **Frontend**: `cd apps/platform/frontend && npm run dev` starts successfully.
3.  **Scheduler**: `cd apps/scheduler && python main.py` runs.
