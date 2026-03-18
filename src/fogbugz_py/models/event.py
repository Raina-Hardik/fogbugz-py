"""Pydantic model for FogBugz case events."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class EventType(str, Enum):
    """Types of events that can occur on a case."""

    OPENED = "opened"
    CLOSED = "closed"
    REOPENED = "reopened"
    ASSIGNED = "assigned"
    REASSIGNED = "reassigned"
    COMMENTED = "commented"
    CHANGED = "changed"
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    MIGRATED = "migrated"
    ATTACHMENT_ADDED = "attachment_added"
    CUSTOM_FIELD_CHANGED = "custom_field_changed"


class Event(BaseModel):
    """FogBugz case event model.

    Represents a change or action that occurred on a case.
    Maps FogBugz API field names to Pythonic names using aliases.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="ixBugEvent")
    case_id: int = Field(alias="ixBug")
    verb: str = Field(alias="sVerb")
    person: str = Field(alias="sPerson")
    person_id: int | None = Field(alias="ixPerson", default=None)
    timestamp: datetime = Field(alias="dt")
    changes: str | None = Field(alias="sChanges", default=None)
    text: str | None = Field(alias="s", default=None)
    event_type_code: int | None = Field(alias="evt", default=None)
    person_assigned_to: int | None = Field(alias="ixPersonAssignedTo", default=None)
    is_email: bool = Field(alias="fEmail", default=False)
    is_html: bool = Field(alias="fHTML", default=False)
    is_external: bool = Field(alias="fExternal", default=False)

    # Email-specific fields
    email_from: str | None = Field(alias="sFrom", default=None)
    email_to: str | None = Field(alias="sTo", default=None)
    email_cc: str | None = Field(alias="sCC", default=None)
    email_bcc: str | None = Field(alias="sBCC", default=None)
    email_reply_to: str | None = Field(alias="sReplyTo", default=None)
    email_subject: str | None = Field(alias="sSubject", default=None)


class EventList(BaseModel):
    """Result from fetching case events."""

    case_id: int
    events: list[Event]
    count: int
