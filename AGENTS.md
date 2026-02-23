# DRA Transaction Reconciliation Platform - Agent Guide

> **Project**: DRA Transaction Reconciliation Platform  
> **Owner**: Data Revolt Agency  
> **Language**: English (all code and documentation)  
> **Last Updated**: 2026-02-23

---

## Project Overview

This is a **SaaS platform** for reconciling e-commerce transaction data between backend systems (Shopify, WooCommerce) and Google Analytics 4 (GA4). The platform detects tracking gaps by comparing transaction IDs from e-commerce backends against GA4 purchase events.

### Business Problem Solved

E-commerce stores often have discrepancies between their backend order data and GA4 tracking data due to:
- Ad blockers preventing GA4 from firing (~15-30% of transactions)
- JavaScript errors on thank-you pages
- Payment redirect flows losing tracking
- Cancelled orders appearing in one system but not the other

The platform calculates **match rates** and identifies **missing transactions** to help businesses understand their true conversion data.

---

## Technology Stack

### Backend (`apps/platform/backend/`)

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | 0.109.0 |
| Runtime | Python | 3.11+ |
| ORM | SQLAlchemy | 2.0.21 (async) |
| Database | PostgreSQL | 15+ |
| Auth | Supabase Auth | JWT-based |
| Migrations | Alembic | 1.12.0 |
| Scheduler | APScheduler | 3.10.4 |
| Encryption | cryptography (Fernet) | 41.0.7 |
| Data Processing | pandas | 2.0.3 |
| Rate Limiting | slowapi | 0.1.9 |
| Cache | redis | 5.0.1 |

### Frontend (`apps/platform/frontend/`)

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Next.js | 16.1.4 |
| Language | TypeScript | 5.x |
| Styling | Tailwind CSS | 4.x |
| UI Library | React | 19.2.3 |
| Icons | Lucide React | 0.563.0 |
| Charts | Recharts | 3.7.0 |
| Auth | Supabase SSR | 0.8.0 |

### Infrastructure

- **Local Development**: Docker Compose (PostgreSQL + Adminer on port 8080)
- **Production Database**: Supabase PostgreSQL
- **Authentication**: Supabase Auth with JWT
- **Container**: Docker with Python 3.11-slim base image
- **Deployment**: Railway (configured via `start.sh` and `Dockerfile`)

---

## Project Structure

