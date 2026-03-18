# API Design

## Client & Resource Pattern

### Resource-Based Design

The public API uses a **resource-based** pattern where resources are accessed as attributes on the client:

```python
client.cases.search(query="assignedTo:me")
client.cases.get(case_id=1234)
client.projects.list()
client.people.search(name="John")
```

### Ownership Model

* `FogBugzClient` owns:
  * Authentication state
  * HTTP transport layer
  * Retry configuration
  * Base URL and settings

* Resources are **thin namespaces**:
  * Not stateful entities
  * Just organize API methods
  * Share parent client's transport

### Example Usage

```python
from fogbugz_py import FogBugzClient

async with FogBugzClient(
    base_url="https://example.manuscript.com",
    token="your-api-token"
) as client:
    # Search for cases
    cases = await client.cases.search("status:open assignedTo:me")
    
    # Get specific case
    case = await client.cases.get(1234)
    
    # List projects
    projects = await client.projects.list()
```

---

## Response Modeling

### Pydantic Models (Default)

The **core package** (`fogbugz-py`) uses **pydantic** for response modeling:

#### Benefits

* Excellent developer experience
* Runtime validation
* IDE autocomplete and type checking
* Field aliasing (`ixBug` → `id`)
* Easy serialization via `.model_dump()`

#### Example Model

```python
from pydantic import BaseModel, Field, ConfigDict

class Case(BaseModel):
    id: int = Field(alias="ixBug")
    title: str = Field(alias="sTitle")
    status: str = Field(alias="sStatus")
    assigned_to: str | None = Field(alias="sPersonAssignedTo", default=None)
    
    model_config = ConfigDict(populate_by_name=True)
```

#### Usage

```python
case = await client.cases.get(1234)
print(case.id)          # Typed attribute access
print(case.title)       # IDE autocomplete works
data = case.model_dump()  # Convert to dict
```

### Plain Dictionaries (Slim Variant)

The **slim package** (`fogbugz-py-slim`) returns plain dictionaries:

```python
case = await client.cases.get(1234)
print(case["ixBug"])    # Raw API field names
print(case["sTitle"])
```

This is for users who:
* Don't want pydantic dependency
* Need maximum performance
* Prefer raw API responses

---

## Error Handling

### Exception Hierarchy

```python
FogBugzError                    # Base exception
├── FogBugzHTTPError            # HTTP-level errors
│   ├── FogBugzClientError      # 4xx errors
│   │   ├── FogBugzAuthError    # 401/403
│   │   └── FogBugzNotFoundError # 404
│   └── FogBugzServerError      # 5xx errors
└── FogBugzTransportError       # Network/timeout errors
```

### Error Information

All exceptions include:
* Original HTTP response (when available)
* Status code
* Request URL
* Response body (for debugging)

### Example Error Handling

```python
from fogbugz_py.errors import FogBugzAuthError, FogBugzNotFoundError

try:
    case = await client.cases.get(1234)
except FogBugzAuthError:
    print("Invalid credentials")
except FogBugzNotFoundError:
    print("Case not found")
```

---

## Retry & Resilience

### Library: Tenacity

All HTTP requests use **Tenacity** for retry logic.

### Default Configuration

* **Max retries**: 3
* **Strategy**: Exponential backoff with full jitter
* **Retry on**:
  * Network timeouts
  * Connection errors
  * HTTP 5xx errors
* **No retries on**: 4xx errors (client errors are not transient)

### Configuration

#### Global (Client-Level)

```python
from fogbugz_py import FogBugzClient, RetryConfig

client = FogBugzClient(
    token="...",
    retry_config=RetryConfig(
        max_attempts=5,
        max_wait_seconds=60
    )
)
```

#### Per-Request Override

```python
# Disable retries for a specific request
case = await client.cases.get(1234, retry=False)

# Custom retry for specific request
case = await client.cases.get(1234, max_attempts=1)
```

### Retry Behavior Example

```
Attempt 1: Immediate
Attempt 2: Wait 1-2s (exponential + jitter)
Attempt 3: Wait 2-4s
Attempt 4: Wait 4-8s (up to max_wait_seconds)
```

---

## Read-Only Operations (v1 Scope)

### Supported Resources

| Resource   | Operations                |
| ---------- | ------------------------- |
| `cases`    | `search()`, `get()`       |
| `projects` | `list()`, `get()`         |
| `people`   | `search()`, `get()`       |

### Future (Not v1)

* Write operations (create, update, delete)
* Advanced filters
* Bulk operations
* Webhooks
* Custom fields manipulation
