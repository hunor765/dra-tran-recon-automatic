# Project Documentation & Changelog

This document tracks changes to the project. Versioning follows Semantic Versioning (Major.Minor.Patch).

## Version 1.0.2
**Date:** 2026-02-17

### Summary
Tracking initialized. Current codebase represents the stable release of the manual reconciliation platform and the MVP of the automated ultra version.

### Components Status
- **dra-tran-recon-manual**:
  - Frontend: Next.js 16 (App Router), Tailwind CSS v4.
  - Backend: Python FastAPI.
  - Database: Supabase (PostgreSQL).
- **dra-tran-recon-ultra**:
  - Python scripts for automated reconciliation (Google Analytics 4 + Backend APIs).

## Version 1.0.3
**Date:** 2026-02-18

### Patch Notes
- **Backend**:
  - Added new Admin Dashboard endpoints:
    - `/api/v1/admin/stats`: Aggregate statistics for clients and jobs.
    - `/api/v1/admin/cleanup`: Trigger data retention cleanup tasks.
    - `/api/v1/admin/storage`: Database storage usage statistics.
    - `/api/v1/admin/health/detailed`: Comprehensive system health check (DB, Redis, Email).
  - Enhanced Connector management:
    - Added `/api/v1/connectors/{id}/test` endpoint for verifying credentials.
    - Added `/api/v1/connectors/config-examples/{type}` for frontend guidance.
  - Added Core modules:
    - `monitoring.py`: System monitoring utilities.
- **Frontend**:
  - Updated `DraApiClient` (`src/lib/api/client.ts`) with methods for new admin and connector endpoints.
  - Added Admin Users management section (`src/app/admin/users/`).
- **Documentation**:
  - Added `database/BACKUP_STRATEGY.md`.
  - Added `database/DATA_RETENTION.md`.
- **Testing**:
  - Added `tests/test_ingestors.py`.
