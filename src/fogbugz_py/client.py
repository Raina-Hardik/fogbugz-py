"""FogBugz API client."""

from __future__ import annotations

import logging

from fogbugz_py.auth.resolver import AuthResolver
from fogbugz_py.config.loader import load_config
from fogbugz_py.config.models import FogBugzConfig, HTTPConfig
from fogbugz_py.http.transport import AsyncTransport
from fogbugz_py.resources.cases import CasesResource
from fogbugz_py.resources.people import PeopleResource
from fogbugz_py.resources.projects import ProjectsResource

logger = logging.getLogger("fogbugz_py.client")


class FogBugzClient:
    """Async client for FogBugz API.

    Orchestrates configuration, authentication, and HTTP transport to provide
    a resource-oriented interface to the FogBugz API.

    Args:
        base_url: Base URL of the FogBugz instance (e.g., "https://example.manuscript.com").
                  If not provided, loads from configuration automatically.
        token: API token for authentication. If not provided, loads from configuration automatically.
        username: Username for authentication (if not using token)
        password: Password for authentication (if not using token)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts (default: 3)
        max_wait_seconds: Maximum wait time between retries (default: 60)

    Example:
        >>> # With explicit credentials
        >>> async with FogBugzClient(base_url="...", token="...") as client:
        ...     cases = await client.cases.search("status:open")
        ...
        >>> # With automatic configuration loading
        >>> async with FogBugzClient() as client:
        ...     cases = await client.cases.search("status:open")
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        max_wait_seconds: int = 60,
    ) -> None:
        """Initialize the FogBugz client.

        If base_url and token are not provided, configuration is loaded automatically
        from config files in the following order:
        1. ./.fogbugz/config.toml
        2. ./config.toml
        3. ~/.fogbugz/config.toml
        4. Environment variables

        Args:
            base_url: Base URL of the FogBugz instance. If None, loads from configuration.
            token: API token for authentication. If None, loads from configuration.
            username: Username for basic auth (requires password)
            password: Password for basic auth (requires username)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            max_wait_seconds: Maximum wait time between retries

        Raises:
            FogBugzConfigError: If configuration is invalid
            FogBugzAuthError: If authentication cannot be resolved
        """
        # If credentials not provided, load from configuration
        if base_url is None or token is None:
            loaded_config = load_config()
            base_url = base_url or loaded_config.base_url
            token = token or loaded_config.token

        # Create HTTP config
        http_config = HTTPConfig(
            timeout=timeout,
            max_retries=max_retries,
            max_wait_seconds=max_wait_seconds,
        )

        # Create FogBugz config
        self._config = FogBugzConfig(
            base_url=base_url,
            token=token,
            username=username,
            password=password,
            http=http_config,
        )

        # Resolve authentication
        self._auth = AuthResolver(self._config)

        # HTTP transport (created in __aenter__)
        self._transport: AsyncTransport | None = None

        # Resource namespaces (created in __aenter__)
        self._cases: CasesResource | None = None
        self._projects: ProjectsResource | None = None
        self._people: PeopleResource | None = None

        logger.debug("Initialized FogBugzClient for %s", base_url)

    @property
    def cases(self) -> CasesResource:
        """Access cases resource.

        Returns:
            CasesResource for searching and retrieving cases

        Raises:
            RuntimeError: If client is not within async context manager
        """
        if self._cases is None:
            raise RuntimeError("Client must be used as async context manager")
        return self._cases

    @property
    def projects(self) -> ProjectsResource:
        """Access projects resource.

        Returns:
            ProjectsResource for listing and retrieving projects

        Raises:
            RuntimeError: If client is not within async context manager
        """
        if self._projects is None:
            raise RuntimeError("Client must be used as async context manager")
        return self._projects

    @property
    def people(self) -> PeopleResource:
        """Access people resource.

        Returns:
            PeopleResource for searching and retrieving people

        Raises:
            RuntimeError: If client is not within async context manager
        """
        if self._people is None:
            raise RuntimeError("Client must be used as async context manager")
        return self._people

    async def __aenter__(self) -> FogBugzClient:
        """Async context manager entry.

        Initializes the HTTP transport and resource namespaces.

        Returns:
            Self for use in async with statement
        """
        # Create and enter transport context
        self._transport = AsyncTransport(self._config, self._auth)
        await self._transport.__aenter__()

        # Create resource namespaces
        self._cases = CasesResource(self)
        self._projects = ProjectsResource(self)
        self._people = PeopleResource(self)

        logger.debug("Entered FogBugzClient context")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        """Async context manager exit.

        Closes the HTTP transport.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        if self._transport is not None:
            await self._transport.__aexit__(exc_type, exc_val, exc_tb)
            self._transport = None

        # Clear resource references
        self._cases = None
        self._projects = None
        self._people = None

        logger.debug("Exited FogBugzClient context")

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> dict:
        """Make an authenticated HTTP request.

        Internal method for resources to use.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/api/v3/cases")
            **kwargs: Additional arguments to pass to transport.request()

        Returns:
            Response data as dictionary

        Raises:
            FogBugzAuthError: If authentication fails
            FogBugzHTTPError: If API request fails
            FogBugzTransportError: If network error occurs
        """
        if self._transport is None:
            raise RuntimeError("Client must be used as async context manager")

        return await self._transport.request(method, endpoint, **kwargs)
