"""Load and resolve FogBugz configuration from multiple sources.

Configuration resolution follows a priority order:
1. Explicit arguments (highest priority)
2. Explicit config file path
3. Project-local config (./.fogbugz/config.toml or ./config.toml)
4. User config (~/.fogbugz/config.toml)
5. Environment variables (lowest priority)

Uses dependency injection pattern to avoid hard Pydantic dependency,
allowing the slim variant to work with plain dicts.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

from fogbugz_py.config.models import FogBugzConfig, HTTPConfig
from fogbugz_py.exceptions import FogBugzConfigError


def _expand_path(path: str) -> Path:
    """Expand ~ and environment variables in file path.

    Args:
        path: Path string potentially containing ~ or env vars.

    Returns:
        Expanded Path object.
    """
    expanded = Path(path).expanduser()
    return Path(os.path.expandvars(str(expanded)))


def _load_toml_file(path: Path) -> dict[str, Any]:
    """Load TOML configuration file.

    Args:
        path: Path to TOML file.

    Returns:
        Parsed TOML data as dictionary.

    Raises:
        FogBugzConfigError: If file cannot be read or parsed.
    """
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except FileNotFoundError as e:
        raise FogBugzConfigError(f"Config file not found: {path}", config_path=str(path)) from e
    except Exception as e:
        raise FogBugzConfigError(
            f"Failed to parse config file {path}: {e}",
            config_path=str(path),
        ) from e


def _find_project_config() -> Path | None:
    """Discover project-local config file.

    Searches for:
    1. ./.fogbugz/config.toml
    2. ./config.toml

    Returns:
        Path to found config file, or None if not found.
    """
    cwd = Path.cwd()

    # Check .fogbugz/config.toml first
    fogbugz_dir = cwd / ".fogbugz" / "config.toml"
    if fogbugz_dir.exists():
        return fogbugz_dir

    # Check ./config.toml
    root_config = cwd / "config.toml"
    if root_config.exists():
        return root_config

    return None


def _find_user_config() -> Path | None:
    """Discover user-level config file.

    Looks for ~/.fogbugz/config.toml

    Returns:
        Path to found config file, or None if not found.
    """
    user_config = _expand_path("~/.fogbugz/config.toml")
    if user_config.exists():
        return user_config
    return None


def _get_env_vars() -> dict[str, Any]:
    """Extract FogBugz environment variables.

    Looks for FOGBUGZ_* prefixed variables and converts them to config keys.

    Returns:
        Dictionary mapping config keys to env var values.
    """
    env_config: dict[str, Any] = {}

    if base_url := os.getenv("FOGBUGZ_BASE_URL"):
        env_config["base_url"] = base_url

    if token := os.getenv("FOGBUGZ_TOKEN"):
        env_config["token"] = token

    if username := os.getenv("FOGBUGZ_USERNAME"):
        env_config["username"] = username

    if password := os.getenv("FOGBUGZ_PASSWORD"):
        env_config["password"] = password

    # HTTP config - nested under 'http' key
    http_config: dict[str, int] = {}

    if timeout := os.getenv("FOGBUGZ_TIMEOUT"):
        try:
            http_config["timeout"] = int(timeout)
        except ValueError as e:
            raise FogBugzConfigError(
                f"Invalid FOGBUGZ_TIMEOUT value: {timeout} (must be integer)"
            ) from e

    if max_retries := os.getenv("FOGBUGZ_MAX_RETRIES"):
        try:
            http_config["max_retries"] = int(max_retries)
        except ValueError as e:
            raise FogBugzConfigError(
                f"Invalid FOGBUGZ_MAX_RETRIES value: {max_retries} (must be integer)"
            ) from e

    if max_wait := os.getenv("FOGBUGZ_MAX_WAIT_SECONDS"):
        try:
            http_config["max_wait_seconds"] = int(max_wait)
        except ValueError as e:
            raise FogBugzConfigError(
                f"Invalid FOGBUGZ_MAX_WAIT_SECONDS value: {max_wait} (must be integer)"
            ) from e

    if http_config:
        env_config["http"] = http_config

    return env_config


def _merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple config dictionaries with nested HTTP config.

    Later dictionaries override earlier ones. Handles nested 'http' key.

    Args:
        *configs: Configuration dictionaries to merge.

    Returns:
        Merged configuration dictionary.
    """
    merged: dict[str, Any] = {}

    for config in configs:
        if not config:
            continue

        for key, value in config.items():
            if key == "http" and isinstance(value, dict):
                # Handle nested HTTP config
                if "http" not in merged:
                    merged["http"] = {}
                if isinstance(merged["http"], dict):
                    merged["http"].update(value)
            else:
                merged[key] = value

    return merged


