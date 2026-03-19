# Development Guide

## Testing Strategy

### Framework

* **pytest** - Test runner
* **pytest-asyncio** - Async test support
* **respx** - HTTP mocking for httpx

### Why respx?

* Native support for `httpx` (our HTTP client)
* Clear request/response assertions
* Pattern matching for URLs
* Async-aware

### Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── unit/
│   ├── test_config.py          # Config loading
│   ├── test_auth.py            # Auth resolution
│   ├── test_retry.py           # Retry logic
│   └── test_models.py          # Pydantic models
├── integration/
│   ├── test_client.py          # Client lifecycle
│   ├── test_cases.py           # Cases resource
│   └── test_projects.py        # Projects resource
└── e2e/                        # End-to-end (manual)
    └── README.md               # Instructions
```

### Mocking HTTP Responses

```python
import pytest
import respx
from httpx import Response
from fogbugz_py import FogBugzClient

@pytest.mark.asyncio
@respx.mock
async def test_get_case():
    # Mock the FogBugz API response
    respx.get("https://example.manuscript.com/f/api/0/jsonapi").mock(
        return_value=Response(
            200,
            json={
                "data": {
                    "case": {
                        "ixBug": 1234,
                        "sTitle": "Test Case",
                        "sStatus": "Active"
                    }
                }
            }
        )
    )
    
    async with FogBugzClient(
        base_url="https://example.manuscript.com",
        token="test-token"
    ) as client:
        case = await client.cases.get(1234)
        assert case.id == 1234
        assert case.title == "Test Case"
```

### Running Tests

```bash
# All tests
hatch run test

# Specific test file
hatch run pytest tests/unit/test_config.py

# With coverage
hatch run pytest --cov=fogbugz_py --cov-report=html

# Async tests specifically
hatch run pytest -k "async"
```

### Test Scope

* **Unit tests**: Core logic, isolated components
* **Integration tests**: Full client workflows with mocked HTTP
* **E2E tests**: Manual testing against real FogBugz instance (not in CI)

### No Live Integration Tests in CI

Rationale:
* Requires real FogBugz instance
* Credentials management complexity
* Network flakiness
* API rate limits

We rely on comprehensive mocking instead.

---

## Code Quality

### Linting & Formatting: Ruff

Single tool for linting and formatting:

```bash
# Check code
hatch run ruff check .

# Format code
hatch run ruff format .

# Fix auto-fixable issues
hatch run ruff check --fix .
```

### Type Checking: mypy

```bash
# Run type checker
hatch run mypy src/
```

### Configuration

```toml
# pyproject.toml

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "ASYNC", # async checks
]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
```

---

## Logging

### Default: Standard logging

```python
import logging

logger = logging.getLogger("fogbugz_py")
logger.debug("Making request to %s", url)
```

### Optional: structlog

When `fogbugz-py[logging]` is installed:

```python
import structlog

logger = structlog.get_logger()
logger.info("request_started", url=url, method="GET")
```

### Logging Guidelines

* **DEBUG**: HTTP requests, retries
* **INFO**: Client lifecycle, successful operations
* **WARNING**: Deprecated features, username/password auth
* **ERROR**: Failed operations
* **CRITICAL**: Unrecoverable errors

### No Forced Logging Opinion

* Users can ignore logging entirely
* We don't configure handlers (user's responsibility)
* Slim variant users avoid all logging deps

---

## Documentation

### Approach

* **Code-first** - Docstrings are primary documentation
* **Type hints** - Leverage for IDE support
* **Examples** - In docstrings and docs/

### Docstring Style

```python
async def search(
    self,
    query: str,
    *,
    max_results: int | None = None
) -> list[Case]:
    """Search for cases matching a query.
    
    Args:
        query: FogBugz search query string.
            Examples: "status:open", "assignedTo:me"
        max_results: Maximum number of results to return.
            Defaults to FogBugz API default (usually 100).
    
    Returns:
        List of Case objects matching the query.
    
    Raises:
        FogBugzAuthError: If authentication fails.
        FogBugzHTTPError: If API request fails.
    
    Example:
        >>> cases = await client.cases.search("status:open")
        >>> for case in cases:
        ...     print(case.id, case.title)
    
    See Also:
        FogBugz search syntax: https://api.manuscript.com/
    """
