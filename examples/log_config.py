"""
Logging configuration for FogBugz examples.

- Human-friendly logs in local/dev
- JSON logs in Docker / CI / prod
- structlog-first, stdlib-compatible
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache

import structlog

# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------
ENV = os.getenv("ENV", "local").lower()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_logger() -> structlog.BoundLogger:
    """
    Return a configured structlog logger.

    Configuration is applied once (cached),
    making this safe to import everywhere.
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if ENV in {"local", "dev"}:
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        processors = [
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(LOG_LEVEL)),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()
