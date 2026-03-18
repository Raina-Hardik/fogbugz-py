"""Find cases with date range filtering.

Demonstrates client-side date filtering combined with base filters
to find cases updated within a specific time period.
"""

import asyncio
from datetime import UTC, datetime, timedelta

from log_config import get_logger

from fogbugz_py import FogBugzClient

log = get_logger()


async def main():
    """Find cases updated in the past week."""
    week_ago = datetime.now(UTC) - timedelta(days=7)

    log.info(
        "finding_cases_with_date_filter",
        status="open",
        updated_after=week_ago.isoformat(),
    )

    async with FogBugzClient() as client:
        recent_updates = await client.cases.find(
            status="open", updated_after=week_ago, max_results=10
        )

        log.info("cases_found", total=len(recent_updates))

        for case in recent_updates[:3]:
            log.info(
                "case_summary",
                case_id=case.id,
                title=case.title[:50],
                status=case.status,
                last_updated=(case.last_updated.isoformat() if case.last_updated else None),
            )


if __name__ == "__main__":
    asyncio.run(main())
