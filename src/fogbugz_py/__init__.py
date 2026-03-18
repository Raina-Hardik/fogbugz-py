"""fogbugz-py: A modern, async-first Python client for FogBugz."""

__version__ = "0.1.0"
__author__ = "Hardik Raina"
__email__ = "hardikraina079@gmail.com"

from fogbugz_py.client import FogBugzClient
from fogbugz_py.exceptions import (
    FogBugzAuthError,
    FogBugzClientError,
    FogBugzError,
    FogBugzHTTPError,
    FogBugzNotFoundError,
    FogBugzServerError,
    FogBugzTransportError,
)

__all__ = [
    "FogBugzAuthError",
    "FogBugzClient",
    "FogBugzClientError",
    "FogBugzError",
    "FogBugzHTTPError",
    "FogBugzNotFoundError",
    "FogBugzServerError",
    "FogBugzTransportError",
]
