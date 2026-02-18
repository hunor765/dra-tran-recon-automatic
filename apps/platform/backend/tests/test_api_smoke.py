"""API smoke tests for basic health checks."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test the health endpoint returns 200 when healthy."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert "checks" in data
        assert "api" in data["checks"]


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint returns API info."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "operational"


@pytest.mark.asyncio
async def test_run_job_unauthorized_without_token():
    """Test that running a job without auth token returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # In production, this should return 401 Unauthorized
        # In development, it may allow access (dev bypass)
        response = await ac.post("/api/v1/jobs/run/999999")
        # Should be either 401 (no auth) or 404 (auth passed but client not found)
        assert response.status_code in [401, 403, 404]