```

### External References

Always link to FogBugz API docs:

* Base: [https://api.manuscript.com/](https://api.manuscript.com/)
* Include specific endpoint refs in resource docstrings

---

## CLI Development (Typer Variant)

### MVP Commands

```bash
fogbugz search "<query>"        # Search cases
fogbugz case get <id>           # Get specific case
fogbugz projects list           # List projects
fogbugz whoami                  # Show current user
```

### Output Format

* **Default**: Pretty, human-readable (via `rich`)
* **No pagination** in v1 (dump all results)
* **JSON output**: Explicitly deferred to post-v1

### Example Implementation

```python
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def search(
    query: str,
    token: str = typer.Option(..., envvar="FOGBUGZ_TOKEN"),
    base_url: str = typer.Option(..., envvar="FOGBUGZ_BASE_URL")
):
    """Search for cases."""
    # Implementation
    table = Table(title="Search Results")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Status")
    
    # ... populate table
    
    console.print(table)
```

---

## Current Test Status (Phase 3)

### Test Results: 83 Tests Passing ✅

```
Phase 1 Tests (Config & Auth): 31 passing
  - Config loading: 20 tests
  - Auth resolver: 11 tests

Phase 2 Tests (HTTP & Retry): 29 passing
  - HTTP retry: 14 tests
  - HTTP transport: 15 tests

Phase 3 Tests (Client & Resources): 16 passing
  - Client initialization: 4 tests
  - Context manager lifecycle: 3 tests
  - Cases resource: 3 tests
  - Projects resource: 2 tests
  - People resource: 2 tests
  - Error handling: 2 tests

Smoke Tests: 7 passing
Total: 83 tests with 100% async support
```

### Running Tests

```bash
# All tests with details
hatch run pytest -v

# With coverage report
hatch run pytest --cov=fogbugz_py --cov-report=html

# Specific test file
hatch run pytest tests/test_client.py -v

# Async tests specifically
hatch run pytest -k "asyncio"
```

---

## Next Steps (Phase 4+)

### Phase 4: Resource Enhancements & Polish

1. **Additional field support**
   - Add more case fields
   - Add more project fields
   - Add more person fields

2. **Query filtering**
   - Advanced search parameters
   - Pagination support

3. **Documentation improvements**
   - API reference documentation
   - Usage examples for each resource
   - Advanced configuration guide

4. **Type checking & linting**
   - Run mypy validation
   - Run ruff linting
   - Fix any issues found

### Phase 5: CLI Implementation (Completed)

5. **CLI commands (typer extra)**
   - `fogbugz search "<query>"` - Search cases
   - `fogbugz case get <id>` - Get specific case
    - `fogbugz case events <id> --max <n>` - Get case events
   - `fogbugz projects list` - List projects
    - `fogbugz projects get <id>` - Get specific project
   - `fogbugz people search <name>` - Search people
    - `fogbugz people get <id>` - Get specific person
   - `fogbugz whoami` - Show current user

6. **CLI output formatting**
   - Rich table output for lists
   - Formatted case details
   - Error message improvements

7. **Structured logging (logging extra)**
   - structlog configuration
   - Request/response logging
   - Retry attempt logging

---

## Development Environment Setup

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourorg/fogbugz-py.git
cd fogbugz-py

# Create Hatch environment
hatch env create

# Run tests
hatch run test

# Run linting
hatch run ruff check .

# Format code
hatch run ruff format .
```

### IDE Setup

#### VS Code

Install extensions:
* Python
* Pylance
* Ruff

Settings:
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.testing.pytestEnabled": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

#### PyCharm

* Mark `src/` as sources root
* Enable pytest as test runner
* Configure Ruff as external tool

---

## Contributing Guidelines (Future)

For future contributors:

* Write tests for new features
* Update documentation
* Follow existing code style
* Run linter before committing
* Use conventional commits
* Update CHANGELOG.md

---

## Performance Considerations

### Async Best Practices

* Use `asyncio.gather()` for parallel requests
* Don't create too many concurrent connections
* Respect FogBugz rate limits (implement if needed)

### Example: Parallel Case Fetching

```python
async def get_cases(client, case_ids):
    tasks = [client.cases.get(cid) for cid in case_ids]
    return await asyncio.gather(*tasks)
```

### Connection Pooling

`httpx.AsyncClient` handles this automatically:

```python
# Single client instance for entire session
async with FogBugzClient(...) as client:
    # Reuses connections
    case1 = await client.cases.get(1)
    case2 = await client.cases.get(2)
```
