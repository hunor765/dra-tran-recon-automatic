from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import engine, Base
from models import client, user_client, schedule
import asyncio

app = FastAPI(title=settings.PROJECT_NAME)

# CORS middleware - Updated for port 4000 (frontend) and 8001 (backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:4000",  # New frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # In production use Alembic for migrations, here we create tables for simplicity
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def read_root():
    return {"message": "Welcome to DRA Reconciliation Platform API"}

from api.v1.endpoints import clients, jobs, connectors, admin, users, schedules

# Include routers
app.include_router(clients.router, prefix="/api/v1/clients", tags=["clients"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])

# Nested routes for client-specific connectors
app.include_router(connectors.router, prefix="/api/v1/clients/{client_id}/connectors", tags=["connectors"])
# Also keep flat routes for backward compatibility
app.include_router(connectors.single_router, prefix="/api/v1/connectors", tags=["connectors"])

app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(schedules.router, prefix="/api/v1", tags=["schedules"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
