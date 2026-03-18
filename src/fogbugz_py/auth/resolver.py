"""Resolve and apply authentication to HTTP requests.

Handles FogBugz authentication methods:
- API token (preferred)
- Username/password (deprecated)

Authentication is resolved once at client creation time.
"""

from __future__ import annotations

import logging
import warnings
from typing import TYPE_CHECKING, Any

from fogbugz_py.exceptions import FogBugzAuthError

if TYPE_CHECKING:
    from fogbugz_py.config.models import FogBugzConfig

logger = logging.getLogger("fogbugz_py.auth")


class AuthResolver:
    """Resolve and apply authentication to requests.

    Single source of truth for authentication state. Resolved once
    at client creation time.

    Attributes:
        config: The configuration containing auth credentials.
        auth_token: Resolved authentication token (if using token auth).
        auth_method: Type of auth used: 'token' or 'basic'.
    """

    def __init__(self, config: FogBugzConfig) -> None:
        """Initialize authentication resolver.

        Validates that at least one auth method is provided and
        resolves which method to use.

        Args:
            config: FogBugz configuration with credentials.

        Raises:
            FogBugzAuthError: If no valid auth method is provided.
        """
        self.config = config
        self.auth_token: str | None = None
        self.auth_method: str | None = None

        self._resolve_auth()

    def _resolve_auth(self) -> None:
        """Resolve which authentication method to use.

        Priority:
        1. API token (if provided)
        2. Username/password (if both provided)

        Raises:
            FogBugzAuthError: If no valid auth method found.
        """
        if self.config.token:
            self.auth_token = self.config.token
            self.auth_method = "token"
            logger.debug("Auth resolved: using API token")
        elif self.config.username and self.config.password:
            self.auth_method = "basic"
            logger.debug("Auth resolved: using username/password")
            warnings.warn(
                "Using username/password authentication is deprecated. "
                "Use API tokens for better security: "
                "https://api.manuscript.com/",
                DeprecationWarning,
                stacklevel=2,
            )
        else:
            raise FogBugzAuthError(
                "No authentication method provided. Use token, or both username and password."
            )

    def apply_to_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Apply authentication to request headers.

        Args:
            headers: Request headers dictionary (will be modified).

        Returns:
            Updated headers dictionary with auth applied.
        """
        if self.auth_method == "token":
            # FogBugz API expects token as query parameter or header
            # Using header approach (Bearer token style)
            headers["Authorization"] = f"Bearer {self.auth_token}"
        elif self.auth_method == "basic":
            # For basic auth, httpx handles it via auth parameter
            # This method just validates the method exists
            pass

        return headers

    def apply_to_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Apply authentication to query parameters.

        FogBugz API expects token as query parameter.

        Args:
            params: Query parameters dictionary (will be modified).

        Returns:
            Updated parameters dictionary with auth applied.
        """
        if self.auth_method == "token":
            # FogBugz API accepts token as query parameter
            params["token"] = self.auth_token

        return params

    def get_http_auth_tuple(self) -> tuple[str, str] | None:
        """Get HTTP Basic auth tuple if using username/password.

        Returns:
            Tuple of (username, password) for basic auth, or None if using token.
        """
        if self.auth_method == "basic":
            return (self.config.username or "", self.config.password or "")
        return None

    def validate(self) -> None:
        """Validate that authentication is properly configured.

        Raises:
            FogBugzAuthError: If auth is invalid or missing.
        """
        if not self.auth_method:
            raise FogBugzAuthError("No authentication method resolved")
