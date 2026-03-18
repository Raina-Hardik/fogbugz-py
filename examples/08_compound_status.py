"""Find cases with compound status values.

Demonstrates handling FogBugz compound status values like
"Closed (Responded)" and proper error handling for status lookups.
"""

import asyncio

from log_config import get_logger

from fogbugz_py import FogBugzClient
from fogbugz_py.exceptions import FogBugzClientError

log = get_logger()


async def main():
    """Find cases with a specific compound status."""
    async with FogBugzClient() as client:
        status_to_find = "Closed (Responded)"

        log.info("finding_cases_with_status", status=status_to_find)

        try:
            closed_cases = await client.cases.find(status=status_to_find, max_results=5)

            log.info("cases_found", total=len(closed_cases))

            for case in closed_cases[:3]:
                log.info(
                    "case_summary",
                    case_id=case.id,
                    title=case.title[:50],
                    status=case.status,
                    closed=case.closed.isoformat() if case.closed else None,
                )

        except FogBugzClientError as e:
            log.warning(
                "status_lookup_failed",
                requested_status=status_to_find,
                error=str(e)[:100],
                note="FogBugz uses exact compound status names. Try: Active, Build Sent, Waiting for Customer, etc.",
            )


if __name__ == "__main__":
    asyncio.run(main())