```
dra-tran-recon-automatic-1/
├── apps/
│   ├── platform/              # Main web application (FastAPI + Next.js)
│   │   ├── backend/           # FastAPI backend API
│   │   │   ├── main.py        # Application entry point
│   │   │   ├── requirements.txt
│   │   │   ├── core/          # Core business logic
│   │   │   │   ├── config.py       # Settings management (pydantic-settings)
│   │   │   │   ├── database.py     # SQLAlchemy async setup
│   │   │   │   ├── auth.py         # JWT validation, RBAC
│   │   │   │   ├── encryption.py   # Fernet credential encryption
│   │   │   │   ├── scheduler.py    # APScheduler setup
│   │   │   │   ├── cache.py        # Redis caching layer
│   │   │   │   ├── rate_limiter.py # API rate limiting
│   │   │   │   ├── webhooks.py     # Webhook delivery
│   │   │   │   ├── email_service.py # Resend integration
│   │   │   │   ├── monitoring.py   # Sentry integration
│   │   │   │   └── ingestors/      # Data source integrations
│   │   │   │       ├── base.py
│   │   │   │       ├── google_analytics.py  # GA4 API client
│   │   │   │       ├── shopify.py           # Shopify API client
│   │   │   │       └── woocommerce.py       # WooCommerce API client
│   │   │   ├── api/v1/endpoints/  # REST API routes
│   │   │   │   ├── admin.py       # Admin dashboard stats
│   │   │   │   ├── clients.py     # Client CRUD
│   │   │   │   ├── connectors.py  # Connector CRUD + testing
│   │   │   │   ├── jobs.py        # Job execution + retry logic
│   │   │   │   ├── users.py       # User invitations
│   │   │   │   ├── schedules.py   # Job scheduling
│   │   │   │   ├── webhooks.py    # Webhook management
│   │   │   │   ├── exports.py     # Data export functionality
│   │   │   │   └── debug.py       # Debug endpoints
│   │   │   ├── models/            # SQLAlchemy models
│   │   │   │   ├── client.py
│   │   │   │   ├── connector.py
│   │   │   │   ├── job.py
│   │   │   │   ├── schedule.py
│   │   │   │   ├── user_client.py # RBAC linking table
│   │   │   │   └── webhook.py
│   │   │   ├── schemas/           # Pydantic models
│   │   │   │   ├── client.py
│   │   │   │   ├── connector.py
│   │   │   │   ├── connector_configs.py
│   │   │   │   ├── job.py
│   │   │   │   ├── schedule.py
│   │   │   │   └── webhook.py
│   │   │   ├── tests/             # pytest test suite
│   │   │   │   ├── test_api_smoke.py
│   │   │   │   ├── test_api_endpoints.py
│   │   │   │   ├── test_core_components.py
│   │   │   │   └── test_ingestors.py
│   │   │   └── alembic/           # Database migrations
│   │   │       ├── env.py
│   │   │       └── versions/
│   │   │
│   │   ├── frontend/              # Next.js application
│   │   │   ├── package.json
│   │   │   ├── next.config.ts
│   │   │   ├── middleware.ts      # Auth + RBAC middleware
│   │   │   ├── eslint.config.mjs
│   │   │   ├── tsconfig.json
│   │   │   └── src/
│   │   │       ├── app/           # App router pages
│   │   │       │   ├── admin/     # Admin panel routes
│   │   │       │   ├── dashboard/ # Client dashboard
│   │   │       │   ├── login/     # Authentication
│   │   │       │   └── layout.tsx # Root layout
│   │   │       ├── components/
│   │   │       │   ├── red-kit/   # Custom UI kit (Button, Card, Input)
│   │   │       │   ├── dashboard/ # Dashboard-specific components
│   │   │       │   └── ui/        # Generic UI components
│   │   │       └── lib/
│   │   │           ├── api/client.ts    # TypeScript API client
│   │   │           ├── hooks/           # React hooks (useClients, useJobs)
│   │   │           ├── supabase/        # Supabase clients
│   │   │           └── utils.ts
│   │   │
│   │   └── database/              # SQL schemas & migrations
│   │       ├── schema.sql         # Base schema
│   │       ├── COMPLETE_SETUP.sql # Full setup script
│   │       ├── auth_schema.sql    # RLS policies
│   │       ├── schedules.sql      # Scheduling tables
│   │       └── user_clients.sql   # RBAC tables
│   │
│   └── scheduler/                 # Standalone reconciliation worker
│       └── src/
│           ├── main.py            # CLI reconciliation tool
│           ├── server.py          # Simple HTTP server wrapper
│           ├── config.yaml        # Configuration template
│           ├── README.md
│           ├── ingestors/         # Standalone ingestors (copied from backend)
│           └── templates/         # HTML report templates
│
├── docs/                          # Documentation
│   ├── DEVELOPER_GUIDE.md         # Developer setup & guidelines
│   ├── BRAND_GUIDELINES.md        # Design system & color palette
│   ├── IMPLEMENTATION_PLAN.md     # Build roadmap and status
│   ├── API_MAP.md                 # API endpoint reference
│   └── platform/                  # Platform-specific docs
│       ├── QUICK_START.md         # Step-by-step setup
│       ├── SUPABASE_SETUP.md      # Auth model explanation
│       ├── TEST_ACCOUNTS.md       # Test user credentials
│       ├── DEPLOYMENT.md          # Production deployment guide
│       └── API_INTEGRATION_GUIDE.md
│
├── scripts/                       # Utility scripts
│   ├── dev/                       # Development helpers
│   └── analysis/                  # Data analysis scripts
│
├── client 2/                      # Client-specific analysis (separate)
│   ├── analysis.py
│   └── *.md                       # Analysis reports
│
├── Dockerfile                     # Production container image
├── docker-compose.yml            # Local PostgreSQL setup
└── README.md                     # Project overview
```

---

## Build and Run Commands

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (or Docker)

### Backend (Port 8000/8001)

```bash
cd apps/platform/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py              # Production mode (port 8001)
# OR
uvicorn main:app --reload   # Development mode (port 8000)
```

**Backend Environment Variables** (create `.env` file):
```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/dra_platform
ENCRYPTION_KEY=your-32-byte-base64-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:4000
REDIS_URL=redis://localhost:6379/0  # Optional
RESEND_API_KEY=your-resend-key      # Optional (emails)
SENTRY_DSN=your-sentry-dsn          # Optional (monitoring)
```

### Frontend (Port 4000)

```bash
cd apps/platform/frontend

# Install dependencies
npm install

# Development server
npm run dev                 # Runs on port 4000

# Production build
npm run build
npm start
```

