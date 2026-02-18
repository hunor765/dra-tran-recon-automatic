# Port Configuration

This document describes the port configuration for local development.

## Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend (Next.js) | 4000 | http://localhost:4000 |
| Backend (FastAPI) | 8001 | http://localhost:8001 |

## Files Modified

### Frontend
- `frontend/.env.local` - Updated `NEXT_PUBLIC_API_URL` to point to port 8001
- `frontend/package.json` - Updated scripts to use port 4000 (`-p 4000`)
- `frontend/next.config.ts` - Cleaned up config

### Backend
- `backend/main.py` - Updated CORS to allow port 4000, added `__main__` block to run on port 8001

## Running the Application

### Option 1: Using start scripts

```bash
# Terminal 1 - Backend
cd dra-tran-recon-manual/backend
./start.sh

# Terminal 2 - Frontend
cd dra-tran-recon-manual/frontend
./start.sh
```

### Option 2: Manual startup

```bash
# Terminal 1 - Backend (port 8001)
cd dra-tran-recon-manual/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend (port 4000)
cd dra-tran-recon-manual/frontend
npm run dev
```

## Accessing the Application

- **Landing Page**: http://localhost:4000
- **Login**: http://localhost:4000/login
- **Dashboard**: http://localhost:4000/dashboard
- **Admin**: http://localhost:4000/admin
- **API Docs**: http://localhost:8001/docs
- **API Root**: http://localhost:8001/

## CORS Configuration

The backend is configured to accept requests from:
- http://localhost:3000 (default Next.js)
- http://localhost:3001 (alternate Next.js)
- http://localhost:4000 (configured frontend port)
