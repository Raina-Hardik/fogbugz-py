"""Tests for case events resource."""

from fogbugz_py.models.event import Event, EventList, EventType


class TestEventModel:
    """Test Event Pydantic model."""

    def test_event_creation_with_all_fields(self) -> None:
        """Test creating an event with all fields populated."""
        event_data = {
            "ixBugEvent": 12345,
            "ixBug": 100,
            "sVerb": "Incoming Email",
            "sPerson": "john@example.com",
            "ixPerson": 42,
            "dt": "2024-01-15T10:30:00Z",
            "sChanges": "Status changed from Open to In Progress",
            "s": "This is an email message",
            "evt": 11,
            "ixPersonAssignedTo": 50,
            "fEmail": True,
            "fHTML": True,
            "fExternal": True,
        }

        event = Event(**event_data)

        assert event.id == 12345
        assert event.case_id == 100
        assert event.verb == "Incoming Email"
        assert event.person == "john@example.com"
        assert event.person_id == 42
        assert event.changes == "Status changed from Open to In Progress"
        assert event.text == "This is an email message"
        assert event.event_type_code == 11
        assert event.is_email is True
        assert event.is_html is True
        assert event.is_external is True

    def test_event_creation_with_minimal_fields(self) -> None:
        """Test creating an event with only required fields."""
        event_data = {
            "ixBugEvent": 12345,
            "ixBug": 100,
            "sVerb": "Assigned",
            "sPerson": "jane@example.com",
            "dt": "2024-01-15T10:30:00Z",
        }

        event = Event(**event_data)

        assert event.id == 12345
        assert event.case_id == 100
        assert event.verb == "Assigned"
        assert event.person_id is None
        assert event.changes is None
        assert event.text is None
        assert event.is_email is False

    def test_event_with_pythonic_field_names(self) -> None:
        """Test that Field aliases work correctly."""
        event = Event(
            ixBugEvent=1,
            ixBug=1,
            sVerb="opened",
            sPerson="user",
            dt="2024-01-15T10:30:00Z",
        )

        assert event.id == 1
        assert event.case_id == 1
        assert event.verb == "opened"
        assert event.person == "user"


class TestEventListModel:
    """Test EventList Pydantic model."""

    def test_event_list_creation(self) -> None:
        """Test creating an EventList."""
        events = [
            Event(
                ixBugEvent=1,
                ixBug=100,
                sVerb="opened",
                sPerson="user1",
                dt="2024-01-15T10:00:00Z",
            ),
            Event(
                ixBugEvent=2,
                ixBug=100,
                sVerb="Replied",
                sPerson="user2",
                dt="2024-01-15T11:00:00Z",
                s="Great issue!",
            ),
        ]

        event_list = EventList(case_id=100, events=events, count=2)

        assert event_list.case_id == 100
        assert len(event_list.events) == 2
        assert event_list.count == 2
        assert event_list.events[0].verb == "opened"
        assert event_list.events[1].text == "Great issue!"

    def test_event_list_empty(self) -> None:
        """Test creating an empty EventList."""
        event_list = EventList(case_id=100, events=[], count=0)

        assert event_list.case_id == 100
        assert len(event_list.events) == 0
        assert event_list.count == 0


class TestEventType:
    """Test EventType enum."""

    def test_event_type_values(self) -> None:
        """Test that EventType enum has expected values."""
        assert EventType.OPENED.value == "opened"
        assert EventType.CLOSED.value == "closed"
        assert EventType.COMMENTED.value == "commented"
        assert EventType.ASSIGNED.value == "assigned"
        assert EventType.REASSIGNED.value == "reassigned"

    def test_event_type_membership(self) -> None:
        """Test that we can check event types."""
        event_type = EventType.COMMENTED
        assert event_type == EventType.COMMENTED
        assert event_type.value == "commented"
