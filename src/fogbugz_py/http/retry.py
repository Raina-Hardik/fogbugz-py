"""Retry logic using Tenacity for transient failures.

Implements exponential backoff retry strategy for handling transient
network and server errors.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from fogbugz_py.exceptions import FogBugzServerError, FogBugzTransportError

logger = logging.getLogger("fogbugz_py.http.retry")


@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_attempts: Maximum number of retry attempts (including initial).
        max_wait_seconds: Maximum wait time between retries in seconds.
        retry_on_timeout: Whether to retry on timeout errors.
    """

    max_attempts: int = 3
    max_wait_seconds: int = 60
    retry_on_timeout: bool = True


class RetryStrategy:
    """Manages retry logic for HTTP requests.

    Uses exponential backoff to gradually increase wait time between retries.
    Retries transient errors (network issues, 5xx server errors, timeouts).

    Attributes:
        config: Retry configuration settings.
    """

    def __init__(self, config: RetryConfig | None = None) -> None:
        """Initialize retry strategy.

        Args:
            config: Retry configuration. Uses defaults if not provided.
        """
        self.config = config or RetryConfig()
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate retry configuration values."""
        if self.config.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.config.max_wait_seconds < 1:
            raise ValueError("max_wait_seconds must be >= 1")

    def should_retry(self, exception: Exception) -> bool:
        """Determine if an exception should trigger a retry.

        Retryable exceptions:
        - FogBugzTransportError: Network/timeout issues
        - FogBugzServerError: 5xx server errors

        Non-retryable:
        - FogBugzHTTPError (4xx): Client errors, auth failures

        Args:
            exception: The exception that occurred.

        Returns:
            True if the exception is retryable, False otherwise.
        """
        # Always retry transport errors (network, timeout)
        if isinstance(exception, FogBugzTransportError):
            # But skip if timeout and timeout retry is disabled
            return not ("timeout" in str(exception).lower() and not self.config.retry_on_timeout)

        # Retry server errors (5xx)
        return bool(isinstance(exception, FogBugzServerError))

    def get_decorator(self) -> Any:
        """Get a Tenacity retry decorator for this strategy.

        Returns:
            Tenacity retry decorator configured with this strategy.
        """
        return retry(
            retry=retry_if_exception_type((FogBugzTransportError, FogBugzServerError)),
            stop=stop_after_attempt(self.config.max_attempts),
            wait=wait_exponential(
                multiplier=1,
                min=1,
                max=self.config.max_wait_seconds,
            ),
            reraise=True,
        )

    def log_retry(
        self,
        attempt_num: int,
        exception: Exception,
        sleep_secs: float,
    ) -> None:
        """Log a retry attempt.

        Args:
            attempt_num: Current attempt number (1-indexed).
            exception: The exception that triggered the retry.
            sleep_secs: Seconds to wait before retrying.
        """
        logger.warning(
            "Retry attempt %d/%d after %s (sleeping %.1fs)",
            attempt_num,
            self.config.max_attempts,
            type(exception).__name__,
            sleep_secs,
        )

    def log_exhausted(self, exception: Exception) -> None:
        """Log when retries are exhausted.

        Args:
            exception: The final exception after all retries failed.
        """
        logger.error(
            "Exhausted all %d retry attempts: %s",
            self.config.max_attempts,
            exception,
        )
