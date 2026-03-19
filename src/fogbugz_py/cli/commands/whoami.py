"""Whoami command for CLI."""

from __future__ import annotations

import asyncio

from fogbugz_py import FogBugzClient
from fogbugz_py.cli.context import CLIOptions, resolve_client_kwargs


def whoami_command(options: CLIOptions) -> dict[str, str]:
    """Show current authenticated user information."""
    return asyncio.run(_whoami_async(options))


async def _whoami_async(options: CLIOptions) -> dict[str, str]:
    kwargs = resolve_client_kwargs(options)
    async with FogBugzClient(**kwargs) as client:
        response = await client._request(
            "POST",
            "/f/api/0/jsonapi",
            json={"cmd": "viewPerson"},
        )

        person = response.get("data", {}).get("person", {})
        return {
            "name": str(person.get("sFullName", "unknown")),
            "email": str(person.get("sEmail", "")),
            "id": str(person.get("ixPerson", "")),
        }
