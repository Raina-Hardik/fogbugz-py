"""Exception hierarchy for fogbugz-py.

Provides structured error handling for authentication, HTTP, configuration,
and transport-level failures.
"""

from __future__ import annotations


class FogBugzError(Exception):
    """Base exception for all FogBugz client errors.

    Parent class for all fogbugz-py exceptions. Catch this to handle
    any FogBugz-related error.

    Example:
        >>> try:
        ...     case = await client.cases.get(1234)
        ... except FogBugzError as e:
        ...     print(f"FogBugz operation failed: {e}")
    """


class FogBugzConfigError(FogBugzError):
    """Raised when configuration is invalid or incomplete.

    Indicates problems during config file loading, parsing, or validation.
    Examples: missing required fields, invalid TOML syntax, file not found.

    Attributes:
        message: Human-readable error description.
        config_path: Path to the problematic config file (if applicable).
    """

    def __init__(
        self,
        message: str,
        config_path: str | None = None,
    ) -> None:
        """Initialize ConfigError.

        Args:
            message: Description of the configuration error.
            config_path: Path to the config file with the error.
        """
        self.message = message
        self.config_path = config_path
        super().__init__(message)


class FogBugzHTTPError(FogBugzError):
    """Base exception for HTTP-level errors.

    Parent class for all HTTP-related errors. Catch this to handle
    any issues during API communication.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code from the response.
        url: The request URL that failed.
        response_body: The response body (for debugging).
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        url: str | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize HTTPError.

        Args:
            message: Description of the HTTP error.
            status_code: HTTP status code from response.
            url: The request URL.
            response_body: The raw response body.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.url = url
        self.response_body = response_body


class FogBugzClientError(FogBugzHTTPError):
    """Raised for HTTP 4xx client errors.

    Indicates that the request was malformed or invalid. These errors
    are typically not transient and should not be retried.

    Sub-exceptions provide more specific error types.
    """


class FogBugzAuthError(FogBugzClientError):
    """Raised when authentication fails or is missing.

    Indicates that provided credentials are invalid, missing, or expired.
    This includes both API token authentication failures and no auth provided.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code if from HTTP response (e.g., 401, 403).
    """

    def __init__(
        self,
        message: str,
        status_code: int = 401,
        url: str | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize AuthError.

        Args:
            message: Description of the authentication error.
            status_code: HTTP status code (defaults to 401).
            url: The request URL if from HTTP response.
            response_body: The response body if from HTTP response.
        """
        super().__init__(message, status_code, url, response_body)


class FogBugzNotFoundError(FogBugzClientError):
    """Raised when a requested resource is not found (HTTP 404).

    Indicates that the requested case, project, or resource does not exist.

    Example:
        >>> try:
        ...     case = await client.cases.get(99999)
        ... except FogBugzNotFoundError:
        ...     print("Case not found")
    """


class FogBugzServerError(FogBugzHTTPError):
    """Raised for HTTP 5xx server errors.

    Indicates that the FogBugz server encountered an error.
    These errors may be transient and could be retried.

    Example:
        >>> try:
        ...     cases = await client.cases.search("status:open")
        ... except FogBugzServerError as e:
        ...     print(f"Server error {e.status_code}: {e.message}")
    """


class FogBugzTransportError(FogBugzError):
    """Raised for network-level errors.

    Indicates network connectivity issues, timeouts, or other
    transport-layer problems. These are often transient.

    Attributes:
        message: Human-readable error description.
        original_error: The underlying exception (e.g., TimeoutError).
    """

    def __init__(
        self,
        message: str,
        original_error: Exception | None = None,
    ) -> None:
        """Initialize TransportError.

        Args:
            message: Description of the transport error.
            original_error: The underlying exception that caused this.
        """
        self.message = message
        self.original_error = original_error
        super().__init__(message)
