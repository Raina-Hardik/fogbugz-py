"""Projects commands for CLI."""

from __future__ import annotations

import asyncio

from fogbugz_py import FogBugzClient
from fogbugz_py.cli.context import CLIOptions, resolve_client_kwargs
from fogbugz_py.models.project import Project


def list_projects_command(options: CLIOptions) -> list[Project]:
    """List all projects."""
    return asyncio.run(_list_projects_async(options))


async def _list_projects_async(options: CLIOptions) -> list[Project]:
    kwargs = resolve_client_kwargs(options)
    async with FogBugzClient(**kwargs) as client:
        return await client.projects.list()
