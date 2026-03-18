"""Custom search queries with result limits.

Demonstrates raw search with complex query syntax and pagination.
"""

import asyncio

from log_config import get_logger

from fogbugz_py import FogBugzClient

log = get_logger()


async def main():
    """Search with custom queries and limits."""
    async with FogBugzClient() as client:
        log.info("searching_active_bugs", query="status:active or status:build*", limit=5)
        active_bugs = await client.cases.search("status:active or status:build*", max_results=5)

        log.info("search_complete", total=len(active_bugs))

        for case in active_bugs:
            log.info(
                "case_summary",
                case_id=case.id,
                title=case.title[:50],
                priority=case.priority,
                status=case.status,
            )


if __name__ == "__main__":
    asyncio.run(main())
