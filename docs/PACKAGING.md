# Packaging & Distribution

## Package Variants

We provide **one package** with **optional extras**, not separate distributions.

### Core Packages

| Package Name          | Description                                    | Key Dependencies       |
| --------------------- | ---------------------------------------------- | ---------------------- |
| `fogbugz-py-slim`     | Minimal async client, no pydantic              | `httpx`, `tenacity`    |
| `fogbugz-py`          | Full client with pydantic models (default)     | + `pydantic`           |
| `fogbugz-py[logging]` | Adds structured logging support                | + `structlog`          |
| `fogbugz-py[typer]`   | Adds Typer-based CLI                           | + `typer`, `rich`      |

### Installation Examples

```bash
# Minimal installation (dict responses)
pip install fogbugz-py-slim

# Default installation (pydantic models)
pip install fogbugz-py

# With structured logging
pip install fogbugz-py[logging]

# With CLI
pip install fogbugz-py[typer]

# Full installation (all extras)
pip install fogbugz-py[logging,typer]
```

---

## Dependency Tree

### Core Dependencies (All Variants)

```
httpx >= 0.27.0        # Async HTTP client
tenacity >= 9.0.0      # Retry logic
tomli >= 2.0.0         # TOML parsing (Python 3.12)
```

### Default Variant (`fogbugz-py`)

```
+ pydantic >= 2.0.0    # Response models & validation
```

### Optional Extras

#### `[logging]`
```
+ structlog >= 24.0.0  # Structured logging
```

#### `[typer]`
```
+ typer >= 0.12.0      # CLI framework
+ rich >= 13.0.0       # Pretty terminal output
```

---

## pyproject.toml Structure

```toml
[project]
name = "fogbugz-py"
version = "0.1.0"
description = "Async Python client for FogBugz"
requires-python = ">=3.12,<3.14"
dependencies = [
    "httpx>=0.27.0",
    "tenacity>=9.0.0",
    "tomli>=2.0.0; python_version < '3.13'",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
logging = ["structlog>=24.0.0"]
typer = ["typer>=0.12.0", "rich>=13.0.0"]

# Slim variant (separate distribution)
# Handled via separate pyproject.toml or build backend magic

[project.scripts]
fogbugz = "fogbugz_py.cli:main"  # Only when [typer] installed
```

---

## Slim Variant Implementation

### Option 1: Conditional Imports (Recommended)

Single codebase with conditional pydantic usage:

```python
# src/fogbugz_py/responses.py
try:
    from pydantic import BaseModel
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

if PYDANTIC_AVAILABLE:
    # Return pydantic models
    def parse_case(data):
        return Case.model_validate(data)
else:
    # Return plain dicts
    def parse_case(data):
        return data
```

### Option 2: Separate Distributions

Maintain two `pyproject.toml` files:

```
fogbugz-py/           # Full version
├── pyproject.toml
└── src/

fogbugz-py-slim/      # Slim version
├── pyproject.toml
└── src/              # Symlink or shared code
```

**Decision**: We'll use **Option 1** for simplicity in v1.

---

## Build System: Hatch

### Why Hatch?

* Modern Python build backend
* Built-in environment management
* Easy extras handling
* Version management
* Clean build/publish workflow

### Key Hatch Features Used

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.envs.default]
dependencies = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "respx>=0.21.0",
]

[tool.hatch.envs.dev]
dependencies = [
    "ruff>=0.4.0",
    "mypy>=1.10.0",
]
```

### Common Hatch Commands

```bash
# Create dev environment
hatch env create

# Run tests
hatch run test

# Run linting
hatch run lint

# Build distribution
hatch build

# Publish to PyPI
hatch publish
```

---

## Version Management

### Versioning Scheme

We follow **semantic versioning**: `MAJOR.MINOR.PATCH`

* **MAJOR**: Breaking API changes
* **MINOR**: New features, backwards compatible
* **PATCH**: Bug fixes

### Version Source

Single source of truth in `pyproject.toml`:

```toml
[project]
version = "0.1.0"
```

Access at runtime:

```python
from fogbugz_py import __version__
print(__version__)  # "0.1.0"
```

---

## Python Version Support

### Supported Versions

* **Python 3.12** (minimum)
* **Python 3.13** (actively tested)

### Python 3.11 and Earlier

**Not supported**. Rationale:
* Python 3.12 has better async performance
* Modern type hints (PEP 695 generics)
* Cleaner standard library

Users on older Python versions should use older FogBugz clients or upgrade Python.

---

## Distribution Checklist

Before publishing:

- [ ] All tests pass (Python 3.12 & 3.13)
- [ ] Documentation is up to date
- [ ] `CHANGELOG.md` is updated
- [ ] Version bumped in `pyproject.toml`
- [ ] Git tag created (`git tag v0.1.0`)
- [ ] Built distributions tested (`hatch build`)
- [ ] Published to Test PyPI first
- [ ] Published to PyPI (`hatch publish`)
- [ ] GitHub release created

---

## Import Paths

### Default Package

```python
# Main client
from fogbugz_py import FogBugzClient

# Models (pydantic variant only)
from fogbugz_py.models import Case, Project

# Errors
from fogbugz_py.errors import FogBugzError, FogBugzAuthError

# Config
from fogbugz_py.config import load_config
```

### Slim Package

Same import paths, different behavior:

```python
# Returns dicts instead of pydantic models
from fogbugz_py import FogBugzClient

client = FogBugzClient(...)
case = await client.cases.get(1234)
print(type(case))  # <class 'dict'> in slim variant
```
