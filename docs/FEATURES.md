# FogBugz Python Client - Features

This document tracks the features and capabilities of the `fogbugz-py` client library. It will be updated as new features are added.

## Current Phase: Core Client Complete (Phases 1, 2 & 3)

### Phase 1: Configuration & Authentication ✅

#### Configuration Loading
- **Multi-source configuration resolution** with priority order:
  1. Explicit arguments (highest priority)
  2. Explicit config file path
  3. Project-local config (`./.fogbugz/config.toml` or `./config.toml`)
  4. User config (`~/.fogbugz/config.toml`)
  5. Environment variables (lowest priority)
- **TOML file parsing** with environment variable expansion (`~` and `$VAR` syntax)
- **Environment variable support** with `FOGBUGZ_*` prefix (e.g., `FOGBUGZ_BASE_URL`, `FOGBUGZ_TOKEN`)
- **Nested HTTP configuration** via environment (e.g., `FOGBUGZ_HTTP_TIMEOUT`, `FOGBUGZ_HTTP_MAX_RETRIES`)
- **Configuration validation** with clear error messages for missing required fields

#### Configuration Models
- **FogBugzConfig**: Main configuration model
  - Required: `base_url`, and either `token` OR both `username` and `password`
  - Optional: custom HTTP settings
- **HTTPConfig**: HTTP client configuration
  - `timeout`: Request timeout in seconds (default: 30)
  - `max_retries`: Maximum retry attempts (default: 3)
  - `max_wait_seconds`: Maximum wait time between retries (default: 60)
  - `verify_ssl`: SSL certificate verification (default: True)

#### Authentication Resolution
- **Token-based authentication**: Bearer token in Authorization header
- **Basic authentication**: Username and password with proper encoding
- **Authentication priority**: Token takes precedence over username/password
- **Deprecation warning**: Username/password authentication emits deprecation warning (safer method recommended)
- **Authentication validation**: Ensures one valid auth method is configured

#### Error Handling
- **FogBugzConfigError**: Configuration loading and validation errors with file path tracking
- **FogBugzAuthError**: Authentication failures (defaults to 401 status)
- **Comprehensive exception hierarchy**: Organized error types for proper exception handling

### Phase 2: HTTP Transport & Retry Logic ✅

#### Async HTTP Transport
- **Async-first implementation** using `httpx.AsyncClient`
- **Context manager support** for proper client lifecycle management (`async with AsyncTransport() as transport:`)
- **Request method**: Async HTTP requests with automatic auth header injection
- **Request/response handling**: Automatic JSON parsing and error conversion
- **Custom user agent**: Identifies requests with `fogbugz-py/{version}`

#### Automatic Error Conversion
- **HTTP status code → domain exception mapping**:
  - 401/403: `FogBugzAuthError` (authentication/authorization failed)
  - 404: `FogBugzNotFoundError` (resource not found)
  - 400-499: `FogBugzClientError` (client request error)
  - 500+: `FogBugzServerError` (server error, retryable)
  - Network errors: `FogBugzTransportError` (timeout, connection, retryable)
- **Response body tracking**: Error objects include raw response body for debugging
- **URL and headers in errors**: Full request context available in exceptions

#### Retry Strategy
- **Exponential backoff** with jitter for failed requests
- **Automatic retry configuration**:
  - `max_attempts`: Maximum number of retry attempts (default: 3)
  - `max_wait_seconds`: Maximum wait time between retries (default: 60)
  - `retry_on_timeout`: Whether to retry on timeout errors (default: True)
- **Smart retry logic**: Only retries on:
  - Network errors (timeouts, connection failures)
  - Server errors (5xx HTTP status codes)
  - Does NOT retry on client errors (4xx) or auth failures (401/403)
- **Retry decorators**: Tenacity-based decorator for easy integration
- **Structured logging**: Detailed logging of retry attempts and exhausted retries

#### Configuration Management
- **Dependency injection pattern**: No hard dependencies on Pydantic in core
- **Slim variant compatibility**: Designed to work with or without full Pydantic installation
- **Type hints throughout**: Full Python 3.12+ type annotations
- **Validation at instantiation**: Config errors caught early with clear messages

### Phase 3: Core FogBugzClient Class ✅

#### Main Client Implementation
- **FogBugzClient**: Orchestrating async client class with full context manager support
  - Integrates configuration, authentication, and HTTP transport layers
  - Single entry point for all FogBugz API interactions
  - Async-only interface using `async with` statement
- **Resource-oriented architecture**: Access via properties (`client.cases`, `client.projects`, `client.people`)
- **Lazy initialization**: Resources created in `__aenter__`, properly cleaned up in `__aexit__`
- **Context manager enforcement**: Clear errors when resources accessed outside `async with` block
- **Internal request routing**: `_request()` method for resources to make authenticated HTTP calls

