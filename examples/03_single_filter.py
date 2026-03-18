"""Find cases using a single structured filter.

Demonstrates the Pythonic find() API with one filter parameter.
"""

import asyncio

from log_config import get_logger

from fogbugz_py import FogBugzClient

log = get_logger()


async def main():
    """Find open cases with priority 1."""
    async with FogBugzClient() as client:
        log.info("finding_cases", status="open", priority=1)
        open_critical = await client.cases.find(status="open", priority=1, max_results=5)

        log.info("cases_found", total=len(open_critical))

        for case in open_critical:
            log.info(
                "case_summary",
                case_id=case.id,
                title=case.title[:50],
                status=case.status,
                priority=case.priority,
            )


if __name__ == "__main__":
    asyncio.run(main())
