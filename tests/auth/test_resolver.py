"""Tests for authentication resolver.

Tests the auth system's ability to:
- Resolve authentication methods (token vs basic)
- Apply auth to requests
- Validate auth configuration
- Emit deprecation warnings for username/password
"""

from __future__ import annotations

import warnings

import pytest

from fogbugz_py.auth.resolver import AuthResolver
from fogbugz_py.config.models import FogBugzConfig
from fogbugz_py.exceptions import FogBugzAuthError


class TestAuthResolver:
    """Test AuthResolver class."""

    def test_resolve_with_token(self) -> None:
        """Resolve authentication using API token."""
        config = FogBugzConfig(
            base_url="https://example.com",
            token="my-token",
        )
        resolver = AuthResolver(config)

        assert resolver.auth_method == "token"
        assert resolver.auth_token == "my-token"

    def test_resolve_with_username_password(self) -> None:
        """Resolve authentication using username/password."""
        config = FogBugzConfig(
            base_url="https://example.com",
            username="user@example.com",
            password="secret",
        )
        resolver = AuthResolver(config)

        assert resolver.auth_method == "basic"
        assert resolver.config.username == "user@example.com"
        assert resolver.config.password == "secret"

    def test_token_preferred_over_password(self) -> None:
        """Token is preferred when both auth methods provided."""
        config = FogBugzConfig(
            base_url="https://example.com",
            token="my-token",
            username="user",
            password="pass",
        )
        resolver = AuthResolver(config)

        # Token should be chosen
        assert resolver.auth_method == "token"

    def test_missing_auth_raises_error(self) -> None:
        """Raise error when no auth method provided."""
        with pytest.raises(ValueError, match="No authentication method"):
            FogBugzConfig(
                base_url="https://example.com",
            )

    def test_apply_token_to_headers(self) -> None:
        """Apply token authentication to request headers."""
        config = FogBugzConfig(
            base_url="https://example.com",
            token="my-token",
        )
        resolver = AuthResolver(config)

        headers = {}
        headers = resolver.apply_to_headers(headers)

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer my-token"

    def test_apply_basic_auth_returns_tuple(self) -> None:
        """Get basic auth tuple for username/password."""
        config = FogBugzConfig(
            base_url="https://example.com",
            username="user@example.com",
            password="secret",
        )
        resolver = AuthResolver(config)

        auth_tuple = resolver.get_http_auth_tuple()
        assert auth_tuple == ("user@example.com", "secret")

    def test_token_auth_returns_none_for_basic_tuple(self) -> None:
        """Token auth does not return basic auth tuple."""
        config = FogBugzConfig(
            base_url="https://example.com",
            token="my-token",
        )
        resolver = AuthResolver(config)

        auth_tuple = resolver.get_http_auth_tuple()
        assert auth_tuple is None

    def test_deprecation_warning_for_password_auth(self) -> None:
        """Emit deprecation warning for username/password auth."""
        config = FogBugzConfig(
            base_url="https://example.com",
            username="user",
            password="pass",
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            AuthResolver(config)

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert "token" in str(w[0].message).lower()

    def test_validate_auth_passes_when_resolved(self) -> None:
        """Validation passes when auth is properly resolved."""
        config = FogBugzConfig(
            base_url="https://example.com",
            token="my-token",
        )
        resolver = AuthResolver(config)

        # Should not raise
        resolver.validate()

    def test_validate_auth_fails_when_not_resolved(self) -> None:
        """Validation fails if auth method is not set."""
        config = FogBugzConfig(
            base_url="https://example.com",
            token="my-token",
        )
        resolver = AuthResolver(config)
        resolver.auth_method = None

        with pytest.raises(FogBugzAuthError, match="No authentication method"):
            resolver.validate()

    def test_apply_to_params(self) -> None:
        """Apply authentication to query parameters."""
        config = FogBugzConfig(
            base_url="https://example.com",
            token="my-token",
        )
        resolver = AuthResolver(config)

        params = {"q": "search"}
        result = resolver.apply_to_params(params)

        # FogBugz API expects token as query parameter
        assert result == {"q": "search", "token": "my-token"}
