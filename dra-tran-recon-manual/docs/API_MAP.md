# API Endpoint Map

This document provides a precise mapping of all backend API endpoints in the `dra-tran-recon-manual` application.

## 1. Authentication & Users
**Base Path:** `/api/v1`

| Method | Endpoint | Functionality | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/clients/{client_id}/invite` | Invite a user via email to access a specific client. Check if user already exists for client. | Admin |
| `GET` | `/clients/{client_id}/users` | List all users (invitations/active) for a specific client. | Admin |
| `DELETE` | `/users/{user_client_id}` | Revoke a user's access to a client. | Admin |

## 2. Clients
**Base Path:** `/api/v1/clients`

| Method | Endpoint | Functionality | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | List all clients. Supports pagination (`skip`, `limit`). | Authenticated |
| `POST` | `/` | Create a new client. | Authenticated |
| `GET` | `/{client_id}` | Get details of a specific client. | Authenticated |
| `PUT` | `/{client_id}` | Update client details (name, slug, logo). | Admin |
| `DELETE` | `/{client_id}` | Delete a client permanently. | Admin |

## 3. Connectors
**Base Paths:**
- `/api/v1/clients/{client_id}/connectors` (Management)
- `/api/v1/connectors` (Operations)

| Method | Endpoint | Functionality | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/clients/{client_id}/connectors` | List all connectors configured for a client. | Authenticated |
| `POST` | `/clients/{client_id}/connectors` | Create a new connector with validated config. | Admin |
| `GET` | `/clients/{client_id}/connectors/config-examples/{connector_type}` | Get example config for a connector type. | Admin |
| `GET` | `/connectors/{connector_id}` | Get details of a specific connector. | Authenticated |
| `PUT` | `/connectors/{connector_id}` | Update connector configuration or type. Re-encrypts config if changed. | Admin |
| `DELETE` | `/connectors/{connector_id}` | Delete a connector. | Admin |
| `POST` | `/connectors/{connector_id}/test` | Test connector connection. Decrypts config and attempts raw fetch (1 day). | Admin |

### Connector Configuration Schemas

