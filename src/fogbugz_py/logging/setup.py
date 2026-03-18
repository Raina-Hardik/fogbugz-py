"""Structured logging configuration using structlog.

Only available when fogbugz-py[logging] is installed.
"""

from __future__ import annotations


def setup_logging(*, json_output: bool = False, log_level: str = "INFO") -> None:
    """Configure structured logging with structlog.

    Args:
        json_output: Whether to output logs as JSON
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> from fogbugz_py.logging import setup_logging
        >>> setup_logging(log_level="DEBUG")
    """
    try:
        import structlog  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "structlog is required for structured logging. "
            "Install with: pip install fogbugz-py[logging]"
        ) from e

    # Implementation pending
    raise NotImplementedError("Structured logging setup pending")
