"""Timeout configuration and management."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TimeoutConfig:
    """HTTP timeout configuration.

    Args:
        connect: Timeout for establishing connection
        read: Timeout for reading response
        write: Timeout for writing request
        pool: Timeout for acquiring connection from pool
    """

    connect: float = 10.0
    read: float = 30.0
    write: float = 30.0
    pool: float = 10.0

    @property
    def total(self) -> float:
        """Total timeout (max of all timeouts)."""
        return max(self.connect, self.read, self.write, self.pool)
