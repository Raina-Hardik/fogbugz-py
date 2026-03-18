"""Fetch and display a specific case by ID.

Demonstrates basic case retrieval and field access.
"""

import asyncio

from log_config import get_logger

from fogbugz_py import FogBugzClient

log = get_logger()


async def main():
    """Fetch a specific bug by ID."""
    async with FogBugzClient() as client:
        log.info("fetching_case", case_id=25201)
        bug = await client.cases.get(25201)

        log.info(
            "case_retrieved",
            case_id=bug.id,
            title=bug.title,
            status=bug.status,
            assigned_to=bug.assigned_to,
            priority=bug.priority,
            area=bug.area,
            category=bug.category,
        )


if __name__ == "__main__":
    asyncio.run(main())
