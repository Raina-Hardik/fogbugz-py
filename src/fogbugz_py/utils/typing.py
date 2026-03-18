"""Type definitions and type aliases."""

from __future__ import annotations

from typing import Protocol, TypeVar

# Type variable for generic responses
T = TypeVar("T")

# JSON types
JSONPrimitive = str | int | float | bool | None
JSONValue = JSONPrimitive | dict[str, "JSONValue"] | list["JSONValue"]
JSONDict = dict[str, JSONValue]


class SupportsClose(Protocol):
    """Protocol for objects that support async close."""

    async def close(self) -> None:
        """Close the resource."""
        ...
