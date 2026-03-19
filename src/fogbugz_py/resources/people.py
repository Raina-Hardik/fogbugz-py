"""People resource for searching and retrieving users."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from fogbugz_py.models.person import Person

if TYPE_CHECKING:
    from fogbugz_py.client import FogBugzClient

logger = logging.getLogger("fogbugz_py.resources.people")


class PeopleResource:
    """Resource for interacting with FogBugz people (users).

    Accessed via `client.people`.
    """

    def __init__(self, client: FogBugzClient) -> None:
        """Initialize people resource.

        Args:
            client: Parent FogBugz client
        """
        self._client = client

    async def search(self, name: str) -> list[Person]:
        """Search for people by name.

        Args:
            name: Name to search for

        Returns:
            List of Person objects matching the search

        Raises:
            FogBugzAuthError: If authentication fails
            FogBugzHTTPError: If API request fails

        Example:
            >>> people = await client.people.search("John")
            >>> for person in people:
            ...     print(person.id, person.name)
        """
        logger.debug("Searching people with name: %s", name)

        response = await self._client._request(
            "POST",
            "/f/api/0/jsonapi",
            json={"cmd": "listPeople"},
        )

        people_data = response.get("data", {}).get("people", [])
        all_people = [Person(**person_data) for person_data in people_data]

        query = name.casefold()
        people = [
            person
            for person in all_people
            if query in person.name.casefold() or query in (person.email or "").casefold()
        ]

        logger.debug("Found %d people", len(people))
        return people

    async def get(self, person_id: int) -> Person:
        """Get a specific person by ID.

        Args:
            person_id: Person ID to retrieve

        Returns:
            Person object

        Raises:
            FogBugzNotFoundError: If person doesn't exist
            FogBugzAuthError: If authentication fails
            FogBugzHTTPError: If API request fails

        Example:
            >>> person = await client.people.get(1)
            >>> print(person.name, person.email)
        """
        logger.debug("Getting person %d", person_id)

        response = await self._client._request(
            "POST",
            "/f/api/0/jsonapi",
            json={"cmd": "viewPerson", "ixPerson": person_id},
        )

        person_data: dict[str, Any] = response.get("data", {}).get("person", {})
        if not person_data:
            raise ValueError(f"Person {person_id} not found")

        person = Person(**person_data)

        logger.debug("Retrieved person %d", person_id)
        return person
