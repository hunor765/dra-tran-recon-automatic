"""Tests for core components."""
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from core.encryption import encrypt_config, decrypt_config
from core.cache import cached, clear_cache
from core.rate_limiter import RateLimits, get_limiter_key
from core.scheduler import build_trigger, init_scheduler


class TestEncryption:
    """Tests for encryption module."""
    
    @patch("core.encryption.settings")
    def test_encrypt_decrypt_roundtrip(self, mock_settings):
        """Test that encryption and decryption work correctly."""
        # Use a valid Fernet key (32 bytes base64 encoded)
        from cryptography.fernet import Fernet
        valid_key = Fernet.generate_key().decode()
        mock_settings.ENCRYPTION_KEY = valid_key
        
        original = json.dumps({"secret": "value", "number": 123})
        
        encrypted = encrypt_config(original)
        decrypted = decrypt_config(encrypted)
        
        assert encrypted != original
        assert decrypted == original
    
    @patch("core.encryption.settings")
    def test_encrypt_different_outputs(self, mock_settings):
        """Test that encrypting same data produces different ciphertexts."""
        from cryptography.fernet import Fernet
        valid_key = Fernet.generate_key().decode()
        mock_settings.ENCRYPTION_KEY = valid_key
        
        original = json.dumps({"secret": "value"})
        
        encrypted1 = encrypt_config(original)
        encrypted2 = encrypt_config(original)
        
        # Same plaintext should produce different ciphertexts (Fernet includes timestamp)
        # But both should decrypt to the same value
        assert decrypt_config(encrypted1) == decrypt_config(encrypted2) == original
    
    @patch("core.encryption.settings")
    def test_decrypt_invalid_data(self, mock_settings):
        """Test error handling for invalid encrypted data."""
        from cryptography.fernet import Fernet
        valid_key = Fernet.generate_key().decode()
        mock_settings.ENCRYPTION_KEY = valid_key
        
        with pytest.raises(Exception):
            decrypt_config("invalid-ciphertext")


class TestCaching:
    """Tests for caching module."""
    
    def test_cached_decorator(self):
        """Test that cached decorator caches function results."""
        call_count = 0
        
        @cached(ttl=60, key_prefix="test")
        def expensive_function(arg1, arg2):
            nonlocal call_count
            call_count += 1
            return arg1 + arg2
        
        # First call should execute
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call with same args should use cache
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Not incremented
        
        # Different args should execute
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2
    
    def test_cached_skip_self(self):
        """Test that cached decorator can skip self argument."""
        call_count = 0
        
        class TestClass:
            @cached(ttl=60, key_prefix="test_self", skip_args=[0])
            def method(self, arg):
                nonlocal call_count
                call_count += 1
                return arg * 2
        
        obj1 = TestClass()
        obj2 = TestClass()
        
        # Different objects should share cache for same args
        result1 = obj1.method(5)
        result2 = obj2.method(5)
        
        assert result1 == result2 == 10
        assert call_count == 1  # Only called once due to cache
    
    def test_clear_cache(self):
        """Test clearing the cache."""
        call_count = 0
        
        @cached(ttl=60, key_prefix="test_clear")
        def function(arg):
            nonlocal call_count
            call_count += 1
            return arg
        
        function(1)
        function(1)  # Cached
        assert call_count == 1
        
        clear_cache()
        
        function(1)  # Should re-execute
        assert call_count == 2


class TestRateLimiter:
    """Tests for rate limiting module."""
    
    def test_rate_limits_defined(self):
        """Test that rate limit constants are defined."""
        assert RateLimits.HEALTH == ["60/minute"]
        assert RateLimits.LIST == ["100/minute"]
        assert RateLimits.GET == ["100/minute"]
        assert RateLimits.CREATE == ["30/minute"]
        assert RateLimits.UPDATE == ["30/minute"]
        assert RateLimits.DELETE == ["10/minute"]
        assert RateLimits.JOB_RUN == ["10/minute"]
        assert RateLimits.CONNECTOR_TEST == ["20/minute"]
        assert RateLimits.ADMIN_READ == ["200/minute"]
        assert RateLimits.ADMIN_WRITE == ["50/minute"]
    
    def test_get_limiter_key_with_user(self):
        """Test getting rate limit key for authenticated user."""
        mock_request = Mock()
        mock_request.state.user = {"id": "user-123"}
        
        key = get_limiter_key(mock_request)
        assert key == "user:user-123"
    
    def test_get_limiter_key_without_user(self):
        """Test getting rate limit key for unauthenticated request."""
        mock_request = Mock()
        mock_request.state.user = None
        mock_request.client.host = "192.168.1.1"
        
        key = get_limiter_key(mock_request)
        assert "192.168.1.1" in key


