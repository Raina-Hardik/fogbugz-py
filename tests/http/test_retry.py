"""Tests for retry logic and configuration.

Tests the retry strategy's ability to:
- Configure retry behavior
- Determine which errors are retryable
- Log retry attempts
- Validate configuration
"""

from __future__ import annotations

import pytest

from fogbugz_py.exceptions import (
    FogBugzAuthError,
    FogBugzClientError,
    FogBugzServerError,
    FogBugzTransportError,
)
from fogbugz_py.http.retry import RetryConfig, RetryStrategy


class TestRetryConfig:
    """Test RetryConfig data model."""

    def test_retry_config_defaults(self) -> None:
        """Test default retry configuration."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.max_wait_seconds == 60
        assert config.retry_on_timeout is True

    def test_retry_config_custom(self) -> None:
        """Allow customizing retry configuration."""
        config = RetryConfig(
            max_attempts=5,
            max_wait_seconds=120,
            retry_on_timeout=False,
        )
        assert config.max_attempts == 5
        assert config.max_wait_seconds == 120
        assert config.retry_on_timeout is False


class TestRetryStrategy:
    """Test RetryStrategy retry logic."""

    def test_strategy_with_default_config(self) -> None:
        """Create retry strategy with default config."""
        strategy = RetryStrategy()
        assert strategy.config.max_attempts == 3
        assert strategy.config.max_wait_seconds == 60

    def test_strategy_with_custom_config(self) -> None:
        """Create retry strategy with custom config."""
        config = RetryConfig(max_attempts=10, max_wait_seconds=180)
        strategy = RetryStrategy(config)
        assert strategy.config.max_attempts == 10
        assert strategy.config.max_wait_seconds == 180

    def test_validate_max_attempts_must_be_positive(self) -> None:
        """Reject invalid max_attempts value."""
        with pytest.raises(ValueError, match="max_attempts must be >= 1"):
            config = RetryConfig(max_attempts=0)
            RetryStrategy(config)

    def test_validate_max_wait_must_be_positive(self) -> None:
        """Reject invalid max_wait_seconds value."""
        with pytest.raises(ValueError, match="max_wait_seconds must be >= 1"):
            config = RetryConfig(max_wait_seconds=0)
            RetryStrategy(config)

    def test_retry_transport_error(self) -> None:
        """Transport errors are retryable."""
        strategy = RetryStrategy()
        error = FogBugzTransportError("Network error")
        assert strategy.should_retry(error) is True

    def test_retry_server_error(self) -> None:
        """Server errors (5xx) are retryable."""
        strategy = RetryStrategy()
        error = FogBugzServerError(
            "Internal server error",
            status_code=500,
        )
        assert strategy.should_retry(error) is True

    def test_dont_retry_client_error(self) -> None:
        """Client errors (4xx) are not retryable."""
        strategy = RetryStrategy()
        error = FogBugzClientError(
            "Bad request",
            status_code=400,
        )
        assert strategy.should_retry(error) is False

    def test_dont_retry_auth_error(self) -> None:
        """Auth errors (401/403) are not retryable."""
        strategy = RetryStrategy()
        error = FogBugzAuthError("Unauthorized")
        assert strategy.should_retry(error) is False

    def test_timeout_respects_retry_on_timeout_flag(self) -> None:
        """Respect retry_on_timeout configuration."""
        # With retry_on_timeout=True (default)
        strategy_retry = RetryStrategy(RetryConfig(retry_on_timeout=True))
        timeout_error = FogBugzTransportError("Request timeout")
        assert strategy_retry.should_retry(timeout_error) is True

        # With retry_on_timeout=False
        strategy_no_retry = RetryStrategy(RetryConfig(retry_on_timeout=False))
        assert strategy_no_retry.should_retry(timeout_error) is False

    def test_log_retry(self) -> None:
        """Log retry attempts."""
        strategy = RetryStrategy()
        error = FogBugzTransportError("Connection reset")

        # Should not raise
        strategy.log_retry(1, error, 1.0)
        strategy.log_retry(2, error, 2.0)

    def test_log_exhausted(self) -> None:
        """Log when retries are exhausted."""
        strategy = RetryStrategy()
        error = FogBugzTransportError("Connection reset")

        # Should not raise
        strategy.log_exhausted(error)

    def test_get_decorator(self) -> None:
        """Get Tenacity retry decorator."""
        strategy = RetryStrategy()
        decorator = strategy.get_decorator()

        # Decorator should be callable and configured
        assert decorator is not None
        assert callable(decorator)
