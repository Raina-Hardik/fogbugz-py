"""HTTP-specific errors (deprecated, use exceptions.py)."""

# For backwards compatibility, re-export from exceptions
from fogbugz_py.exceptions import (
    FogBugzAuthError,
    FogBugzClientError,
    FogBugzHTTPError,
    FogBugzNotFoundError,
    FogBugzServerError,
    FogBugzTransportError,
)

__all__ = [
    "FogBugzAuthError",
    "FogBugzClientError",
    "FogBugzHTTPError",
    "FogBugzNotFoundError",
    "FogBugzServerError",
    "FogBugzTransportError",
]
