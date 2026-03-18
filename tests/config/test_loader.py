"""Tests for configuration loading and resolution.

Tests the configuration system's ability to:
- Load from TOML files
- Resolve configuration priority (explicit > project > user > env)
- Validate required fields
- Handle environment variables
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from fogbugz_py.config.loader import load_config
from fogbugz_py.config.models import FogBugzConfig, HTTPConfig
from fogbugz_py.exceptions import FogBugzConfigError


class TestConfigModels:
    """Test FogBugzConfig and HTTPConfig data models."""

    def test_http_config_defaults(self) -> None:
        """Verify HTTP config has sensible defaults."""
        http = HTTPConfig()
        assert http.timeout == 30
        assert http.max_retries == 3
        assert http.max_wait_seconds == 60

    def test_http_config_custom(self) -> None:
        """Allow customizing HTTP config values."""
        http = HTTPConfig(timeout=60, max_retries=5, max_wait_seconds=120)
        assert http.timeout == 60
        assert http.max_retries == 5
        assert http.max_wait_seconds == 120

    def test_fogbugz_config_requires_base_url(self) -> None:
        """Require base_url in FogBugzConfig."""
        with pytest.raises(ValueError, match="base_url is required"):
            FogBugzConfig(base_url="", token="test")

    def test_fogbugz_config_requires_auth(self) -> None:
        """Require at least one auth method."""
        with pytest.raises(ValueError, match="No authentication method"):
            FogBugzConfig(base_url="https://example.com")

    def test_fogbugz_config_with_token(self) -> None:
        """Create config with token authentication."""
        config = FogBugzConfig(
            base_url="https://example.com",
            token="my-token",
        )
        assert config.base_url == "https://example.com"
        assert config.token == "my-token"
        assert config.http is not None

    def test_fogbugz_config_with_username_password(self) -> None:
        """Create config with username/password authentication."""
        config = FogBugzConfig(
            base_url="https://example.com",
            username="user@example.com",
            password="secret",
        )
        assert config.username == "user@example.com"
        assert config.password == "secret"

    def test_fogbugz_config_to_dict(self) -> None:
        """Convert config to dictionary."""
        config = FogBugzConfig(
            base_url="https://example.com",
            token="my-token",
            http=HTTPConfig(timeout=60),
        )
        data = config.to_dict()
        assert data["base_url"] == "https://example.com"
        assert data["token"] == "my-token"
        assert data["http"]["timeout"] == 60


class TestConfigLoader:
    """Test load_config function and resolution order."""

    def test_load_with_explicit_args(self) -> None:
        """Load config from explicit arguments (highest priority)."""
        config = load_config(
            base_url="https://explicit.com",
            token="explicit-token",
            skip_project_config=True,
            skip_user_config=True,
        )
        assert config.base_url == "https://explicit.com"
        assert config.token == "explicit-token"

    def test_load_with_env_vars(self) -> None:
        """Load config from environment variables."""
        with mock.patch.dict(
            os.environ,
            {
                "FOGBUGZ_BASE_URL": "https://env.com",
                "FOGBUGZ_TOKEN": "env-token",
            },
        ):
            config = load_config(skip_project_config=True, skip_user_config=True)
            assert config.base_url == "https://env.com"
            assert config.token == "env-token"

    def test_explicit_args_override_env_vars(self) -> None:
        """Explicit arguments override environment variables."""
        with mock.patch.dict(
            os.environ,
            {
                "FOGBUGZ_BASE_URL": "https://env.com",
                "FOGBUGZ_TOKEN": "env-token",
            },
        ):
            config = load_config(
                token="explicit-token",
                skip_project_config=True,
                skip_user_config=True,
            )
            assert config.token == "explicit-token"
            assert config.base_url == "https://env.com"

    def test_load_from_toml_file(self) -> None:
        """Load configuration from TOML file."""
        toml_content = """
[fogbugz]
base_url = "https://example.com"
token = "file-token"

