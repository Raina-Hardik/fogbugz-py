"""Search for cases assigned to a specific person.

Demonstrates raw search query usage with string patterns.
"""

import asyncio

from log_config import get_logger

from fogbugz_py import FogBugzClient

log = get_logger()


async def main():
    """Search for cases assigned to a person."""
    async with FogBugzClient() as client:
        log.info("searching_assigned_cases", assigned_to="S1")
        bugs = await client.cases.search("assignedTo:S1")

        log.info("search_complete", total_found=len(bugs))

        for case in bugs[:3]:
            log.info(
                "case_summary",
                case_id=case.id,
                title=case.title[:50],
                status=case.status,
                priority=case.priority,
            )


if __name__ == "__main__":
    asyncio.run(main())
