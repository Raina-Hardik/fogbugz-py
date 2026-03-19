# fogbugz-py

> A modern, async-first Python client for FogBugz

[![Python Version](https://img.shields.io/pypi/pyversions/fogbugz-py)](https://pypi.org/project/fogbugz-py/)
[![License](https://img.shields.io/github/license/Raina-Hardik/fogbugz-py)](https://github.com/Raina-Hardik/fogbugz-py/blob/main/LICENSE)

**fogbugz-py** is a Pythonic, async-first client for the FogBugz API. Built on `httpx` with `pydantic` models, automatic retries, and flexible configuration.

---

## Features

✨ **Async-first** - Built on `asyncio` and `httpx` for high-performance concurrent operations  
🎯 **Type-safe** - Full type hints and `pydantic` models for excellent IDE support  
🔄 **Smart retries** - Automatic retry logic with exponential backoff using Tenacity  
⚙️ **Flexible config** - CLI args, config files, or environment variables  
📦 **Multiple variants** - Slim (minimal), full (pydantic), with optional CLI and structured logging  
🔍 **Read-focused** - Search and retrieve cases, projects, and people

---

## Installation

### Default (with pydantic)

```bash
pip install fogbugz-py
```

### Minimal (no pydantic, returns dicts)

```bash
pip install fogbugz-py-slim
```

### With optional features

```bash
# Structured logging with structlog
pip install fogbugz-py[logging]

# CLI with typer
pip install fogbugz-py[typer]

# All features
pip install fogbugz-py[logging,typer]
```

---

## Quick Start

```python
import asyncio
from fogbugz_py import FogBugzClient

async def main():
    async with FogBugzClient(
        base_url="https://example.manuscript.com",
        token="your-api-token"
    ) as client:
        # Search for cases
        cases = await client.cases.search("status:open assignedTo:me")
        for case in cases:
            print(f"#{case.id}: {case.title}")
        
        # Get specific case
        case = await client.cases.get(1234)
        print(f"Status: {case.status}")

asyncio.run(main())
```

---

## Configuration

### Priority Order

Configuration is resolved in this order (highest to lowest):

1. CLI arguments
2. Explicit config file path
3. Project config (`./.fogbugz/config.toml`)
4. User config (`~/.fogbugz/config.toml`)
5. Environment variables

### Config File

Create `~/.fogbugz/config.toml`:

```toml
[fogbugz]
base_url = "https://example.manuscript.com"
token = "your-api-token"

[retry]
max_attempts = 3
max_wait_seconds = 60
```

### Environment Variables

```bash
export FOGBUGZ_BASE_URL="https://example.manuscript.com"
export FOGBUGZ_TOKEN="your-api-token"
```

---

## Usage Examples

### Search Cases

```python
# Simple search
cases = await client.cases.search("status:open")

# Complex query
cases = await client.cases.search(
    "status:active assignedTo:me priority:1,2,3"
)

# Access case properties
for case in cases:
    print(f"{case.id}: {case.title}")
    print(f"  Status: {case.status}")
    print(f"  Assigned to: {case.assigned_to}")
```

### Get Specific Case

```python
case = await client.cases.get(1234)
print(case.model_dump())  # Convert to dict
```

### List Projects

```python
projects = await client.projects.list()
for project in projects:
    print(f"{project.id}: {project.name}")
```

### Error Handling

```python
from fogbugz_py.errors import FogBugzAuthError, FogBugzNotFoundError

try:
    case = await client.cases.get(9999)
except FogBugzNotFoundError:
    print("Case not found")
except FogBugzAuthError:
    print("Authentication failed")
```

### Custom Retry Configuration

```python
from fogbugz_py import FogBugzClient, RetryConfig

client = FogBugzClient(
    base_url="https://example.manuscript.com",
    token="your-token",
    retry_config=RetryConfig(
        max_attempts=5,
        max_wait_seconds=60
    )
)

# Disable retries for specific request
case = await client.cases.get(1234, retry=False)
```

### Parallel Requests

```python
import asyncio

# Fetch multiple cases concurrently
case_ids = [1, 2, 3, 4, 5]
tasks = [client.cases.get(cid) for cid in case_ids]
cases = await asyncio.gather(*tasks)
```

---

## CLI Usage (with typer extra)

```bash
# Search cases
fogbugz search "status:open assignedTo:me"

# Get specific case
fogbugz case get 1234

# Show case events
fogbugz case events 1234 --max 20

# List projects
fogbugz projects list

# Get specific project
fogbugz projects get 2

# Search people
fogbugz people search "Alice"

# Get specific person
fogbugz people get 117

# Show current user
fogbugz whoami

# With explicit config
fogbugz --config /path/to/config.toml search "priority:1"

# With CLI token
fogbugz --token "your-token" search "status:open"
```

---

## API Resources

### Cases

- `client.cases.search(query: str) -> list[Case]`
- `client.cases.get(case_id: int) -> Case`

### Projects

- `client.projects.list() -> list[Project]`
- `client.projects.get(project_id: int) -> Project`

### People

- `client.people.search(name: str) -> list[Person]`
- `client.people.get(person_id: int) -> Person`

---

## Requirements

- Python 3.12 or 3.13
- FogBugz instance with API access

---

## Development

### Setup

```bash
git clone https://github.com/Raina-Hardik/fogbugz-py.git
cd fogbugz-py

# Create environment
hatch env create

# Run tests
hatch run test

# Run linting
hatch run ruff check .

# Format code
hatch run ruff format .
```

### Testing

```bash
# All tests
hatch run pytest

# With coverage
hatch run pytest --cov=fogbugz_py --cov-report=html

# Specific test file
hatch run pytest tests/unit/test_config.py
```

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - Project structure and design
- [API Design](docs/API_DESIGN.md) - Client patterns and error handling
- [Configuration](docs/CONFIGURATION.md) - Config and authentication
- [Packaging](docs/PACKAGING.md) - Package variants and dependencies
- [Development](docs/DEVELOPMENT.md) - Testing and contributing

For FogBugz API reference: [https://api.manuscript.com/](https://api.manuscript.com/)

---

## Roadmap

### v1.0 (Current Focus)

- [x] Core async client
- [x] Config resolution
- [x] Authentication (API token)
- [x] Cases resource (search, find, get, events)
- [x] Projects resource (list, get)
- [x] People resource (search, get)
- [x] CLI (typer extra)
- [x] Documentation

### Post-v1

- [ ] Write operations (create, update)
- [ ] Advanced filters
- [ ] Bulk operations
- [ ] Webhooks
- [ ] Rate limiting

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Author

**Hardik Raina**  
GitHub: [@Raina-Hardik](https://github.com/Raina-Hardik)  
Email: hardikraina079@gmail.com

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run linting and tests
5. Submit a pull request

---

## Acknowledgments

- Built with [httpx](https://www.python-httpx.org/) for async HTTP
- Powered by [pydantic](https://docs.pydantic.dev/) for data validation
- Retry logic via [Tenacity](https://tenacity.readthedocs.io/)
- CLI built with [Typer](https://typer.tiangolo.com/)
