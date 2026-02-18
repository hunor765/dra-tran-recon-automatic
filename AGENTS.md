# DRA Transaction Reconciliation Platform - Agent Guide

> **Project**: DRA Transaction Reconciliation Platform  
> **Owner**: Data Revolt Agency  
> **Language**: English (all code and documentation)  
> **Last Updated**: 2026-02-17

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

### Backend (`dra-tran-recon-manual/backend/`)
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | 0.109.0 |
| Runtime | Python | 3.11+ |
| ORM | SQLAlchemy | 2.0.21 (async) |
| Database | PostgreSQL | 15+ |
| Auth | Supabase Auth | JWT-based |
| Scheduler | APScheduler | 3.10.4 |
| Encryption | cryptography | 41.0.7 |
| Data Processing | pandas | 2.1.1 |

### Frontend (`dra-tran-recon-manual/frontend/`)
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
- **Local Development**: Docker Compose (PostgreSQL + Adminer)
- **Production Database**: Supabase PostgreSQL
- **Authentication**: Supabase Auth

---

## Project Structure

```
dra-tran-recon-automatic-1/
├── AGENTS.md                       # This file
├── BRAND_GUIDELINES.md             # Design system documentation
├── docs/                           # Architecture planning documents
│   ├── IMPLEMENTATION_PLAN.md      # Detailed build roadmap
│   ├── API_MAP.md                  # Complete API endpoint reference
│   └── PLAN-*.md                   # Various feature plans
│
├── dra-tran-recon-manual/          # MAIN PRODUCTION APPLICATION (85% complete)
│   ├── backend/                    # FastAPI application
│   │   ├── main.py                 # Application entry point
│   │   ├── requirements.txt        # Python dependencies
│   │   ├── core/                   # Core business logic
│   │   │   ├── config.py           # Settings management
│   │   │   ├── database.py         # SQLAlchemy setup
│   │   │   ├── auth.py             # JWT validation, RBAC
│   │   │   ├── encryption.py       # Credential encryption (Fernet)
│   │   │   ├── scheduler.py        # APScheduler setup
│   │   │   └── ingestors/          # Data source integrations
│   │   │       ├── base.py         # Base ingestor class
│   │   │       ├── google_analytics.py  # GA4 API client
│   │   │       ├── shopify.py      # Shopify API client
│   │   │       └── woocommerce.py  # WooCommerce API client
│   │   ├── api/v1/endpoints/       # REST API routes
│   │   │   ├── admin.py            # Admin dashboard stats
│   │   │   ├── clients.py          # Client CRUD
│   │   │   ├── connectors.py       # Connector CRUD + testing
│   │   │   ├── jobs.py             # Job execution + retry logic
│   │   │   ├── users.py            # User invitations
│   │   │   └── schedules.py        # Job scheduling
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── client.py
│   │   │   ├── connector.py
│   │   │   ├── job.py
│   │   │   ├── schedule.py
│   │   │   └── user_client.py      # RBAC linking table
│   │   ├── schemas/                # Pydantic models
│   │   └── tests/                  # Test suite
│   │
│   ├── frontend/                   # Next.js application
│   │   ├── package.json            # Node dependencies
│   │   ├── next.config.ts          # Next.js config
│   │   ├── middleware.ts           # Auth + RBAC middleware
│   │   ├── src/
│   │   │   ├── app/                # App router pages
│   │   │   │   ├── admin/          # Admin panel routes
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── clients/
│   │   │   │   │   └── jobs/
│   │   │   │   ├── dashboard/      # Client dashboard
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── history/
│   │   │   │   │   ├── results/[jobId]/
│   │   │   │   │   └── settings/
│   │   │   │   └── login/
│   │   │   ├── components/         # React components
│   │   │   │   ├── red-kit/        # Custom UI kit (Button, Card, Input)
│   │   │   │   ├── dashboard/      # Dashboard-specific components
│   │   │   │   └── ui/             # Generic UI components
│   │   │   └── lib/                # Utilities
│   │   │       ├── api/client.ts   # TypeScript API client
│   │   │       ├── hooks/          # React hooks
│   │   │       └── supabase/       # Supabase clients
│   │
│   ├── database/                   # SQL schema files
│   │   ├── schema.sql              # Base schema
│   │   ├── COMPLETE_SETUP.sql      # Full setup script
│   │   ├── auth_schema.sql         # RLS policies
│   │   ├── schedules.sql           # Scheduling tables
│   │   └── user_clients.sql        # RBAC tables
│   │
│   ├── docker-compose.yml          # Local PostgreSQL setup
│   ├── README.md                   # Project overview
│   ├── QUICK_START.md              # Step-by-step setup guide
│   ├── SUPABASE_SETUP.md           # Auth/data model explanation
│   └── API_MAP.md                  # API documentation
│
├── dra-tran-recon-ultra/           # SIMPLIFIED CLI VERSION
│   ├── main.py                     # CLI reconciliation tool
│   ├── config.yaml                 # Configuration template
│   ├── server.py                   # Simple HTTP server wrapper
│   └── ingestors/                  # Standalone ingestors
│
├── client 2/                       # CLIENT-SPECIFIC ANALYSIS
│   ├── analysis.py                 # Analysis scripts
│   ├── analyze_*.py                # Various analysis tools
│   └── *.md                        # Analysis reports
│
└── Root-level scripts/             # UTILITY SCRIPTS
    ├── reconciliation_analysis.py      # CSV analysis tool v1
    ├── reconciliation_analysis_v2.py   # CSV analysis tool v2
    ├── generate_test_data.py           # Test data generator
    └── inspect_excel.py                # Excel inspection tool
```

