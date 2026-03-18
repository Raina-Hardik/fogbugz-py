"""Quick smoke tests for basic functionality."""

from __future__ import annotations


def test_import_client() -> None:
    """Test that we can import the main client."""
    from fogbugz_py import FogBugzClient

    assert FogBugzClient is not None


def test_import_exceptions() -> None:
    """Test that we can import exceptions."""
    from fogbugz_py import (
        FogBugzAuthError,
        FogBugzError,
        FogBugzHTTPError,
    )

    assert FogBugzError is not None
    assert FogBugzHTTPError is not None
    assert FogBugzAuthError is not None


def test_version() -> None:
    """Test that version is defined."""
    from fogbugz_py import __version__

    assert __version__ == "0.1.0"


def test_retry_config_creation() -> None:
    """Test creating a retry config."""
    from fogbugz_py.http.retry import RetryConfig

    config = RetryConfig(max_attempts=5)
    assert config.max_attempts == 5
    assert config.max_wait_seconds == 60


def test_auth_resolution_basic() -> None:
    """Test basic authentication resolution."""
    from fogbugz_py.auth.resolver import AuthResolver
    from fogbugz_py.config.models import FogBugzConfig

    config = FogBugzConfig(
        base_url="https://example.com",
        token="test",
    )
    resolver = AuthResolver(config)
    assert resolver.auth_method == "token"
    assert resolver.auth_token == "test"
