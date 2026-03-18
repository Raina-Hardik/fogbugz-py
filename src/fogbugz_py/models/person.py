"""Pydantic model for FogBugz people/users."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Person(BaseModel):
    """FogBugz person/user model.

    Maps FogBugz API field names to Pythonic names using aliases.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="ixPerson")
    name: str = Field(alias="sFullName")
    email: str | None = Field(alias="sEmail", default=None)
    phone: str | None = Field(alias="sPhone", default=None)