def _collect_config_sources(
    config_path: str | Path | None,
    skip_project_config: bool,
    skip_user_config: bool,
) -> list[dict[str, Any]]:
    """Collect configuration from all available sources.

    Follows priority order (lowest to highest):
    1. Environment variables
    2. User config (~/.fogbugz/config.toml)
    3. Project config (./.fogbugz/config.toml or ./config.toml)
    4. Explicit config file path

    Args:
        config_path: Optional explicit path to config file.
        skip_project_config: Skip project-local config discovery.
        skip_user_config: Skip user-level config discovery.

    Returns:
        List of config dictionaries in priority order.
    """
    configs: list[dict[str, Any]] = []

    # Lowest priority: environment variables
    configs.append(_get_env_vars())

    # User config
    if not skip_user_config:
        user_config_path = _find_user_config()
        if user_config_path:
            user_data = _load_toml_file(user_config_path)
            config_section = user_data.get("fogbugz", user_data)
            configs.append(config_section)

    # Project config
    if not skip_project_config:
        project_config_path = _find_project_config()
        if project_config_path:
            project_data = _load_toml_file(project_config_path)
            config_section = project_data.get("fogbugz", project_data)
            configs.append(config_section)

    # Highest priority: explicit config file
    if config_path:
        explicit_path = _expand_path(str(config_path))
        explicit_data = _load_toml_file(explicit_path)
        config_section = explicit_data.get("fogbugz", explicit_data)
        configs.append(config_section)

    return configs


def _apply_argument_overrides(
    config: dict[str, Any],
    *,
    base_url: str | None = None,
    token: str | None = None,
    username: str | None = None,
    password: str | None = None,
    timeout: int | None = None,
    max_retries: int | None = None,
    max_wait_seconds: int | None = None,
) -> None:
    """Apply explicit argument overrides to configuration (in-place).

    These arguments have the highest priority and override all other sources.

    Args:
        config: Configuration dictionary to modify.
        base_url: FogBugz instance URL.
        token: API token.
        username: Username for auth.
        password: Password for auth.
        timeout: HTTP timeout in seconds.
        max_retries: Maximum retry attempts.
        max_wait_seconds: Maximum wait between retries.
    """
    # Top-level overrides
    if base_url is not None:
        config["base_url"] = base_url
    if token is not None:
        config["token"] = token
    if username is not None:
        config["username"] = username
    if password is not None:
        config["password"] = password

    # HTTP config overrides
    if not config.get("http"):
        config["http"] = {}

    if timeout is not None:
        config["http"]["timeout"] = timeout
    if max_retries is not None:
        config["http"]["max_retries"] = max_retries
    if max_wait_seconds is not None:
        config["http"]["max_wait_seconds"] = max_wait_seconds


def _build_http_config(http_data: Any) -> HTTPConfig:
    """Create HTTPConfig from raw data.

    Args:
        http_data: HTTP configuration data.

    Returns:
        HTTPConfig instance.

    Raises:
        FogBugzConfigError: If HTTP config is invalid.
    """
    if isinstance(http_data, HTTPConfig):
        return http_data
    return HTTPConfig(**http_data) if isinstance(http_data, dict) else HTTPConfig()


def _build_fogbugz_config(config: dict[str, Any]) -> FogBugzConfig:
    """Create FogBugzConfig from merged configuration dictionary.

    Args:
        config: Merged configuration dictionary.

    Returns:
        FogBugzConfig instance.

    Raises:
        FogBugzConfigError: If config is invalid.
    """
    http_data = config.pop("http", {})
    http_config = _build_http_config(http_data)

    try:
        return FogBugzConfig(
            base_url=config.get("base_url", ""),
            token=config.get("token"),
            username=config.get("username"),
            password=config.get("password"),
            http=http_config,
        )
    except ValueError as e:
        raise FogBugzConfigError(str(e)) from e


def load_config(
    config_path: str | Path | None = None,
    *,
    base_url: str | None = None,
    token: str | None = None,
    username: str | None = None,
    password: str | None = None,
    timeout: int | None = None,
    max_retries: int | None = None,
    max_wait_seconds: int | None = None,
    skip_project_config: bool = False,
    skip_user_config: bool = False,
) -> FogBugzConfig:
    """Load configuration from multiple sources.

    Configuration is merged in order of priority:
    1. Explicit arguments (highest priority)
    2. Explicit config file path
    3. Project-local config (./.fogbugz/config.toml or ./config.toml)
    4. User config (~/.fogbugz/config.toml)
    5. Environment variables (lowest priority)

    Args:
        config_path: Explicit path to TOML config file.
        base_url: FogBugz instance URL (overrides all other sources).
        token: API token (overrides all other sources).
        username: Username for auth (overrides all other sources).
        password: Password for auth (overrides all other sources).
        timeout: HTTP timeout in seconds.
        max_retries: Maximum retry attempts.
        max_wait_seconds: Maximum wait between retries.
        skip_project_config: Skip searching for project-local config.
        skip_user_config: Skip searching for user-level config.

    Returns:
        Resolved FogBugzConfig instance.

    Raises:
        FogBugzConfigError: If config is invalid or required fields missing.

    Example:
        Load from defaults and environment:
        >>> config = load_config()

        Load from explicit file:
        >>> config = load_config("path/to/config.toml")

        Load from file with overrides:
        >>> config = load_config(
        ...     "config.toml",
        ...     token="override-token"  # This token takes precedence
        ... )
    """
    # Collect configs from all sources in priority order
    config_sources = _collect_config_sources(config_path, skip_project_config, skip_user_config)

    # Merge all sources (later sources override earlier ones)
    merged = _merge_configs(*config_sources)

    # Apply explicit argument overrides (highest priority)
    _apply_argument_overrides(
        merged,
        base_url=base_url,
        token=token,
        username=username,
        password=password,
        timeout=timeout,
        max_retries=max_retries,
        max_wait_seconds=max_wait_seconds,
    )

    # Build and return the final configuration
    return _build_fogbugz_config(merged)
