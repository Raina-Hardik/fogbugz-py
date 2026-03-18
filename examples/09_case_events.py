"""Example: Fetch and display case events.

This example demonstrates how to retrieve all events associated with a specific
bug/case, which tracks all changes, comments, assignments, and other actions
that occurred on that case.
"""

import asyncio

from log_config import get_logger

from fogbugz_py.client import FogBugzClient

log = get_logger()


async def main() -> None:
    """Fetch events for a specific case and display them."""
    async with FogBugzClient() as client:
        # Example: Get events for case ID 28470
        case_id = 28470
        log.info("fetching_case_events", case_id=case_id)

        try:
            event_list = await client.cases.get_events(case_id)

            log.info(
                "case_events_retrieved",
                case_id=event_list.case_id,
                event_count=event_list.count,
            )

            # Display all events
            for event in event_list.events:
                log.info(
                    "event_detail",
                    timestamp=event.timestamp.isoformat(),
                    person=event.person,
                    event_type=event.verb,
                    changes=event.changes,
                    text=event.text,
                )

            # Example: Filter for specific event types
            log.info("filtering_comments", case_id=case_id)
            comments = [e for e in event_list.events if "comment" in e.verb.lower()]
            for comment in comments:
                log.info(
                    "comment_event",
                    timestamp=comment.timestamp.isoformat(),
                    person=comment.person,
                    text=comment.text,
                )

            # Example: Filter for assignment changes
            log.info("filtering_assignments", case_id=case_id)
            assignments = [e for e in event_list.events if "assign" in e.verb.lower()]
            for assignment in assignments:
                log.info(
                    "assignment_event",
                    timestamp=assignment.timestamp.isoformat(),
                    changes=assignment.changes,
                    person=assignment.person,
                )

        except ValueError as e:
            log.error("event_fetch_error", error=str(e))


if __name__ == "__main__":
    asyncio.run(main())
