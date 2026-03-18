"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_base_url() -> str:
    """Sample FogBugz base URL for testing."""
    return "https://example.manuscript.com"


@pytest.fixture
def sample_token() -> str:
    """Sample API token for testing."""
    return "test-token-12345"


@pytest.fixture
def sample_auth_config() -> dict[str, str]:
    """Sample authentication configuration."""
    return {
        "token": "test-token-12345",
        "base_url": "https://example.manuscript.com",
    }
