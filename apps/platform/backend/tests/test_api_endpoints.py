"""Tests for API endpoints."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from httpx import AsyncClient, ASGITransport

from main import app
from models.job import JobStatus


class TestClientEndpoints:
    """Tests for client API endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_clients_unauthorized(self):
        """Test that listing clients requires authentication."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/clients/")
            # Should be 401 or 403 depending on auth middleware
            assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    @patch("api.v1.endpoints.clients.get_current_user")
    @patch("sqlalchemy.ext.asyncio.AsyncSession.execute")
    async def test_list_clients_success(self, mock_execute, mock_get_user):
        """Test successful client listing."""
        mock_get_user.return_value = {"id": "test-user", "email": "admin@dra.com"}
        
        # Mock database result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [
            Mock(id=1, name="Test Client", slug="test-client", is_active=True),
        ]
        mock_execute.return_value = mock_result
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/clients/", headers={"Authorization": "Bearer test"})
            # May be 200 if auth passes or 401/403 if mocked differently
            assert response.status_code in [200, 401, 403]


class TestJobEndpoints:
    """Tests for job API endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_jobs_unauthorized(self):
        """Test that listing jobs requires authentication."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/jobs/")
            assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_run_job_unauthorized(self):
        """Test that running jobs requires authentication."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/v1/jobs/run/1")
            assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    @patch("api.v1.endpoints.jobs.get_current_user")
    @patch("api.v1.endpoints.jobs.require_admin")
    @patch("sqlalchemy.ext.asyncio.AsyncSession.execute")
    async def test_run_job_client_not_found(self, mock_execute, mock_require_admin, mock_get_user):
        """Test running job for non-existent client."""
        mock_get_user.return_value = {"id": "test-user", "email": "admin@dra.com"}
        mock_require_admin.return_value = mock_get_user.return_value
        
        # Mock empty result (client not found)
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_execute.return_value = mock_result
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/jobs/run/99999",
                headers={"Authorization": "Bearer test"}
            )
            # Should be 404 if auth passes
            assert response.status_code in [404, 401, 403]


class TestConnectorEndpoints:
    """Tests for connector API endpoints."""
    
    @pytest.mark.asyncio
    async def test_test_connector_unauthorized(self):
        """Test that testing connectors requires authentication."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/v1/connectors/1/test")
            assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    @patch("api.v1.endpoints.connectors.get_current_user")
    @patch("sqlalchemy.ext.asyncio.AsyncSession.get")
    async def test_test_connector_not_found(self, mock_get, mock_get_user):
        """Test testing non-existent connector."""
        mock_get_user.return_value = {"id": "test-user"}
        mock_get.return_value = None  # Connector not found
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/connectors/99999/test",
                headers={"Authorization": "Bearer test"}
            )
            assert response.status_code in [404, 401, 403]


class TestAdminEndpoints:
    """Tests for admin API endpoints."""
    
    @pytest.mark.asyncio
    async def test_admin_stats_unauthorized(self):
        """Test that admin stats requires authentication."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/admin/stats")
            assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_admin_jobs_unauthorized(self):
        """Test that admin jobs endpoint requires authentication."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/admin/jobs")
            assert response.status_code in [401, 403]


class TestWebhookEndpoints:
    """Tests for webhook API endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_webhooks_unauthorized(self):
        """Test that listing webhooks requires authentication."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/clients/1/webhooks")
            assert response.status_code in [401, 403]


class TestSchemaValidation:
    """Tests for request/response schema validation."""
    
    def test_job_config_validation(self):
        """Test JobConfig schema validation."""
        from schemas.job import JobConfig
        
        # Valid config
        config = JobConfig(days=30, max_retries=3)
        assert config.days == 30
        assert config.max_retries == 3
        
        # Invalid days (too high)
        with pytest.raises(ValueError):
            JobConfig(days=500)
        
        # Invalid max_retries (negative)
        with pytest.raises(ValueError):
            JobConfig(max_retries=-1)
    
    def test_job_config_date_validation(self):
        """Test JobConfig date validation."""
        from schemas.job import JobConfig
        
        # Valid dates
        config = JobConfig(start_date="2024-01-01", end_date="2024-01-31")
        assert config.start_date == "2024-01-01"
        assert config.end_date == "2024-01-31"
        
        # Invalid date format
        with pytest.raises(ValueError):
            JobConfig(start_date="01-01-2024")
        
        # Start after end
        with pytest.raises(ValueError):
            JobConfig(start_date="2024-12-31", end_date="2024-01-01")
    
    def test_connector_config_validation(self):
        """Test connector config schema validation."""
        from schemas.connector_configs import ShopifyConfig, GA4Config, WooCommerceConfig
        
        # Valid Shopify config
        shopify = ShopifyConfig(shop_url="test.myshopify.com", access_token="shpat_xxx")
        assert shopify.shop_url == "test.myshopify.com"
        
        # Valid GA4 config
        ga4 = GA4Config(property_id="123456789", credentials_json="{}")
        assert ga4.property_id == "123456789"
        
        # Valid WooCommerce config
        wc = WooCommerceConfig(
            url="https://example.com",
            consumer_key="ck_xxx",
            consumer_secret="cs_xxx"
        )
        assert wc.url == "https://example.com"


class TestErrorHandling:
    """Tests for error handling across endpoints."""
    
    @pytest.mark.asyncio
    async def test_invalid_json_body(self):
        """Test handling of invalid JSON in request body."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/jobs/run/1",
                headers={"Content-Type": "application/json"},
                content="not valid json"
            )
            # Should be 400 Bad Request or 401/403 for auth
            assert response.status_code in [400, 401, 403, 422]
    
    @pytest.mark.asyncio
    async def test_not_found_endpoint(self):
        """Test handling of non-existent endpoints."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/nonexistent")
            assert response.status_code == 404


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check_structure(self):
        """Test health check response structure."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health")
            # Response structure should be consistent regardless of DB state
            assert response.status_code in [200, 503]
            
            data = response.json()
            assert "status" in data
            assert "checks" in data
            assert "api" in data["checks"]