#### Cases Resource
- **search(query, max_results)**: Search for cases with optional result limit
  - Examples: `"status:open"`, `"assignedTo:me"`, `"status:open assignedTo:me"`
  - Returns typed `Case` objects with full field aliasing
- **get(case_id)**: Retrieve specific case by ID
  - Returns single `Case` object with all available fields
- **Case model**: Pydantic model with FogBugz field aliasing
  - `id` (ixBug), `title` (sTitle), `status` (sStatus)
  - `assigned_to` (sPersonAssignedTo), `priority` (ixPriority)
  - `project` (sProject), `area` (sArea), `category` (sCategory)

#### Projects Resource
- **list()**: List all available projects
  - Returns list of typed `Project` objects
- **get(project_id)**: Retrieve specific project by ID
  - Returns single `Project` object with full metadata
- **Project model**: Pydantic model with field aliasing
  - `id` (ixProject), `name` (sProjectName)
  - `description` (sDesc), `status` (sStatus)

#### People Resource
- **search(name)**: Search for people by name
  - Returns list of `Person` objects matching search criteria
- **get(person_id)**: Retrieve specific person by ID
  - Returns single `Person` object with contact information
- **Person model**: Pydantic model with field aliasing
  - `id` (ixPerson), `name` (sFullName)
  - `email` (sEmail), `phone` (sPhone)

#### Model Support
- **Pydantic-based models** with automatic field aliasing for FogBugz API field names
- **populate_by_name**: Supports both Pythonic names and original API field names
- **Type-safe responses**: All fields properly typed with optional defaults
- **Extensible design**: Easy to add new fields and models

## Test Coverage

- **Phase 1**: 31 passing tests
  - Config loading: 20 tests
  - Auth resolver: 11 tests
- **Phase 2**: 29 passing tests
  - HTTP retry: 14 tests
  - HTTP transport: 15 tests
- **Phase 3**: 16 passing tests
  - Client initialization: 4 tests
  - Context manager lifecycle: 3 tests
  - Cases resource: 3 tests
  - Projects resource: 2 tests
  - People resource: 2 tests
  - Error handling: 2 tests
- **Smoke tests**: 7 integration tests
- **Total**: 83 passing tests with 100% async support

## Architecture Patterns

- **Async context managers**: Proper resource lifecycle with `async with`
- **Dependency injection**: Config and auth resolver passed to transport
- **Exception-driven flow**: Clear exception hierarchy for control flow
- **Multi-source configuration**: Cascading resolution with clear priority
- **Type-safe**: Full type hints with mypy compatibility

## Upcoming Features (Planned)

### Phase 4: Resource Enhancements & Polish
- Additional fields and filters for cases, projects, and people
- Pagination support for search results
- Better error messages and validation
- Documentation improvements and examples
- Type checking (mypy) validation
- Linting (ruff) passing

### Phase 5: CLI Tooling
- Command-line interface using Typer framework
- Rich output formatting for terminal display
- Subcommands for case search, project listing, etc.
- Config file auto-discovery and environment variable support

## Usage Example (Current Phase)

```python
import asyncio
from fogbugz_py import FogBugzClient

async def main():
    # Initialize client with config
    async with FogBugzClient(
        base_url="https://example.manuscript.com",
        token="your-api-token"
    ) as client:
        # Search for cases
        cases = await client.cases.search("status:open assignedTo:me")
        for case in cases:
            print(f"#{case.id}: {case.title} ({case.status})")
        
        # Get specific case
        case = await client.cases.get(1234)
        print(f"Case {case.id}: {case.title}")
        
        # List all projects
        projects = await client.projects.list()
        for project in projects:
            print(f"Project: {project.name}")
        
        # Search for people
        people = await client.people.search("John")
        for person in people:
            print(f"User: {person.name} ({person.email})")

asyncio.run(main())
```

## Development Status

- ✅ Core foundation complete (config, auth, HTTP transport)
- ✅ Comprehensive test suite passing (83 tests)
- ✅ Error handling with domain-specific exceptions
- ✅ Retry logic with exponential backoff
- ✅ Client core class (Phase 3)
- ✅ Resource implementations (Phase 3)
- ⏳ Resource enhancements & polish (Phase 4)
- ⏳ CLI interface (Phase 5)

## Documentation Files

- [ARCHITECTURE.md](ARCHITECTURE.md) - Overall system design
- [API_DESIGN.md](API_DESIGN.md) - API and resource specifications
- [CONFIGURATION.md](CONFIGURATION.md) - Detailed configuration guide
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development workflow and testing
