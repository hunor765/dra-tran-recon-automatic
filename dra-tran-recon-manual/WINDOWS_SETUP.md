# Windows Development Setup Guide

> **Last Updated**: 2026-02-17

This guide covers setting up the DRA Platform on Windows for local development.

---

## Prerequisites

1. **Python 3.11+** - [Download from python.org](https://www.python.org/downloads/)
2. **Node.js 20+** - [Download from nodejs.org](https://nodejs.org/)
3. **Git** - [Download from git-scm.com](https://git-scm.com/download/win)
4. **PostgreSQL** - [Download from postgresql.org](https://www.postgresql.org/download/windows/) (or use Docker)

---

## Step 1: Set Up Virtual Environment

Open PowerShell:

```powershell
cd "D:\Antigravity Workspace\dra-tran-recon-automatic-1\dra-tran-recon-manual\backend"
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Step 2: Install Python Dependencies

```powershell
# In backend directory with venv activated
pip install fastapi uvicorn sqlalchemy alembic asyncpg python-dotenv pydantic pydantic-settings pandas google-analytics-data httpx apscheduler cryptography pytz pyjwt supabase slowapi redis openpyxl sentry-sdk pytest pytest-asyncio
```

**Note**: `psycopg2-binary` is only needed for some migration scripts. The main app uses `asyncpg`.

---

## Step 3: Environment Variables

Create `.env` file in `backend` folder:

```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/dra_platform
ENCRYPTION_KEY=your-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## Step 4: Start Database

```powershell
# Using Docker
cd "D:\Antigravity Workspace\dra-tran-recon-automatic-1\dra-tran-recon-manual"
docker-compose up -d
```

---

## Step 5: Start Backend

```powershell
cd "D:\Antigravity Workspace\dra-tran-recon-automatic-1\dra-tran-recon-manual\backend"
.\venv\Scripts\Activate.ps1
python main.py
```

---

## Step 6: Start Frontend (New PowerShell Window!)

```powershell
cd "D:\Antigravity Workspace\dra-tran-recon-automatic-1\dra-tran-recon-manual\frontend"
npm install
```

Create `.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start dev server:
```powershell
npm run dev
```

---

## Common Issues

### Issue: "Cannot find module 'fastapi'"
**Fix**: Virtual environment not activated
```powershell
.\venv\Scripts\Activate.ps1
```

### Issue: "pg_config executable not found"
**Fix**: psycopg2 isn't needed - the app uses asyncpg. Skip that package.

### Issue: "npm error ENOENT"
**Fix**: You're in the wrong directory. Make sure you're in `frontend`, not `backend`.

### Issue: Port already in use
**Fix**: Kill existing processes or change ports
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Quick Test

1. Backend health: http://localhost:8001/health
2. API docs: http://localhost:8001/docs
3. Frontend: http://localhost:3000
4. Login with your Supabase test account
