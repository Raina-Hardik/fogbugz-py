"""Tests for cases resource."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from fogbugz_py.resources.cases import CasesResource


class _FakeClient:
    def __init__(self, response: dict) -> None:
        self.response = response

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:  # noqa: ANN003
        return self.response


@pytest.mark.asyncio
async def test_search_returns_case_models() -> None:
    """Return parsed Case models for search results."""
    client = _FakeClient(
        {
            "data": {
                "cases": [
                    {
                        "ixBug": 123,
                        "sTitle": "Case A",
                        "sStatus": "Active",
                        "sPersonAssignedTo": "Alice",
                    }
                ]
            }
        }
    )
    resource = CasesResource(client)

    cases = await resource.search("status:open")

    assert len(cases) == 1
    assert cases[0].id == 123
    assert cases[0].title == "Case A"


@pytest.mark.asyncio
async def test_find_without_filters_returns_empty_list() -> None:
    """Return empty list when find has no filters."""
    resource = CasesResource(_FakeClient({"data": {"cases": []}}))

    cases = await resource.find()

    assert cases == []


@pytest.mark.asyncio
async def test_find_with_date_filters_applies_client_side_constraints() -> None:
    """Filter date-constrained case results client side."""
    now = datetime.now()
    old = now - timedelta(days=30)
    client = _FakeClient(
        {
            "data": {
                "cases": [
                    {
                        "ixBug": 1,
                        "sTitle": "Old case",
                        "sStatus": "Active",
                        "dtLastUpdated": old.isoformat(),
                    },
                    {
                        "ixBug": 2,
                        "sTitle": "Recent case",
                        "sStatus": "Active",
                        "dtLastUpdated": now.isoformat(),
                    },
                ]
            }
        }
    )
    resource = CasesResource(client)

    cases = await resource.find(status="Active", updated_after=now - timedelta(days=1))

    assert [case.id for case in cases] == [2]


@pytest.mark.asyncio
async def test_get_raises_value_error_when_case_missing() -> None:
    """Raise ValueError when requested case is absent."""
    resource = CasesResource(_FakeClient({"data": {"cases": []}}))

    with pytest.raises(ValueError, match="Case 999 not found"):
        await resource.get(999)


@pytest.mark.asyncio
async def test_get_events_returns_count_and_models() -> None:
    """Return EventList with parsed events for case history."""
    client = _FakeClient(
        {
            "data": {
                "cases": [
                    {
                        "events": [
                            {
                                "ixBugEvent": 10,
                                "ixBug": 123,
                                "sVerb": "edited",
                                "sPerson": "Alice",
                                "dt": "2026-01-01T10:00:00",
                            }
                        ]
                    }
                ]
            }
        }
    )
    resource = CasesResource(client)

    result = await resource.get_events(123)

    assert result.case_id == 123
    assert result.count == 1
    assert result.events[0].id == 10
