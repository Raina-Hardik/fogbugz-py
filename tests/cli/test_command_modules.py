"""Direct tests for CLI command modules."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from fogbugz_py.cli.commands import case as case_cmd
from fogbugz_py.cli.commands import people as people_cmd
from fogbugz_py.cli.commands import projects as projects_cmd
from fogbugz_py.cli.commands import search as search_cmd
from fogbugz_py.cli.commands import whoami as whoami_cmd
from fogbugz_py.cli.context import CLIOptions


class _FakeClient:
    def __init__(self, **kwargs: Any) -> None:
        self.cases = SimpleNamespace(
            get=self._get_case,
            get_events=self._get_events,
            search=self._search_cases,
        )
        self.projects = SimpleNamespace(
            list=self._list_projects,
            get=self._get_project,
        )
        self.people = SimpleNamespace(
            search=self._search_people,
            get=self._get_person,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        return None

    async def _get_case(self, case_id: int):
        return SimpleNamespace(id=case_id)

    async def _get_events(self, case_id: int, *, max_results: int | None = None):
        return SimpleNamespace(case_id=case_id, count=max_results or 0, events=[])

    async def _search_cases(self, query: str, *, max_results: int | None = None):
        return [SimpleNamespace(query=query, max_results=max_results)]

    async def _list_projects(self):
        return [SimpleNamespace(id=1)]

    async def _get_project(self, project_id: int):
        return SimpleNamespace(id=project_id)

    async def _search_people(self, name: str):
        return [SimpleNamespace(name=name)]

    async def _get_person(self, person_id: int):
        return SimpleNamespace(id=person_id)

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        return {"data": {"person": {"sFullName": "A", "sEmail": "a@example.com", "ixPerson": 9}}}


@pytest.fixture
def options() -> CLIOptions:
    return CLIOptions()


def test_case_command_wrappers(monkeypatch, options: CLIOptions) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(case_cmd, "FogBugzClient", _FakeClient)
    monkeypatch.setattr(
        case_cmd, "resolve_client_kwargs", lambda _options: {"base_url": "x", "token": "y"}
    )

    assert case_cmd.get_case_command(options, 10).id == 10
    assert case_cmd.get_case_events_command(options, 10, max_results=3).count == 3


def test_search_command_wrapper(monkeypatch, options: CLIOptions) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(search_cmd, "FogBugzClient", _FakeClient)
    monkeypatch.setattr(
        search_cmd, "resolve_client_kwargs", lambda _options: {"base_url": "x", "token": "y"}
    )

    result = search_cmd.search_command(options, "status:open", max_results=5)
    assert len(result) == 1


def test_projects_command_wrappers(monkeypatch, options: CLIOptions) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(projects_cmd, "FogBugzClient", _FakeClient)
    monkeypatch.setattr(
        projects_cmd, "resolve_client_kwargs", lambda _options: {"base_url": "x", "token": "y"}
    )

    assert projects_cmd.list_projects_command(options)[0].id == 1
    assert projects_cmd.get_project_command(options, 2).id == 2


def test_people_command_wrappers(monkeypatch, options: CLIOptions) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(people_cmd, "FogBugzClient", _FakeClient)
    monkeypatch.setattr(
        people_cmd, "resolve_client_kwargs", lambda _options: {"base_url": "x", "token": "y"}
    )

    assert people_cmd.search_people_command(options, "alice")[0].name == "alice"
    assert people_cmd.get_person_command(options, 5).id == 5


def test_whoami_command_wrapper(monkeypatch, options: CLIOptions) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(whoami_cmd, "FogBugzClient", _FakeClient)
    monkeypatch.setattr(
        whoami_cmd, "resolve_client_kwargs", lambda _options: {"base_url": "x", "token": "y"}
    )

    result = whoami_cmd.whoami_command(options)
    assert result["name"] == "A"
    assert result["email"] == "a@example.com"
    assert result["id"] == "9"
