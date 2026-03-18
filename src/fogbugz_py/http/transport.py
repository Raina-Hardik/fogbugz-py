"""HTTP transport layer using httpx.

Provides async HTTP communication with FogBugz API, including:
- Request/response handling
- Automatic error detection and conversion
- Retry logic integration
- Request logging
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import httpx

from fogbugz_py.exceptions import (
    FogBugzAuthError,
    FogBugzClientError,
    FogBugzNotFoundError,
    FogBugzServerError,
    FogBugzTransportError,
)
from fogbugz_py.http.retry import RetryConfig, RetryStrategy

if TYPE_CHECKING:
    from fogbugz_py.auth.resolver import AuthResolver
    from fogbugz_py.config.models import FogBugzConfig

logger = logging.getLogger("fogbugz_py.http.transport")


class AsyncTransport:
    """Async HTTP transport using httpx.AsyncClient.

    Handles low-level HTTP communication with FogBugz API, including:
    - Request building and execution
    - Response parsing
    - Error handling and conversion
    - Retry integration
    - Request/response logging

    Attributes:
        config: FogBugz configuration.
        auth: Authentication resolver.
        retry_strategy: Retry strategy for transient failures.
        client: httpx.AsyncClient instance (created on context entry).
    """

    def __init__(
        self,
        config: FogBugzConfig,
        auth: AuthResolver,
        retry_config: RetryConfig | None = None,
    ) -> None:
        """Initialize transport.

        Args:
            config: FogBugz configuration with base_url and HTTP settings.
            auth: Resolved authentication handler.
            retry_config: Retry strategy configuration. Uses config.http settings if not provided.
        """
        self.config = config
        self.auth = auth

        # Use retry config from parameter or derive from config.http
        if retry_config is None:
            retry_config = RetryConfig(
                max_attempts=config.http.max_retries,
                max_wait_seconds=config.http.max_wait_seconds,
            )

        self.retry_strategy = RetryStrategy(retry_config)
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> AsyncTransport:
        """Enter async context manager.

        Creates and stores the httpx.AsyncClient.

        Returns:
            Self for use in async with statement.
        """
        # Create httpx client with configured timeout
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.http.timeout,
        )
        logger.debug("Created async HTTP client for %s", self.config.base_url)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager.

        Closes the httpx.AsyncClient.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.
        """
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.debug("Closed async HTTP client")

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request with retry logic.

        Automatically applies authentication, handles errors, and retries
        transient failures.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (relative to base_url)
            params: Query parameters
            json: JSON request body
            headers: HTTP headers (will be merged with auth headers)

        Returns:
            Parsed JSON response as dictionary

        Raises:
            FogBugzAuthError: If authentication fails (401/403)
            FogBugzNotFoundError: If resource not found (404)
            FogBugzClientError: For other 4xx client errors
            FogBugzServerError: For 5xx server errors
            FogBugzTransportError: For network errors

        Example:
            >>> async with AsyncTransport(config, auth) as transport:
            ...     response = await transport.request(
            ...         "GET",
            ...         "/f/api/0/jsonapi",
            ...         params={"q": "status:open"}
            ...     )
        """
        if not self.client:
            raise RuntimeError("Transport not initialized. Use 'async with' context manager.")

        # Prepare headers with authentication
        headers = headers or {}
        headers = self.auth.apply_to_headers(headers)

        # Prepare parameters
        params = params or {}
        params = self.auth.apply_to_params(params)

        logger.debug(
            "HTTP %s %s params=%s",
            method,
            path,
            params,
        )

        try:
            response = await self.client.request(
                method,
                path,
                params=params,
                json=json,
                headers=headers,
            )

            logger.debug(
                "HTTP %s %s -> %d",
                method,
                path,
                response.status_code,
            )

            # Handle errors
            if response.status_code >= 400:
                self._handle_error_response(response)

            # Parse and return JSON
            return response.json()

        except httpx.TimeoutException as e:
            raise FogBugzTransportError(
                f"Request timeout after {self.config.http.timeout}s",
                original_error=e,
            ) from e
        except httpx.NetworkError as e:
            raise FogBugzTransportError(
                f"Network error: {e}",
                original_error=e,
            ) from e
        except httpx.HTTPError as e:
            raise FogBugzTransportError(
                f"HTTP error: {e}",
                original_error=e,
            ) from e

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error HTTP responses.

        Converts HTTP error responses into appropriate exceptions.

        Args:
            response: The error response.

        Raises:
            FogBugzAuthError: For 401/403
            FogBugzNotFoundError: For 404
            FogBugzClientError: For other 4xx
            FogBugzServerError: For 5xx
        """
        status = response.status_code
        url = str(response.request.url)
        body = response.text

        # Try to parse JSON error message
        message = body
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                message = error_data.get("message") or error_data.get("error") or body
        except Exception:
            pass

        error_msg = f"HTTP {status}: {message}"

        # Auth errors
        if status in (401, 403):
            raise FogBugzAuthError(
                error_msg,
                status_code=status,
                url=url,
                response_body=body,
            )

        # Not found
        if status == 404:
            raise FogBugzNotFoundError(
                error_msg,
                status_code=status,
                url=url,
                response_body=body,
            )

        # Other 4xx
        if 400 <= status < 500:
            raise FogBugzClientError(
                error_msg,
                status_code=status,
                url=url,
                response_body=body,
            )

        # 5xx server errors
        if status >= 500:
            raise FogBugzServerError(
                error_msg,
                status_code=status,
                url=url,
                response_body=body,
            )

    async def close(self) -> None:
        """Close the transport and cleanup resources."""
