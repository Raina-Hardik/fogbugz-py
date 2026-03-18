"""Tests for the FogBugzClient class."""

from __future__ import annotations

import httpx
import pytest
import respx

from fogbugz_py import FogBugzClient
from fogbugz_py.exceptions import FogBugzAuthError, FogBugzNotFoundError
from fogbugz_py.models.case import Case
from fogbugz_py.models.person import Person
from fogbugz_py.models.project import Project


class TestFogBugzClientInit:
    """Test FogBugzClient initialization."""

    def test_init_with_token(self) -> None:
        """Test client initialization with API token."""
        client = FogBugzClient(
            base_url="https://example.manuscript.com",
            token="test-token",
        )
        assert client is not None

    def test_init_with_username_password(self) -> None:
        """Test client initialization with username/password."""
        client = FogBugzClient(
            base_url="https://example.manuscript.com",
            username="user",
            password="pass",
        )
        assert client is not None

    def test_init_requires_auth(self) -> None:
        """Test client initialization fails without authentication."""
        with pytest.raises(Exception):  # FogBugzAuthError
            FogBugzClient(base_url="https://example.manuscript.com")

    def test_init_with_custom_http_settings(self) -> None:
        """Test client initialization with custom HTTP settings."""
        client = FogBugzClient(
            base_url="https://example.manuscript.com",
            token="test-token",
            timeout=60.0,
            max_retries=5,
            max_wait_seconds=120,
        )
        assert client is not None


class TestFogBugzClientContextManager:
    """Test FogBugzClient async context manager functionality."""

    @pytest.mark.asyncio
    async def test_context_manager_initialization(self) -> None:
        """Test client context manager properly initializes."""
        async with FogBugzClient(
            base_url="https://example.manuscript.com",
            token="test-token",
        ) as client:
            assert client is not None
            assert client.cases is not None
            assert client.projects is not None
            assert client.people is not None

    @pytest.mark.asyncio
    async def test_resource_access_outside_context_raises_error(self) -> None:
        """Test accessing resources outside context raises error."""
        client = FogBugzClient(
            base_url="https://example.manuscript.com",
            token="test-token",
        )

        with pytest.raises(RuntimeError):
            _ = client.cases

    @pytest.mark.asyncio
    async def test_request_outside_context_raises_error(self) -> None:
        """Test making request outside context raises error."""
        client = FogBugzClient(
            base_url="https://example.manuscript.com",
            token="test-token",
        )

        with pytest.raises(RuntimeError):
            await client._request("GET", "/api/v3/cases")


class TestCasesResource:
    """Test cases resource functionality."""

    @pytest.mark.asyncio
    async def test_search_cases(self) -> None:
        """Test searching for cases."""
        with respx.mock:
            respx.post("https://example.manuscript.com/api/search").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "data": {
                            "cases": [
                                {
                                    "ixBug": 1,
                                    "sTitle": "Test Case",
                                    "sStatus": "Active",
                                    "sPersonAssignedTo": "John",
                                }
                            ]
                        }
                    },
                )
            )

            async with FogBugzClient(
                base_url="https://example.manuscript.com",
                token="test-token",
            ) as client:
                cases = await client.cases.search("status:open")
                assert len(cases) == 1
                assert isinstance(cases[0], Case)
                assert cases[0].id == 1
                assert cases[0].title == "Test Case"

    @pytest.mark.asyncio
    async def test_get_case(self) -> None:
        """Test retrieving a specific case."""
        with respx.mock:
            respx.post("https://example.manuscript.com/api/search").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "data": {
                            "cases": [
                                {
                                    "ixBug": 1234,
                                    "sTitle": "Important Bug",
                                    "sStatus": "Active",
                                    "ixPriority": 1,
                                }
                            ]
                        }
                    },
                )
            )

            async with FogBugzClient(
                base_url="https://example.manuscript.com",
                token="test-token",
            ) as client:
                case = await client.cases.get(1234)
                assert isinstance(case, Case)
                assert case.id == 1234
                assert case.title == "Important Bug"
                assert case.priority == 1

    @pytest.mark.asyncio
    async def test_search_cases_with_max_results(self) -> None:
        """Test searching cases with max_results parameter."""
        with respx.mock:
            respx.post("https://example.manuscript.com/api/search").mock(
                return_value=httpx.Response(
                    200,
                    json={"data": {"cases": []}},
                )
            )

            async with FogBugzClient(
                base_url="https://example.manuscript.com",
                token="test-token",
            ) as client:
                await client.cases.search("status:open", max_results=10)


