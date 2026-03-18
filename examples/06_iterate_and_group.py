"""Iterate and group cases by status.

Demonstrates Pythonic iteration patterns and data analysis
using list comprehensions and dictionaries.
"""

import asyncio

from log_config import get_logger

from fogbugz_py import FogBugzClient

log = get_logger()


async def main():
    """Group cases by status and filter by priority."""
    async with FogBugzClient() as client:
        log.info("fetching_cases", query="status:active or status:build*")
        all_cases = await client.cases.search("status:active or status:build*")

        log.info("total_cases_fetched", count=len(all_cases))

        # Filter cases by priority using Pythonic approach
        critical_cases = [c for c in all_cases if c.priority and c.priority <= 2]
        log.info("critical_cases_found", count=len(critical_cases))

        for case in critical_cases[:3]:
            log.info(
                "case_summary",
                case_id=case.id,
                title=case.title[:50],
                priority=case.priority,
            )

        # Group cases by status
        status_groups = {}
        for case in all_cases[:20]:
            status = case.status or "Unknown"
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(case.id)

        log.info("status_distribution", sample_size=20)
        for status, case_ids in sorted(status_groups.items()):
            log.info(
                "status_group",
                status=status,
                count=len(case_ids),
                case_ids=case_ids[:5],
            )


if __name__ == "__main__":
    asyncio.run(main())
