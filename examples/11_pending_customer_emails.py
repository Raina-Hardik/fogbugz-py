"""Example: Find tickets awaiting internal team response to customer emails.

This example identifies tickets where the last event was an email from a customer,
and calculates how long it has been since the internal team responded.

Output is JSON with ticket ID and time since last internal response.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from datetime import UTC, datetime, timedelta
from typing import Any

from log_config import get_logger

from fogbugz_py.client import FogBugzClient

log = get_logger()


def parse_email_from(email_from: str | None) -> dict[str, str | None]:
    """Parse email From field to extract name, email address, and organization.

    Handles formats like:
    - "John Doe <john@example.com>"
    - "john@example.com"
    - "<john@example.com>"
    - "John Doe" (no email)

    Args:
        email_from: Raw From field value

    Returns:
        Dict with name, email, and org (domain-based guess)
    """
    if not email_from:
        return {"name": None, "email": None, "org": None}

    email_from = email_from.strip()

    # Pattern: "Name <email@domain.com>" or just "<email@domain.com>"
    match = re.match(r'^(?:"?([^"<]*)"?\s*)?<([^>]+)>$', email_from)
    if match:
        name = match.group(1).strip() if match.group(1) else None
        email = match.group(2).strip()
    # Check if it's just an email address
    elif "@" in email_from:
        email = email_from
        name = None
    else:
        # Just a name, no email
        name = email_from
        email = None

    # Extract organization from email domain
    org = None
    if email and "@" in email:
        domain = email.split("@")[1]
        # Remove common suffixes and use domain as org hint
        org = domain.split(".")[0].title()

    return {"name": name, "email": email, "org": org}


FOGBUGZ_BASE_URL = os.getenv("FOGBUGZ_BASE_URL")
FOGBUGZ_TOKEN = os.getenv("FOGBUGZ_TOKEN")


async def main() -> None:
    """Find tickets pending response to customer emails and output as JSON."""
    if not FOGBUGZ_BASE_URL or not FOGBUGZ_TOKEN:
        raise RuntimeError(
            "Set FOGBUGZ_BASE_URL and FOGBUGZ_TOKEN environment variables before running this example."
        )

    async with FogBugzClient(base_url=FOGBUGZ_BASE_URL, token=FOGBUGZ_TOKEN) as client:
        log.info("searching_open_cases")

        # Search for open cases - adjust query as needed for your workflow
        cases = await client.cases.search("status:active")

        log.info("cases_found", count=len(cases))

        pending_responses: list[dict[str, Any]] = []
        now = datetime.now(UTC)

        for case in cases:
            try:
                events_list = await client.cases.get_events(case.id)

                if not events_list.events:
                    continue

                # Sort events by timestamp to get the most recent
                sorted_events = sorted(events_list.events, key=lambda e: e.timestamp, reverse=True)
                last_event = sorted_events[0]

                # Check if the last event was an email from external source (customer)
                if not last_event.is_email:
                    continue

                # External emails are from customers
                if not last_event.is_external:
                    continue

                # Find the last internal response
                last_internal_response = None
                for event in sorted_events:
                    # Internal response: email sent by us (not external)
                    if event.is_email and not event.is_external:
                        last_internal_response = event
                        break

                # Calculate time since last internal response
                if last_internal_response:
                    time_since_response = now - last_internal_response.timestamp
                    time_since_response_str = format_timedelta(time_since_response)
                    last_response_timestamp = last_internal_response.timestamp.isoformat()
                else:
                    # No previous internal response
                    time_since_response = now - last_event.timestamp
                    time_since_response_str = (
                        f"{format_timedelta(time_since_response)} (no prior response)"
                    )
                    last_response_timestamp = None

                # Extract customer info from email From field
                customer_info = parse_email_from(last_event.email_from)

                pending_responses.append(
                    {
                        "ticket_id": case.id,
                        "title": case.title,
                        "customer_email_received": last_event.timestamp.isoformat(),
                        "customer_name": customer_info["name"],
                        "customer_email": customer_info["email"],
                        "customer_org": customer_info["org"],
                        "email_from_raw": last_event.email_from,
                        "last_internal_response": last_response_timestamp,
                        "time_since_response": time_since_response_str,
                        "time_since_response_seconds": int(time_since_response.total_seconds()),
                    }
                )

            except ValueError as e:
                log.warning("failed_to_fetch_events", case_id=case.id, error=str(e))
                continue

        # Sort by longest wait time first
        pending_responses.sort(key=lambda x: x["time_since_response_seconds"], reverse=True)

        # Output as JSON
        result: dict[str, Any] = {
            "generated_at": now.isoformat(),
            "total_pending": len(pending_responses),
            "tickets": pending_responses,
        }

        print(json.dumps(result, indent=2))

        log.info("analysis_complete", pending_count=len(pending_responses))


def format_timedelta(td: timedelta) -> str:
    """Format a timedelta into a human-readable string."""
    total_seconds = int(td.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60

    parts: list[str] = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")

    return " ".join(parts) if parts else "< 1m"


if __name__ == "__main__":
    asyncio.run(main())
