# Configuration & Authentication

## Configuration System

### Resolution Order (Highest → Lowest Priority)

1. **CLI arguments** - Explicitly passed flags
2. **Explicit config path** - `--config path/to/config.toml`
3. **Project-local config** - `./config.toml` or `./.fogbugz/config.toml`
4. **User config** - `~/.fogbugz/config.toml`
5. **Environment variables** - `FOGBUGZ_*` prefixed

### Config Format: TOML Only

```toml
# ~/.fogbugz/config.toml

[fogbugz]
base_url = "https://example.manuscript.com"
token = "your-api-token-here"

[retry]
max_attempts = 3
max_wait_seconds = 60

[http]
timeout = 30
```

### Config File Locations

| Location                      | Purpose                         |
| ----------------------------- | ------------------------------- |
| `~/.fogbugz/config.toml`      | User-level defaults             |
| `./config.toml`               | Project-specific overrides      |
| `./.fogbugz/config.toml`      | Project-specific (alternative)  |
| Custom path via `--config`    | Explicit override               |

### Disabling Config Auto-Discovery

```bash
# Ignore all config files, only use CLI args and env vars
fogbugz --no-config search "status:open"
```

---

## Authentication

### Supported Methods

#### 1. API Token (Preferred)

```python
from fogbugz_py import FogBugzClient

client = FogBugzClient(
    base_url="https://example.manuscript.com",
    token="your-api-token"
)
```

Via config:
```toml
[fogbugz]
base_url = "https://example.manuscript.com"
token = "your-api-token"
```

Via environment:
```bash
export FOGBUGZ_TOKEN="your-api-token"
export FOGBUGZ_BASE_URL="https://example.manuscript.com"
```

Via CLI:
```bash
fogbugz --token "your-api-token" search "status:open"
```

#### 2. Username/Password (Supported, Warns)

```python
client = FogBugzClient(
    base_url="https://example.manuscript.com",
    username="user@example.com",
    password="your-password"
)
```

**Note**: Using username/password will emit a warning recommending API tokens for better security. This warning is suppressible.

### Authentication Resolution

Same priority order as configuration:

1. Explicit arguments to `FogBugzClient()`
2. Config file (project → user)
3. Environment variables

### Environment Variables

| Variable               | Purpose                  |
| ---------------------- | ------------------------ |
| `FOGBUGZ_BASE_URL`     | FogBugz instance URL     |
| `FOGBUGZ_TOKEN`        | API token                |
| `FOGBUGZ_USERNAME`     | Username (if not token)  |
| `FOGBUGZ_PASSWORD`     | Password (if not token)  |

### Authentication Behavior

* Authentication resolved **once** at client creation
* Token passed via FogBugz-native mechanism (query param or header)
* No automatic re-authentication on 401 (fail fast)
* Clear error messages on auth failures

---

## Configuration Profiles (Future)

**Not in v1**, but the design allows for:

```toml
[profiles.production]
base_url = "https://prod.manuscript.com"
token = "prod-token"

[profiles.staging]
base_url = "https://staging.manuscript.com"
token = "staging-token"
```

```bash
fogbugz --profile production search "status:open"
```

---

## Config Validation

* Invalid config files fail fast with clear errors
* Missing required fields (e.g., `base_url`) raise `ConfigError`
* Unknown fields emit warnings (forward compatibility)

### Example Error Messages

```
ConfigError: Missing required field 'base_url' in config file: ~/.fogbugz/config.toml

AuthError: No authentication method provided. Use --token, config file, or FOGBUGZ_TOKEN env var.
```

---

## Security Best Practices

### Recommended

* Use **API tokens** instead of passwords
* Store tokens in user config (`~/.fogbugz/config.toml`) with proper permissions
* Use environment variables in CI/CD environments
* Never commit tokens to version control

### Token Storage Permissions

```bash
# Linux/macOS
chmod 600 ~/.fogbugz/config.toml

# Windows (via PowerShell)
icacls "$env:USERPROFILE\.fogbugz\config.toml" /inheritance:r /grant:r "$env:USERNAME:R"
```

### .gitignore Recommendations

```gitignore
# FogBugz config files
config.toml
.fogbugz/
```

---

## Programmatic Configuration

### Direct Instantiation

```python
from fogbugz_py import FogBugzClient

# Minimal
client = FogBugzClient(
    base_url="https://example.manuscript.com",
    token="your-token"
)

# With custom settings
client = FogBugzClient(
    base_url="https://example.manuscript.com",
    token="your-token",
    timeout=60,
    max_retries=5
)
```

### Load from Config File

```python
from fogbugz_py.config import load_config

config = load_config("path/to/config.toml")
client = FogBugzClient.from_config(config)
```

### Mixed Sources

```python
# Load from default locations, override specific values
client = FogBugzClient(
    token="override-token",  # Override config file
    # base_url loaded from config/env
)
```