#### GA4 Config
```json
{
  "property_id": "123456789",
  "credentials_json": {
    "type": "service_account",
    "project_id": "my-project",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    "client_email": "analytics@my-project.iam.gserviceaccount.com",
    "client_id": "...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

#### Shopify Config
```json
{
  "shop_url": "my-store.myshopify.com",
  "access_token": "shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

#### WooCommerce Config
```json
{
  "url": "https://my-store.com",
  "consumer_key": "ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "consumer_secret": "cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

## 4. Jobs & Reconciliation
**Base Path:** `/api/v1/jobs`

| Method | Endpoint | Functionality | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | List all reconciliation jobs. Filters: `client_id`, `status`. | Authenticated |
| `POST` | `/run/{client_id}` | **Trigger job (async).** Creates a job and runs reconciliation in background. Supports `days`, `start_date`, `end_date`. Returns immediately. | Admin |
| `POST` | `/{job_id}/retry` | **Retry a failed job.** Manually retry with exponential backoff. | Admin |
| `GET` | `/{job_id}` | Get detailed job information including retry status. | Authenticated |

### Job Configuration

When triggering a job, you can specify date range:

```json
{
  "days": 30,
  "start_date": "2026-01-01",
  "end_date": "2026-01-31",
  "max_retries": 3
}
```

- `days`: Number of days to fetch (1-365, default: 30). Ignored if `start_date` provided.
- `start_date`: Explicit start date (YYYY-MM-DD). Optional.
- `end_date`: Explicit end date (YYYY-MM-DD). Defaults to today. Optional.
- `max_retries`: Maximum retry attempts for failed jobs (0-5, default: 3).

The job result now includes:
```json
{
  "match_rate": 95.5,
  "total_backend_value": 15000.00,
  "total_ga4_value": 14325.00,
  "missing_count": 5,
  "missing_ids": ["ORD-1001", "ORD-1002"],
  "days_analyzed": 30,
  "date_range": {
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
  },
  "ga4_records": 100,
  "backend_records": 105,
  "retry_attempt": 1
}
```

### Job Retry

Jobs automatically retry on failure with exponential backoff (2^attempt seconds):
- Attempt 1: Wait 2 seconds
- Attempt 2: Wait 4 seconds  
- Attempt 3: Wait 8 seconds

Manual retry:
```bash
POST /api/v1/jobs/{job_id}/retry
```

## 5. Schedules & Triggers
**Base Path:** `/api/v1`

| Method | Endpoint | Functionality | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/trigger/{client_id}` | **Manual Trigger (async).** Creates a job and runs reconciliation in background. Accepts date range config. | Admin |
| `GET` | `/clients/{client_id}/schedule` | Get client schedule from database. Returns schedule config with computed `next_run`. | Admin |
| `POST` | `/clients/{client_id}/schedule` | Create or update client schedule. Stores in database. | Admin |
| `PUT` | `/clients/{client_id}/schedule` | Update specific fields of client schedule. | Admin |
| `DELETE` | `/clients/{client_id}/schedule` | Delete client schedule. | Admin |

### Schedule Configuration

```json
{
  "frequency": "daily",
  "time_of_day": "03:00:00",
  "timezone": "Europe/Bucharest",
  "is_active": true,
  "config": {
    "days": 30,
    "start_date": null,
    "end_date": null,
    "max_retries": 3
  }
}
```

- `frequency`: `daily`, `hourly`, or `weekly`
- `time_of_day`: Time in HH:MM:SS format (for daily/weekly)
- `timezone`: IANA timezone name (e.g., "Europe/Bucharest")
- `config.days`: Number of days to fetch for scheduled runs (default: 30)
- `config.start_date`/`end_date`: Explicit date range (optional)
- `config.max_retries`: Retry attempts for scheduled jobs (default: 3)

## 6. Admin Dashboard
**Base Path:** `/api/v1/admin`

| Method | Endpoint | Functionality | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/stats` | Aggregated stats: Client count, Active clients, Job counts, Jobs by status, Recent jobs (10). | Admin |
| `GET` | `/jobs` | Admin view of all jobs with filtering. | Admin |

---

## Changes Log

### Phase 1 (Completed)

#### 1. Fixed Redundant Job Triggers
- **Before**: Two endpoints with different behavior (sync vs async)
- **After**: Both endpoints now run asynchronously using background tasks

#### 2. Fixed Hardcoded Schedule
- **Before**: `GET /clients/{client_id}/schedule` returned hardcoded `3:00 AM EET`
- **After**: Schedule is stored in database and fully configurable via API

#### 3. Fixed Blocking Operations
- **Before**: `/api/v1/jobs/run/{client_id}` ran blocking
- **After**: All job execution is done via `BackgroundTasks`

### Phase 2 (Completed)

#### 4. Parameterized Date Ranges
- **Before**: Reconciliation always used hardcoded `fetch_data(days=30)`
- **After**: Jobs support configurable `days` parameter (1-365)

#### 5. Added Connector Config Validation
- **Before**: Connector configs stored as generic `Dict[str, Any]`
- **After**: Strongly-typed validation for GA4, Shopify, WooCommerce configs

### Phase 3 (Completed)

#### 6. Dynamic Scheduler
- **Before**: Single cron job at 3 AM for all clients
- **After**: 
    - Each client schedule gets its own cron trigger
    - Schedules auto-refresh every 5 minutes from database
    - Supports per-client timezone configuration
    - New scheduler functions: `load_schedules()`, `shutdown_scheduler()`

#### 7. Date Range Support
- **Before**: Only supported `days` parameter
- **After**:
    - All ingestors support `start_date` and `end_date` parameters
    - Job model has `start_date` and `end_date` columns
    - Schedule config supports date range
    - Date validation ensures YYYY-MM-DD format

#### 8. Job Retry Logic
- **Before**: Jobs failed immediately on error
- **After**:
    - Automatic retry with exponential backoff (2^attempt seconds)
    - Configurable `max_retries` per job (0-5, default: 3)
    - New job statuses: `RETRYING`, `FAILED`
    - Job model tracks `retry_count` and `max_retries`
    - Manual retry endpoint: `POST /jobs/{id}/retry`
    - Job response includes `can_retry` boolean

---

## Architecture

### Scheduler Flow
```
start_scheduler()
    ↓
load_schedules() ← Every 5 minutes
    ↓
For each active schedule:
    Create/Update APScheduler Job
    ↓
Trigger fires → run_job_for_client()
    ↓
Create Job record → execute_reconciliation()
    ↓
Success: Mark COMPLETED
Failure: Retry with backoff → Max retries reached → Mark FAILED
```

### Retry Flow
```
execute_reconciliation() fails
    ↓
retry_count < max_retries?
    ↓ YES
Set status RETRYING
    ↓
Sleep 2^attempt seconds
    ↓
Retry execute_reconciliation(attempt+1)
    ↓ NO
Set status FAILED
Log final error
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `ENCRYPTION_KEY` | Key for config encryption | Required |
| `SCHEDULER_ENABLED` | Enable background scheduler | `true` |
