"""List all open bugs and the correspondent's email.

Demonstrates retrieving cases with correspondent email information
using the sCustomerEmail field from the FogBugz API.
"""

import asyncio

from log_config import get_logger

from fogbugz_py import FogBugzClient

log = get_logger()


async def main():
    """Fetch all open cases and display correspondent email."""
    async with FogBugzClient() as client:
        log.info("fetching_open_bugs")
        open_bugs = await client.cases.find(status="open")

        log.info("open_bugs_retrieved", total=len(open_bugs))

        for idx, case in enumerate(open_bugs, 1):
            log.info(
                "bug_with_correspondent",
                idx=idx,
                case_id=case.id,
                title=case.title,
                status=case.status,
                correspondent_email=case.customer_email,
                assigned_to=case.assigned_to,
            )


if __name__ == "__main__":
    asyncio.run(main())