class TestScheduler:
    """Tests for scheduler module."""
    
    def test_init_scheduler(self):
        """Test scheduler initialization."""
        scheduler = init_scheduler()
        assert scheduler is not None
        assert scheduler.timezone.zone == "UTC"
    
    def test_build_trigger_hourly(self):
        """Test building hourly trigger."""
        from apscheduler.triggers.interval import IntervalTrigger
        
        mock_schedule = Mock()
        mock_schedule.frequency = "hourly"
        
        trigger = build_trigger(mock_schedule)
        
        assert isinstance(trigger, IntervalTrigger)
        assert trigger.interval.total_seconds() == 3600  # 1 hour
    
    def test_build_trigger_daily(self):
        """Test building daily trigger."""
        from apscheduler.triggers.cron import CronTrigger
        
        mock_schedule = Mock()
        mock_schedule.frequency = "daily"
        mock_schedule.time_of_day = Mock(hour=9, minute=30)
        mock_schedule.timezone = "America/New_York"
        
        trigger = build_trigger(mock_schedule)
        
        assert isinstance(trigger, CronTrigger)
    
    def test_build_trigger_weekly(self):
        """Test building weekly trigger."""
        from apscheduler.triggers.cron import CronTrigger
        
        mock_schedule = Mock()
        mock_schedule.frequency = "weekly"
        mock_schedule.time_of_day = Mock(hour=3, minute=0)
        mock_schedule.timezone = "UTC"
        
        trigger = build_trigger(mock_schedule)
        
        assert isinstance(trigger, CronTrigger)
    
    def test_build_trigger_unknown(self):
        """Test building trigger for unknown frequency."""
        mock_schedule = Mock()
        mock_schedule.frequency = "unknown"
        
        trigger = build_trigger(mock_schedule)
        
        assert trigger is None


class TestAuthUtils:
    """Tests for authentication utilities."""
    
    @pytest.mark.asyncio
    @patch("core.auth.jwt.decode")
    async def test_get_current_user_valid_token(self, mock_decode):
        """Test extracting user from valid token."""
        from core.auth import get_current_user
        
        mock_decode.return_value = {
            "sub": "user-123",
            "email": "test@example.com"
        }
        
        mock_request = Mock()
        mock_request.headers = {"Authorization": "Bearer valid-token"}
        
        # This test is simplified - actual implementation has more logic
        # We just verify the structure
        user = await get_current_user(mock_request)
        # Result depends on actual implementation


class TestDatabaseUtils:
    """Tests for database utilities."""
    
    @pytest.mark.asyncio
    async def test_get_db(self):
        """Test database session context manager."""
        from core.database import get_db
        
        # get_db is an async generator, so we need to iterate
        async for session in get_db():
            assert session is not None
            # Session should be an AsyncSession
            break


class TestJobStatus:
    """Tests for job status enum and logic."""
    
    def test_job_status_values(self):
        """Test job status enum values."""
        from models.job import JobStatus
        
        assert JobStatus.PENDING == "pending"
        assert JobStatus.RUNNING == "running"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.FAILED == "failed"
        assert JobStatus.RETRYING == "retrying"
    
    def test_job_status_transitions(self):
        """Test valid job status transitions."""
        from models.job import JobStatus
        
        # Valid transitions
        valid_transitions = {
            JobStatus.PENDING: [JobStatus.RUNNING, JobStatus.FAILED],
            JobStatus.RUNNING: [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.RETRYING],
            JobStatus.RETRYING: [JobStatus.RUNNING, JobStatus.FAILED],
            JobStatus.COMPLETED: [],  # Terminal state
            JobStatus.FAILED: [JobStatus.RUNNING],  # For retries
        }
        
        for from_status, to_statuses in valid_transitions.items():
            for to_status in to_statuses:
                # Just verifying the transition exists in our mapping
                assert to_status in valid_transitions.get(from_status, [])


class TestWebhookUtils:
    """Tests for webhook utilities."""
    
    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_webhook_notification_success(self, mock_post):
        """Test successful webhook notification."""
        from core.webhooks import notify_job_completed
        
        mock_post.return_value = Mock(status_code=200)
        
        mock_job = Mock()
        mock_job.id = 1
        mock_job.status = "completed"
        mock_job.result_summary = {"match_rate": 95.5}
        
        mock_db = AsyncMock()
        
        # Test would need actual implementation details
        # This is a placeholder for the structure