[fogbugz.http]
timeout = 60
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text(toml_content)

            config = load_config(
                str(config_path),
                skip_project_config=True,
                skip_user_config=True,
            )
            assert config.base_url == "https://example.com"
            assert config.token == "file-token"
            assert config.http.timeout == 60

    def test_load_toml_without_fogbugz_section(self) -> None:
        """Handle TOML files without [fogbugz] section."""
        toml_content = """
base_url = "https://example.com"
token = "file-token"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text(toml_content)

            config = load_config(
                str(config_path),
                skip_project_config=True,
                skip_user_config=True,
            )
            assert config.base_url == "https://example.com"
            assert config.token == "file-token"

    def test_explicit_file_overrides_env(self) -> None:
        """Explicit config file overrides environment variables."""
        toml_content = """
base_url = "https://file.com"
token = "file-token"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text(toml_content)

            with mock.patch.dict(
                os.environ,
                {"FOGBUGZ_TOKEN": "env-token"},
            ):
                config = load_config(
                    str(config_path),
                    skip_project_config=True,
                    skip_user_config=True,
                )
                assert config.token == "file-token"

    def test_invalid_toml_file(self) -> None:
        """Raise FogBugzConfigError for invalid TOML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text("invalid toml content [[[")

            with pytest.raises(FogBugzConfigError):
                load_config(
                    str(config_path),
                    skip_project_config=True,
                    skip_user_config=True,
                )

    def test_missing_toml_file(self) -> None:
        """Raise FogBugzConfigError for missing file."""
        with pytest.raises(FogBugzConfigError, match="Config file not found"):
            load_config(
                "/nonexistent/path/config.toml",
                skip_project_config=True,
                skip_user_config=True,
            )

    def test_env_var_timeout_parsing(self) -> None:
        """Parse timeout from environment variable."""
        with mock.patch.dict(
            os.environ,
            {
                "FOGBUGZ_BASE_URL": "https://example.com",
                "FOGBUGZ_TOKEN": "token",
                "FOGBUGZ_TIMEOUT": "120",
            },
        ):
            config = load_config(skip_project_config=True, skip_user_config=True)
            assert config.http.timeout == 120

    def test_env_var_invalid_timeout(self) -> None:
        """Raise error for invalid timeout value in env var."""
        with (
            mock.patch.dict(
                os.environ,
                {
                    "FOGBUGZ_BASE_URL": "https://example.com",
                    "FOGBUGZ_TOKEN": "token",
                    "FOGBUGZ_TIMEOUT": "not-a-number",
                },
            ),
            pytest.raises(FogBugzConfigError, match="Invalid FOGBUGZ_TIMEOUT"),
        ):
            load_config(skip_project_config=True, skip_user_config=True)

    def test_skip_project_and_user_config(self) -> None:
        """Skip auto-discovery when explicitly requested."""
        with mock.patch.dict(
            os.environ,
            {
                "FOGBUGZ_BASE_URL": "https://env.com",
                "FOGBUGZ_TOKEN": "token",
            },
        ):
            config = load_config(
                skip_project_config=True,
                skip_user_config=True,
            )
            assert config.base_url == "https://env.com"

    def test_username_password_auth(self) -> None:
        """Support username/password authentication."""
        config = load_config(
            base_url="https://example.com",
            username="user@example.com",
            password="secret",
            skip_project_config=True,
            skip_user_config=True,
        )
        assert config.username == "user@example.com"
        assert config.password == "secret"

    def test_http_config_overrides(self) -> None:
        """Apply HTTP config parameter overrides."""
        config = load_config(
            base_url="https://example.com",
            token="token",
            timeout=90,
            max_retries=10,
            max_wait_seconds=180,
            skip_project_config=True,
            skip_user_config=True,
        )
        assert config.http.timeout == 90
        assert config.http.max_retries == 10
        assert config.http.max_wait_seconds == 180
