"""Configuration data models.

Defines the structure of FogBugz client configuration.
Used with dependency injection to support both pydantic and dict-based variants.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class HTTPConfig:
    """HTTP-level configuration.

    Attributes:
        timeout: Request timeout in seconds. Defaults to 30.
        max_retries: Maximum number of retry attempts. Defaults to 3.
        max_wait_seconds: Maximum wait time between retries. Defaults to 60.
    """

    timeout: int = 30
    max_retries: int = 3
    max_wait_seconds: int = 60


@dataclass
class FogBugzConfig:
    """Core FogBugz client configuration.

    This is the single source of truth for all client settings.
    Configuration is resolved once at client creation time.

    Attributes:
        base_url: FogBugz instance URL (e.g., https://example.manuscript.com).
        token: API authentication token (preferred over username/password).
        username: Username for authentication (deprecated, use token).
        password: Password for authentication (deprecated, use token).
        http: HTTP-level settings.
    """

    base_url: str
    token: str | None = None
    username: str | None = None
    password: str | None = None
    http: HTTPConfig | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.base_url:
            raise ValueError("base_url is required")

        if not self.http:
            self.http = HTTPConfig()

        # At least one auth method must be provided
        if not (self.token or (self.username and self.password)):
            raise ValueError(
                "No authentication method provided. Use token, or both username and password."
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of the configuration.
        """
        http_dict = {
            "timeout": self.http.timeout,
            "max_retries": self.http.max_retries,
            "max_wait_seconds": self.http.max_wait_seconds,
        }

        return {
            "base_url": self.base_url,
            "token": self.token,
            "username": self.username,
            "password": self.password,
            "http": http_dict,
        }
