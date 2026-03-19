"""Smoke tests for CLI read commands."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from typer.testing import CliRunner

from fogbugz_py.cli import app as cli_app


def test_cli_help_includes_read_command_groups() -> None:
    """Show all read-oriented command groups in top-level help."""
    runner = CliRunner()
    result = runner.invoke(cli_app.build_app(), ["--help"])

    assert result.exit_code == 0
    assert "search" in result.stdout
    assert "case" in result.stdout
    assert "projects" in result.stdout
    assert "people" in result.stdout
    assert "whoami" in result.stdout


def test_cli_read_commands_smoke(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Execute one smoke invocation per read command."""

    monkeypatch.setattr(
        cli_app,
        "search_command",
        lambda options, query, *, max_results=None: [
            SimpleNamespace(
                id=1,
                title="Case 1",
                status="Active",
                assigned_to="A",
                priority=1,
                project="P",
            )
        ],
    )
    monkeypatch.setattr(
        cli_app,
        "get_case_command",
        lambda options, case_id: SimpleNamespace(
            id=case_id,
            title="Case",
            status="Active",
            assigned_to="A",
            priority=1,
            project="P",
            area="Area",
            category="Bug",
        ),
    )
    monkeypatch.setattr(
        cli_app,
        "get_case_events_command",
        lambda options, case_id, *, max_results=None: SimpleNamespace(
            events=[
                SimpleNamespace(
                    id=11,
                    timestamp=datetime(2026, 1, 1, 9, 0, 0),
                    person="A",
                    verb="updated",
                    is_email=False,
                )
            ],
            count=1,
        ),
    )
    monkeypatch.setattr(
        cli_app,
        "list_projects_command",
        lambda options: [SimpleNamespace(id=2, name="Proj", status="Active", description="Desc")],
    )
    monkeypatch.setattr(
        cli_app,
        "get_project_command",
        lambda options, project_id: SimpleNamespace(
            id=project_id,
            name="Proj",
            status="Active",
            description="Desc",
        ),
    )
    monkeypatch.setattr(
        cli_app,
        "search_people_command",
        lambda options, name: [SimpleNamespace(id=3, name="Person", email="p@x", phone="")],
    )
    monkeypatch.setattr(
        cli_app,
        "get_person_command",
        lambda options, person_id: SimpleNamespace(
            id=person_id,
            name="Person",
            email="p@x",
            phone="",
        ),
    )
    monkeypatch.setattr(
        cli_app,
        "whoami_command",
        lambda options: {"id": "99", "name": "Me", "email": "me@x"},
    )

    runner = CliRunner()

    assert runner.invoke(cli_app.build_app(), ["search", "status:open"]).exit_code == 0
    assert runner.invoke(cli_app.build_app(), ["case", "get", "1"]).exit_code == 0
    assert runner.invoke(cli_app.build_app(), ["case", "events", "1"]).exit_code == 0
    assert runner.invoke(cli_app.build_app(), ["projects", "list"]).exit_code == 0
    assert runner.invoke(cli_app.build_app(), ["projects", "get", "2"]).exit_code == 0
    assert runner.invoke(cli_app.build_app(), ["people", "search", "Person"]).exit_code == 0
    assert runner.invoke(cli_app.build_app(), ["people", "get", "3"]).exit_code == 0
    assert runner.invoke(cli_app.build_app(), ["whoami"]).exit_code == 0
