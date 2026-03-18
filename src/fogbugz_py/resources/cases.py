"""Cases resource for searching and retrieving cases."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from fogbugz_py.models.case import Case
from fogbugz_py.models.event import Event, EventList

if TYPE_CHECKING:
    from datetime import datetime

    from fogbugz_py.client import FogBugzClient

logger = logging.getLogger("fogbugz_py.resources.cases")


class CasesResource:
    """Resource for interacting with FogBugz cases.

    Accessed via `client.cases`.
    """

    def __init__(self, client: FogBugzClient) -> None:
        """Initialize cases resource.

        Args:
            client: Parent FogBugz client
        """
        self._client = client

    async def search(self, query: str, *, max_results: int | None = None) -> list[Case]:
        """Search for cases matching a query."""
        logger.debug("Searching cases with query: %s", query)

        json_data: dict[str, Any] = {
            "cmd": "search",
            "q": query,
            "cols": [
                "ixBug",
                "sTitle",
                "sStatus",
                "sPersonAssignedTo",
                "sProject",
                "ixPriority",
                "sArea",
                "sCategory",
                "dtOpened",
                "dtClosed",
                "dtResolved",
                "dtLastUpdated",
                "sCustomerEmail",
            ],
        }
        if max_results is not None:
            json_data["max"] = max_results

        response = await self._client._request(
            "POST",
            "/f/api/0/jsonapi",
            json=json_data,
        )

        cases_data = response.get("data", {}).get("cases", [])
        cases = [Case(**case_data) for case_data in cases_data]

        logger.debug("Found %d cases", len(cases))
        return cases

    async def find(
        self,
        *,
        status: str | None = None,
        assigned_to: str | None = None,
        priority: int | None = None,
        area: str | None = None,
        category: str | None = None,
        project: str | None = None,
        opened_after: datetime | None = None,
        opened_before: datetime | None = None,
        closed_after: datetime | None = None,
        closed_before: datetime | None = None,
        updated_after: datetime | None = None,
        updated_before: datetime | None = None,
        max_results: int | None = None,
    ) -> list[Case]:
        """Find cases using structured filters."""
        has_date_filters = any(
            [
                opened_after is not None,
                opened_before is not None,
                closed_after is not None,
                closed_before is not None,
                updated_after is not None,
                updated_before is not None,
            ]
        )

        if has_date_filters:
            return await self._find_with_dates(
                status=status,
                assigned_to=assigned_to,
                priority=priority,
                area=area,
                category=category,
                project=project,
                opened_after=opened_after,
                opened_before=opened_before,
                closed_after=closed_after,
                closed_before=closed_before,
                updated_after=updated_after,
                updated_before=updated_before,
                max_results=max_results,
            )

        query_parts = []

        if status is not None:
            query_parts.append(f"status:'{status}'" if " " in status else f"status:{status}")

        if assigned_to is not None:
            query_parts.append(f"assignedTo:{assigned_to}")

        if priority is not None:
            query_parts.append(f"priority:{priority}")

        if area is not None:
            query_parts.append(f"area:{area}")

        if category is not None:
            query_parts.append(f"category:{category}")

        if project is not None:
            query_parts.append(f"project:{project}")

        if not query_parts:
            logger.warning("find() called with no filters; returning empty list")
            return []

        query = " and ".join(query_parts)
        logger.debug("Finding cases with filters: %s", query)

        return await self.search(query, max_results=max_results)

    async def _find_with_dates(
        self,
        *,
        status: str | None = None,
        assigned_to: str | None = None,
        priority: int | None = None,
        area: str | None = None,
        category: str | None = None,
        project: str | None = None,
        opened_after: datetime | None = None,
        opened_before: datetime | None = None,
        closed_after: datetime | None = None,
        closed_before: datetime | None = None,
        updated_after: datetime | None = None,
        updated_before: datetime | None = None,
        max_results: int | None = None,
    ) -> list[Case]:
        logger.debug("Finding cases with base filters and date constraints")

        cases = await self._search_with_base_filters(
            status=status,
            assigned_to=assigned_to,
            priority=priority,
            area=area,
            category=category,
            project=project,
            max_results=max_results,
        )

        return [
            case
            for case in cases
            if self._matches_date_constraints(
                case,
                opened_after=opened_after,
                opened_before=opened_before,
                closed_after=closed_after,
                closed_before=closed_before,
                updated_after=updated_after,
                updated_before=updated_before,
            )
        ]

    async def _search_with_base_filters(
        self,
        *,
        status: str | None = None,
        assigned_to: str | None = None,
        priority: int | None = None,
        area: str | None = None,
        category: str | None = None,
        project: str | None = None,
        max_results: int | None = None,
    ) -> list[Case]:
        query_parts: list[str] = []

        if status is not None:
            query_parts.append(f"status:'{status}'" if " " in status else f"status:{status}")
        if assigned_to is not None:
            query_parts.append(f"assignedTo:{assigned_to}")
        if priority is not None:
            query_parts.append(f"priority:{priority}")
        if area is not None:
            query_parts.append(f"area:{area}")
        if category is not None:
            query_parts.append(f"category:{category}")
        if project is not None:
            query_parts.append(f"project:{project}")

        if not query_parts:
            logger.warning("Searching all cases (no base filters provided)")
            return []

        query = " and ".join(query_parts)
        logger.debug("Finding cases with base filters: %s", query)
        return await self.search(query, max_results=max_results)

    @staticmethod
    def _matches_date_constraints(
        case: Case,
        *,
        opened_after: datetime | None = None,
        opened_before: datetime | None = None,
        closed_after: datetime | None = None,
        closed_before: datetime | None = None,
        updated_after: datetime | None = None,
        updated_before: datetime | None = None,
    ) -> bool:
        return (
            CasesResource._check_date_range(case.opened, opened_after, opened_before)
            and CasesResource._check_date_range(case.closed, closed_after, closed_before)
            and CasesResource._check_date_range(case.last_updated, updated_after, updated_before)
        )

    @staticmethod
    def _check_date_range(
        case_date: datetime | None,
        after: datetime | None,
        before: datetime | None,
    ) -> bool:
        if not case_date:
            return True

        if after is not None and case_date < after:
            return False
        return not (before is not None and case_date > before)

    async def get(self, case_id: int) -> Case:
        logger.debug("Getting case %d", case_id)

        response = await self._client._request(
            "POST",
            "/f/api/0/jsonapi",
            json={
                "cmd": "search",
                "q": f"ixBug:{case_id}",
                "cols": [
                    "ixBug",
                    "sTitle",
                    "sStatus",
                    "sPersonAssignedTo",
                    "sProject",
                    "ixPriority",
                    "sArea",
                    "sCategory",
                    "dtOpened",
                    "dtLastUpdated",
                    "sCustomerEmail",
                ],
            },
        )

        cases_data = response.get("data", {}).get("cases", [])
        if not cases_data:
            raise ValueError(f"Case {case_id} not found")

        return Case(**cases_data[0])

    async def get_events(
        self,
        case_id: int,
        *,
        max_results: int | None = None,
    ) -> EventList:
        logger.debug("Fetching events for case %d", case_id)

        json_data: dict[str, Any] = {
            "cmd": "search",
            "q": f"ixBug:{case_id}",
            "cols": ["ixBug", "sTitle", "sStatus", "events"],
        }
        if max_results is not None:
            json_data["max"] = max_results

        response = await self._client._request(
            "POST",
            "/f/api/0/jsonapi",
            json=json_data,
        )

        cases_data = response.get("data", {}).get("cases", [])
        if not cases_data:
            return EventList(case_id=case_id, events=[], count=0)

        events_data = cases_data[0].get("events", [])
        events = [Event(**event_data) for event_data in events_data]

        return EventList(case_id=case_id, events=events, count=len(events))
