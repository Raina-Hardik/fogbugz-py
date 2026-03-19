"""Search command for CLI."""

from __future__ import annotations

import asyncio

from fogbugz_py import FogBugzClient
from fogbugz_py.cli.context import CLIOptions, resolve_client_kwargs
from fogbugz_py.models.case import Case


def search_command(
    options: CLIOptions, query: str, *, max_results: int | None = None
) -> list[Case]:
    """Search for cases matching a query.

    Args:
        options: Shared CLI options.
        query: FogBugz search query
        max_results: Optional maximum number of results
    """
    return asyncio.run(_search_async(options, query, max_results=max_results))


async def _search_async(
    options: CLIOptions,
    query: str,
    *,
    max_results: int | None = None,
) -> list[Case]:
    kwargs = resolve_client_kwargs(options)
    async with FogBugzClient(**kwargs) as client:
        return await client.cases.search(query, max_results=max_results)