---

## Build and Run Commands

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (or Docker)

### Backend (Port 8000/8001)

```bash
cd dra-tran-recon-manual/backend

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
ENVIRONMENT=development
```

### Frontend (Port 3000/4000)

```bash
cd dra-tran-recon-manual/frontend

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
cd dra-tran-recon-manual
docker-compose up -d        # Starts PostgreSQL on port 5432 + Adminer on 8080
```

---

## Code Style Guidelines

### Python (Backend)

- **Style**: PEP 8 compliance
- **Types**: Use type hints for all function signatures
- **Async**: All database operations use `async`/`await`
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

- **Style**: ESLint config provided (`eslint.config.mjs`)
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
- **RLS**: Enable Row Level Security for multi-tenancy

---

## Testing Instructions

### Backend Tests

```bash
cd dra-tran-recon-manual/backend
pytest tests/                    # Run all tests
pytest tests/test_api_smoke.py  # Run smoke tests only
pytest -v                       # Verbose output
```

### Frontend Tests

```bash
cd dra-tran-recon-manual/frontend
npm run lint                    # ESLint check
# Note: Jest/React Testing Library setup pending (Phase 8)
```

### Manual Testing

1. **Setup Test Accounts**: See `TEST_ACCOUNTS.md`
   - Admin: `admin@dra.com` / `AdminTest123!`
   - Client: `client@example.com` / `ClientTest123!`

2. **API Testing**: FastAPI auto-docs at `http://localhost:8000/docs`

3. **End-to-End Flow**:
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

Admin email patterns (defined in `middleware.ts`):
- `@dra.com`
- `@datarevolt.ro`
- `@revolt.agency`

---

## Security Considerations

### Credential Encryption

All connector API credentials are encrypted at rest using Fernet (AES-128):
- Encryption key stored in `ENCRYPTION_KEY` env var
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

### API Security

- CORS configured for known origins only
- Rate limiting recommended for production (not yet implemented)
- Input validation via Pydantic schemas

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

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Can't login" | Check user exists in Supabase Auth dashboard, email confirmed |
| "User sees no clients" | Check `user_clients` table has linking row |
| "Connector test fails" | Verify real API credentials, check backend logs |
| "Admin can't access panel" | Email must match patterns in `middleware.ts` |
| "CORS errors" | Check `allow_origins` in `main.py` matches frontend port |
| "Database connection failed" | Verify `DATABASE_URL` format (must use `asyncpg` driver) |

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
| `QUICK_START.md` | Step-by-step setup from zero |
| `SUPABASE_SETUP.md` | Auth model and data architecture |
| `TEST_ACCOUNTS.md` | Test user creation |
| `API_MAP.md` | Complete API endpoint reference |
| `SHOPIFY_SETUP.md` | Shopify API configuration |
| `API_INTEGRATION_GUIDE.md` | WooCommerce + GA4 setup |
| `IMPLEMENTATION_PLAN.md` | Build roadmap and status |
| `BRAND_GUIDELINES.md` | Design system |

---

*This document is maintained for AI coding agents. For human contributors, see README.md files.*
