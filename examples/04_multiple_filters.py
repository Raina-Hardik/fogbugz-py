"""Find cases using multiple filters combined.

Demonstrates the Pythonic find() API with several filter parameters
combined with AND logic at the API level.
"""

import asyncio

from log_config import get_logger

from fogbugz_py import FogBugzClient

log = get_logger()


async def main():
    """Find open priority-3 cases in Issue area."""
    async with FogBugzClient() as client:
        log.info(
            "finding_cases",
            status="open",
            priority=3,
            area="Issue",
        )
        filtered = await client.cases.find(status="open", priority=3, area="Issue", max_results=5)

        log.info("cases_found", total=len(filtered))

        for case in filtered[:3]:
            log.info(
                "case_summary",
                case_id=case.id,
                title=case.title[:50],
                priority=case.priority,
                area=case.area,
            )


if __name__ == "__main__":
    asyncio.run(main())