class TestProjectsResource:
    """Test projects resource functionality."""

    @pytest.mark.asyncio
    async def test_list_projects(self) -> None:
        """Test listing all projects."""
        with respx.mock:
            respx.get("https://example.manuscript.com/api/v3/projects").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "projects": [
                            {
                                "ixProject": 1,
                                "sProjectName": "Project A",
                                "sDesc": "First project",
                            },
                            {
                                "ixProject": 2,
                                "sProjectName": "Project B",
                                "sDesc": "Second project",
                            },
                        ]
                    },
                )
            )

            async with FogBugzClient(
                base_url="https://example.manuscript.com",
                token="test-token",
            ) as client:
                projects = await client.projects.list()
                assert len(projects) == 2
                assert isinstance(projects[0], Project)
                assert projects[0].id == 1
                assert projects[0].name == "Project A"

    @pytest.mark.asyncio
    async def test_get_project(self) -> None:
        """Test retrieving a specific project."""
        with respx.mock:
            respx.get("https://example.manuscript.com/api/v3/projects/1").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "ixProject": 1,
                        "sProjectName": "Main Project",
                        "sDesc": "Main project description",
                        "sStatus": "Active",
                    },
                )
            )

            async with FogBugzClient(
                base_url="https://example.manuscript.com",
                token="test-token",
            ) as client:
                project = await client.projects.get(1)
                assert isinstance(project, Project)
                assert project.id == 1
                assert project.name == "Main Project"


class TestPeopleResource:
    """Test people resource functionality."""

    @pytest.mark.asyncio
    async def test_search_people(self) -> None:
        """Test searching for people."""
        with respx.mock:
            respx.get("https://example.manuscript.com/api/v3/people").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "people": [
                            {
                                "ixPerson": 1,
                                "sFullName": "John Doe",
                                "sEmail": "john@example.com",
                            }
                        ]
                    },
                )
            )

            async with FogBugzClient(
                base_url="https://example.manuscript.com",
                token="test-token",
            ) as client:
                people = await client.people.search("John")
                assert len(people) == 1
                assert isinstance(people[0], Person)
                assert people[0].id == 1
                assert people[0].name == "John Doe"

    @pytest.mark.asyncio
    async def test_get_person(self) -> None:
        """Test retrieving a specific person."""
        with respx.mock:
            respx.get("https://example.manuscript.com/api/v3/people/1").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "ixPerson": 1,
                        "sFullName": "John Doe",
                        "sEmail": "john@example.com",
                        "sPhone": "555-1234",
                    },
                )
            )

            async with FogBugzClient(
                base_url="https://example.manuscript.com",
                token="test-token",
            ) as client:
                person = await client.people.get(1)
                assert isinstance(person, Person)
                assert person.id == 1
                assert person.name == "John Doe"
                assert person.email == "john@example.com"


class TestClientErrorHandling:
    """Test error handling in client."""

    @pytest.mark.asyncio
    async def test_auth_error_on_401(self) -> None:
        """Test authentication error on 401 response."""
        with respx.mock:
            respx.post("https://example.manuscript.com/api/search").mock(
                return_value=httpx.Response(401)
            )

            async with FogBugzClient(
                base_url="https://example.manuscript.com",
                token="invalid-token",
            ) as client:
                with pytest.raises(FogBugzAuthError):
                    await client.cases.search("status:open")

    @pytest.mark.asyncio
    async def test_not_found_error_on_404(self) -> None:
        """Test not found error on 404 response."""
        with respx.mock:
            respx.post("https://example.manuscript.com/api/search").mock(
                return_value=httpx.Response(404)
            )

            async with FogBugzClient(
                base_url="https://example.manuscript.com",
                token="test-token",
            ) as client:
                with pytest.raises(FogBugzNotFoundError):
                    await client.cases.get(9999)