**Frontend Environment Variables** (create `.env.local` file):
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Local Database (Docker)

```bash
cd apps/platform
docker-compose up -d        # Starts PostgreSQL on port 5432 + Adminer on 8080
```

### Scheduler (Standalone)

```bash
cd apps/scheduler/src
pip install pandas pyyaml jinja2 google-analytics-data
python main.py              # Run reconciliation manually
```

### Database Migrations

```bash
cd apps/platform/backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Code Style Guidelines

### Python (Backend)

- **Style**: PEP 8 compliance
- **Types**: Use type hints for all function signatures
- **Async**: All database operations use `async`/`await` with SQLAlchemy 2.0 async
- **Imports**: Group as stdlib → third-party → local
- **Docstrings**: Google style docstrings for public functions

Example:
```python
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

async def fetch_data(
    self, 
    days: int = 30,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """Fetch data for the specified date range.
    
    Args:
        days: Number of days to fetch (used if start_date not provided)
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)
        
    Returns:
        DataFrame with cleaned transaction data
    """
    pass
```

### TypeScript/React (Frontend)

- **Style**: ESLint config provided (`eslint.config.mjs`) extends Next.js core web vitals
- **Components**: Functional components with explicit return types
- **Props**: Interface definitions for all component props
- **State**: Use hooks, prefer `useCallback`/`useMemo` for expensive operations
- **API Calls**: Use the typed `DraApiClient` in `lib/api/client.ts`

Example:
```typescript
interface HeroStatProps {
  matchRate: number;
  totalOrders: number;
  trend?: 'up' | 'down' | 'neutral';
}

export function HeroStat({ matchRate, totalOrders, trend }: HeroStatProps): JSX.Element {
  // Component implementation
}
```

### Database

- **Migrations**: Use Alembic for schema migrations
- **Naming**: snake_case for tables/columns
- **Foreign Keys**: Always use explicit FK constraints with CASCADE where appropriate
- **RLS**: Enable Row Level Security for multi-tenancy (see `auth_schema.sql`)

---

## Testing Instructions

### Backend Tests

```bash
cd apps/platform/backend

# Run all tests
pytest tests/

# Run smoke tests only
pytest tests/test_api_smoke.py

# Run with coverage
pytest --cov=core --cov=api tests/

# Verbose output
pytest -v
```

**Test Files:**
- `test_api_smoke.py` - Basic health checks and endpoint availability
- `test_api_endpoints.py` - API endpoint functionality tests
- `test_core_components.py` - Unit tests for encryption, cache, rate limiter, scheduler
- `test_ingestors.py` - Tests for GA4, Shopify, WooCommerce ingestors

### Frontend Tests

```bash
cd apps/platform/frontend

# ESLint check
npm run lint

# Type check
npx tsc --noEmit
```

### Manual Testing

1. **Setup Test Accounts**: See `docs/platform/TEST_ACCOUNTS.md`
   - Admin: `admin@dra.com` / `AdminTest123!`
   - Client: `client@example.com` / `ClientTest123!`

2. **API Testing**: FastAPI auto-docs at `http://localhost:8000/docs`

3. **End-to-End Flow**:
   - Login as admin at `/login`
   - Create client in Admin panel
   - Add GA4 + Shopify/WooCommerce connectors
   - Test connector connections
   - Run reconciliation job
   - View results in Dashboard

---

## Key Architecture Patterns

### Multi-Tenancy Model

```
auth.users (Supabase managed)
    │
    ▼
user_clients (links users to clients)
    │
    ▼
clients ──► connectors ──► jobs
```

- `auth.users`: Login accounts (managed by Supabase)
- `clients`: Business entities (stores being monitored)
- `user_clients`: Permission links (RBAC)
- `connectors`: API credentials (encrypted)
- `jobs`: Reconciliation execution records

### Reconciliation Flow

```
1. Trigger Job (API / Schedule)
        │
        ▼
2. Fetch GA4 Data ───────┐
   (transaction IDs)     │
        │                │
        ▼                ▼
3. Fetch Backend Data    │
   (Shopify/WooCommerce) │
        │                │
        ▼                ▼
4. Compare Transaction IDs
   - Match: IDs present in both
   - Missing: In backend but NOT in GA4
        │
        ▼
5. Calculate Metrics
   - Match Rate: % of backend orders found in GA4
   - Value Discrepancy: Financial difference
        │
        ▼
6. Store Results (jobs table)
```

### Admin vs Client Access

| Feature | Admin | Client |
|---------|-------|--------|
| Create/Edit Clients | ✅ | ❌ |
| Manage Connectors | ✅ | ❌ |
| Run Jobs | ✅ | ❌ |
| View All Jobs | ✅ | ❌ |
| View Own Dashboard | ✅ | ✅ |
| View Job Results | ✅ (all) | ✅ (own only) |

**Admin email patterns** (defined in `middleware.ts`):
- `@dra.com`
- `@datarevolt.ro`
- `@revolt.agency`

---

## Security Considerations

### Credential Encryption

All connector API credentials are encrypted at rest using Fernet (AES-128):
- Encryption key stored in `ENCRYPTION_KEY` env var (32-byte base64-encoded)
- Encrypt on save: `encrypt_config(config_json)`
- Decrypt on use: `decrypt_config(encrypted)`

### Authentication

- JWT tokens from Supabase Auth
- Token validation in `core/auth.py`
- Middleware checks in `middleware.ts`

### Row Level Security (RLS)

PostgreSQL RLS policies enforce:
- Users can only see clients linked via `user_clients`
- Admins can see all (via email domain check)

See `apps/platform/database/auth_schema.sql` for RLS policy definitions.

### API Security

- CORS configured for known origins only (`CORS_ORIGINS` env var)
- Rate limiting implemented with slowapi (Redis-backed)
- Input validation via Pydantic schemas
- Standard rate limits:
  - Health checks: 60/minute
  - List/Get operations: 100/minute
  - Create/Update: 30/minute
  - Delete: 10/minute
  - Job execution: 10/minute

### Data Retention

Configured retention policies (in `core/config.py`):
- Job results: 90 days
- Job logs: 30 days
- Failed jobs: 180 days
- Audit logs: 365 days

---

## Common Development Tasks

### Adding a New Connector Type

1. Create ingestor in `backend/core/ingestors/{new_platform}.py`
2. Inherit from `BaseIngestor` and implement `fetch_data()`
3. Add config schema in `backend/schemas/connector_configs.py`
4. Add frontend form component
5. Update connector type enum in database

### Adding a New API Endpoint

1. Create/update endpoint file in `backend/api/v1/endpoints/`
2. Add Pydantic schema in `backend/schemas/` if needed
3. Register router in `backend/main.py`
4. Add TypeScript method in `frontend/src/lib/api/client.ts`
5. Update `docs/API_MAP.md`

### Database Schema Changes

1. Modify model in `backend/models/`
2. Create Alembic migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`
4. Update `database/schema.sql` for new setups

---

## External Dependencies

### APIs Used

- **Google Analytics Data API v1beta**: GA4 transaction data
- **Shopify Admin API**: Order data
- **WooCommerce REST API**: Order data
- **Supabase Auth**: Authentication

### Required Credentials

**GA4 Connector**:
- Property ID (9-digit number)
- Service Account JSON key file

**Shopify Connector**:
- Shop URL (e.g., `my-store.myshopify.com`)
- Admin API access token (`shpat_...`)

**WooCommerce Connector**:
- Store URL
- Consumer Key (`ck_...`)
- Consumer Secret (`cs_...`)

---

## Documentation Index

| File | Purpose |
|------|---------|
| `docs/platform/QUICK_START.md` | Step-by-step setup from zero |
| `docs/platform/SUPABASE_SETUP.md` | Auth model and data architecture |
| `docs/platform/TEST_ACCOUNTS.md` | Test user creation |
| `docs/API_MAP.md` | Complete API endpoint reference |
| `docs/platform/SHOPIFY_SETUP.md` | Shopify API configuration |
| `docs/platform/API_INTEGRATION_GUIDE.md` | WooCommerce + GA4 setup |
| `docs/IMPLEMENTATION_PLAN.md` | Build roadmap and status |
| `docs/BRAND_GUIDELINES.md` | Design system |
| `docs/platform/DEPLOYMENT.md` | Production deployment guide |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Can't login" | Check user exists in Supabase Auth dashboard, email confirmed |
| "User sees no clients" | Check `user_clients` table has linking row |
| "Connector test fails" | Verify real API credentials, check backend logs |
| "Admin can't access panel" | Email must match patterns in `middleware.ts` |
| "CORS errors" | Check `CORS_ORIGINS` in `.env` matches frontend port |
| "Database connection failed" | Verify `DATABASE_URL` format (must use `asyncpg` driver) |
| "Encryption key error" | Generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |

---

*© 2026 Data Revolt Agency. All rights reserved.*
