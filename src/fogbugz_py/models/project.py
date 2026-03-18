"""Pydantic model for FogBugz projects."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Project(BaseModel):
    """FogBugz project model.

    Maps FogBugz API field names to Pythonic names using aliases.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="ixProject")
    name: str = Field(alias="sProjectName")
    description: str | None = Field(alias="sDesc", default=None)
    status: str | None = Field(alias="sStatus", default=None)
