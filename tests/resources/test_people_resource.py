"""Tests for people resource."""

from __future__ import annotations

from typing import Any, cast

import pytest

from fogbugz_py.resources.people import PeopleResource


class _FakeClient:
    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        return self.response


@pytest.mark.asyncio
async def test_search_people_returns_models() -> None:
    """Return parsed Person models from search response."""
    resource = PeopleResource(
        cast(
            Any,
            _FakeClient(
                {
                    "data": {
                        "people": [
                            {
                                "ixPerson": 7,
                                "sFullName": "Alice Smith",
                                "sEmail": "alice@example.com",
                            },
                            {
                                "ixPerson": 8,
                                "sFullName": "Bob Jones",
                                "sEmail": "bob@example.com",
                            },
                        ]
                    }
                }
            ),
        )
    )

    people = await resource.search("alice")

    assert len(people) == 1
    assert people[0].id == 7
    assert people[0].name == "Alice Smith"


@pytest.mark.asyncio
async def test_get_person_returns_model() -> None:
    """Return parsed Person model for person ID request."""
    resource = PeopleResource(
        cast(
            Any,
            _FakeClient(
                {
                    "data": {
                        "person": {
                            "ixPerson": 21,
                            "sFullName": "Bob Jones",
                            "sEmail": "bob@example.com",
                            "sPhone": "555-0101",
                        }
                    }
                }
            ),
        )
    )

    person = await resource.get(21)

    assert person.id == 21
    assert person.name == "Bob Jones"
    assert person.phone == "555-0101"


@pytest.mark.asyncio
async def test_get_person_raises_value_error_when_missing() -> None:
    """Raise ValueError when requested person is absent."""
    resource = PeopleResource(cast(Any, _FakeClient({"data": {"person": {}}})))

    with pytest.raises(ValueError, match="Person 101 not found"):
        await resource.get(101)
