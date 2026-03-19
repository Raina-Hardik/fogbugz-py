"""People commands for CLI."""

from __future__ import annotations

import asyncio

from fogbugz_py import FogBugzClient
from fogbugz_py.cli.context import CLIOptions, resolve_client_kwargs
from fogbugz_py.models.person import Person


def search_people_command(options: CLIOptions, name: str) -> list[Person]:
    """Search people by full or partial name."""
    return asyncio.run(_search_people_async(options, name))


def get_person_command(options: CLIOptions, person_id: int) -> Person:
    """Get one person by ID."""
    return asyncio.run(_get_person_async(options, person_id))


async def _search_people_async(options: CLIOptions, name: str) -> list[Person]:
    kwargs = resolve_client_kwargs(options)
    async with FogBugzClient(**kwargs) as client:
        return await client.people.search(name)


async def _get_person_async(options: CLIOptions, person_id: int) -> Person:
    kwargs = resolve_client_kwargs(options)
    async with FogBugzClient(**kwargs) as client:
        return await client.people.get(person_id)
