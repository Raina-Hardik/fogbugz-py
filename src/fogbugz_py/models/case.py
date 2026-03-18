"""Pydantic model for FogBugz cases."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Case(BaseModel):
    """FogBugz case model.

    Maps FogBugz API field names to Pythonic names using aliases.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="ixBug")
    title: str = Field(alias="sTitle")
    status: str = Field(alias="sStatus")
    assigned_to: str | None = Field(alias="sPersonAssignedTo", default=None)
    priority: int | None = Field(alias="ixPriority", default=None)
    project: str | None = Field(alias="sProject", default=None)
    area: str | None = Field(alias="sArea", default=None)
    category: str | None = Field(alias="sCategory", default=None)
    opened: datetime | None = Field(alias="dtOpened", default=None)
    closed: datetime | None = Field(alias="dtClosed", default=None)
    resolved: datetime | None = Field(alias="dtResolved", default=None)
    last_updated: datetime | None = Field(alias="dtLastUpdated", default=None)
    customer_email: str | None = Field(alias="sCustomerEmail", default=None)
    
    @field_validator("opened", "closed", "resolved", "last_updated", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

class CaseSearchResult(BaseModel):
    """Result from a case search operation."""

    cases: list[Case]
    count: int
