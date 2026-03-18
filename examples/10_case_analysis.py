"""Example: Comprehensive case analysis with full history.

This example demonstrates how to fetch a complete picture of a case including
its metadata and full event history, enabling analysis of the case lifecycle,
who worked on it, what changed, and when.
"""

import asyncio
from collections import defaultdict

from log_config import get_logger

from fogbugz_py.client import FogBugzClient

log = get_logger()


async def main() -> None:
    """Fetch and analyze a case comprehensively."""
    async with FogBugzClient() as client:
        case_id = 28470
        log.info("comprehensive_case_analysis", case_id=case_id)

        # Get the case metadata
        case = await client.cases.get(case_id)
        log.info(
            "case_metadata",
            id=case.id,
            title=case.title,
            status=case.status,
            assigned_to=case.assigned_to,
            priority=case.priority,
            area=case.area,
            category=case.category,
            project=case.project,
            opened=case.opened.isoformat() if case.opened else None,
            resolved=case.resolved.isoformat() if case.resolved else None,
            closed=case.closed.isoformat() if case.closed else None,
            last_updated=case.last_updated.isoformat() if case.last_updated else None,
        )

        # Get all events for the case
        log.info("fetching_case_history", case_id=case_id)
        events_list = await client.cases.get_events(case_id)

        if not events_list.events:
            log.info("no_history_found", case_id=case_id)
            return

        log.info("case_history_retrieved", total_events=events_list.count)

        # Analyze events by type
        events_by_type = defaultdict(list)
        events_by_person = defaultdict(list)

        for event in events_list.events:
            events_by_type[event.verb].append(event)
            events_by_person[event.person].append(event)

        log.info("event_type_breakdown", types=list(events_by_type.keys()))
        log.info(
            "contributors_breakdown",
            contributors=list(events_by_person.keys()),
            contributor_count=len(events_by_person),
        )

        # Timeline analysis
        if events_list.events:
            first_event = min(events_list.events, key=lambda e: e.timestamp)
            last_event = max(events_list.events, key=lambda e: e.timestamp)
            duration = last_event.timestamp - first_event.timestamp

            log.info(
                "case_timeline",
                first_event=first_event.timestamp.isoformat(),
                last_event=last_event.timestamp.isoformat(),
                duration_days=duration.days,
                duration_hours=duration.seconds // 3600,
            )

        # Analyze status changes
        status_changes = [e for e in events_list.events if "Status changed" in (e.changes or "")]
        if status_changes:
            log.info("status_change_history", count=len(status_changes))
            for change_event in status_changes:
                log.info(
                    "status_change",
                    timestamp=change_event.timestamp.isoformat(),
                    person=change_event.person,
                    change=change_event.changes,
                )

        # Analyze ownership changes
        ownership_changes = [e for e in events_list.events if "Owner changed" in (e.changes or "")]
        if ownership_changes:
            log.info("ownership_change_history", count=len(ownership_changes))
            for change_event in ownership_changes:
                log.info(
                    "ownership_change",
                    timestamp=change_event.timestamp.isoformat(),
                    person=change_event.person,
                    change=change_event.changes,
                )

        # Count emails and comments
        emails = [e for e in events_list.events if e.is_email]
        replies = [e for e in events_list.events if e.verb == "Replied"]

        log.info("communication_analysis", emails=len(emails), replies=len(replies))

        # Contributions by person
        log.info("contributions_by_person")
        for person, person_events in sorted(
            events_by_person.items(), key=lambda x: len(x[1]), reverse=True
        ):
            event_types = defaultdict(int)
            for e in person_events:
                event_types[e.verb] += 1
            log.info(
                "person_contribution",
                person=person,
                total_events=len(person_events),
                event_types=dict(event_types),
            )


if __name__ == "__main__":
    asyncio.run(main())
