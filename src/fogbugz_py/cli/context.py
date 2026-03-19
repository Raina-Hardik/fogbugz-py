"""CLI context and configuration resolution helpers."""

from __future__ import annotations

from dataclasses import dataclass

from fogbugz_py.config.loader import load_config


@dataclass(slots=True)
class CLIOptions:
    """Resolved CLI options that override config loading."""

    config_path: str | None = None
    base_url: str | None = None
    token: str | None = None
    username: str | None = None
    password: str | None = None
    timeout: int | None = None
    max_retries: int | None = None
    max_wait_seconds: int | None = None


def resolve_client_kwargs(options: CLIOptions) -> dict[str, object]:
    """Resolve full client kwargs from CLI options and config sources."""
    config = load_config(
        config_path=options.config_path,
        base_url=options.base_url,
        token=options.token,
        username=options.username,
        password=options.password,
        timeout=options.timeout,
        max_retries=options.max_retries,
        max_wait_seconds=options.max_wait_seconds,
    )

    return {
        "base_url": config.base_url,
        "token": config.token,
        "username": config.username,
        "password": config.password,
        "timeout": config.http.timeout,
        "max_retries": config.http.max_retries,
        "max_wait_seconds": config.http.max_wait_seconds,
    }
