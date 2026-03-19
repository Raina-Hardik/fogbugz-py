"""Case commands for CLI."""

from __future__ import annotations

import asyncio

from fogbugz_py import FogBugzClient
from fogbugz_py.cli.context import CLIOptions, resolve_client_kwargs
from fogbugz_py.models.case import Case


def get_case_command(options: CLIOptions, case_id: int) -> Case:
    """Get a specific case by ID.

    Args:
        options: Shared CLI options.
        case_id: Case ID to retrieve
    """
    return asyncio.run(_get_case_async(options, case_id))


async def _get_case_async(options: CLIOptions, case_id: int) -> Case:
    kwargs = resolve_client_kwargs(options)
    async with FogBugzClient(**kwargs) as client:
        return await client.cases.get(case_id)
