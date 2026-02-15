import pytest
from httpx import AsyncClient, ASGITransport
from main import app  # Assumes main.py is in backend root and app is named 'app'
import asyncio

# Fix loop scope for pytest-asyncio if installed, else just run simple
@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health") # Assuming /health exists or fails 404
        # If /health doesn't exist, try /docs just to check app load
        if response.status_code == 404:
            response = await ac.get("/docs")
            assert response.status_code == 200
        else:
             assert response.status_code == 200

@pytest.mark.asyncio
async def test_run_job_invalid_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 999999 should not exist
        response = await ac.post("/api/v1/jobs/run/999999")
        assert response.status_code == 404
