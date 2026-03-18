# fogbugz-py Architecture Overview

## TL;DR

**fogbugz-py** is an **async-first, OOP, resource-oriented client** built on `httpx`, with **Tenacity-based retries**, **TOML config resolution**, and **read-only FogBugz APIs**.

We ship a **pydantic-powered core** (`fogbugz-py`) and a **minimal, pydantic-free slim variant** (`fogbugz-py-slim`), with **logging** and **CLI (typer)** as composable extras.

The public API is **resource-based** (`client.cases.search()`), responses are **typed pydantic models**, and configuration precedence is **CLI > explicit config > project config > user config > env**.

---

## Project Goals & Non-Goals

### Goals

* Pythonic, async-first FogBugz client
* Read/search-focused API surface
* Strong typing and DX via pydantic
* Clean separation of transport, auth, config, and resources
* Optional CLI and structured logging
* Explicit, predictable behavior

### Non-Goals (for v1)

* Write/mutate APIs
* Advanced FogBugz features
* Full API surface coverage
* Sync-first API

---

## Supported Python & Tooling

* **Python**: 3.12–3.13
* **Build system**: Hatch
* **Async runtime**: `asyncio`
* **HTTP client**: `httpx.AsyncClient`
* **Retries**: Tenacity
* **Testing**: pytest + pytest-asyncio
* **Response format**: JSON (not XML)

---

## Project Structure

```text
fogbugz-py/
├── pyproject.toml
├── README.md
├── main.py
├── docs/
│   ├── ARCHITECTURE.md       # This file
│   ├── API_DESIGN.md         # Client & resource patterns
│   ├── CONFIGURATION.md      # Config & auth resolution
│   ├── PACKAGING.md          # Package variants & extras
│   └── DEVELOPMENT.md        # Testing & next steps
├── src/
│   └── fogbugz_py/
│       ├── __init__.py
│       ├── client.py
│       ├── http/
│       │   ├── transport.py
│       │   ├── retry.py
│       │   └── errors.py
│       ├── auth/
│       │   └── resolver.py
│       ├── config/
│       │   └── loader.py
│       ├── resources/
│       │   ├── cases.py
│       │   ├── projects.py
│       │   └── people.py
│       ├── models/          # pydantic-only
│       │   └── case.py
│       ├── cli/             # typer-only
│       └── logging/         # structlog-only
└── tests/
    └── ...
```

---

## Async & HTTP Architecture

### HTTP Stack

* `httpx.AsyncClient` for all HTTP operations
* Shared client per `FogBugzClient` instance
* Connection pooling enabled
* Configurable timeouts

### Public API

* **Async-only** - no sync wrappers in v1
* All network operations return coroutines

```python
async with FogBugzClient(...) as client:
    cases = await client.cases.search("status:open")
```

---

## Documentation References

* FogBugz API documentation: [https://api.manuscript.com/](https://api.manuscript.com/)
* All endpoints use JSON format (not XML)
