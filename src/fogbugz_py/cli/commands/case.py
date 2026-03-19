"""Case commands for CLI."""

from __future__ import annotations

import asyncio

from fogbugz_py import FogBugzClient
from fogbugz_py.cli.context import CLIOptions, resolve_client_kwargs
from fogbugz_py.models.case import Case
from fogbugz_py.models.event import EventList


def get_case_command(options: CLIOptions, case_id: int) -> Case:
    """Get a specific case by ID.

    Args:
        options: Shared CLI options.
        case_id: Case ID to retrieve
    """
    return asyncio.run(_get_case_async(options, case_id))


def get_case_events_command(
    options: CLIOptions,
    case_id: int,
    *,
    max_results: int | None = None,
) -> EventList:
    """Get events for a specific case by ID."""
    return asyncio.run(_get_case_events_async(options, case_id, max_results=max_results))


async def _get_case_async(options: CLIOptions, case_id: int) -> Case:
    kwargs = resolve_client_kwargs(options)
    async with FogBugzClient(**kwargs) as client:
        return await client.cases.get(case_id)


async def _get_case_events_async(
    options: CLIOptions,
    case_id: int,
    *,
    max_results: int | None = None,
) -> EventList:
    kwargs = resolve_client_kwargs(options)
    async with FogBugzClient(**kwargs) as client:
        return await client.cases.get_events(case_id, max_results=max_results)
