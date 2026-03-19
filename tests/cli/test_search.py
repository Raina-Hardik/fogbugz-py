"""Tests for CLI commands."""

from __future__ import annotations

from types import SimpleNamespace

from typer.testing import CliRunner

from fogbugz_py.cli import app as cli_app
from fogbugz_py.exceptions import FogBugzClientError


def test_search_command_renders_results(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Render search output for matching cases."""

    def fake_search(options, query, *, max_results=None):  # type: ignore[no-untyped-def]
        assert query == "status:open"
        assert max_results == 5
        return [
            SimpleNamespace(
                id=123,
                title="Example bug",
                status="Active",
                assigned_to="Alice",
                priority=1,
                project="Core",
            )
        ]

    monkeypatch.setattr(cli_app, "search_command", fake_search)

    runner = CliRunner()
    result = runner.invoke(cli_app.build_app(), ["search", "status:open", "--max", "5"])

    assert result.exit_code == 0
    assert "Example bug" in result.stdout


def test_case_get_command_renders_case(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Render case details for case get command."""

    def fake_get_case(options, case_id):  # type: ignore[no-untyped-def]
        assert case_id == 42
        return SimpleNamespace(
            id=42,
            title="Login page broken",
            status="Open",
            assigned_to="Bob",
            priority=2,
            project="Auth",
            area="UI",
            category="Bug",
        )

    monkeypatch.setattr(cli_app, "get_case_command", fake_get_case)

    runner = CliRunner()
    result = runner.invoke(cli_app.build_app(), ["case", "get", "42"])

    assert result.exit_code == 0
    assert "Case 42" in result.stdout


def test_projects_list_command_renders_projects(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Render project list for projects list command."""

    def fake_list_projects(options):  # type: ignore[no-untyped-def]
        return [SimpleNamespace(id=7, name="Platform", status="Active", description="Core systems")]

    monkeypatch.setattr(cli_app, "list_projects_command", fake_list_projects)

    runner = CliRunner()
    result = runner.invoke(cli_app.build_app(), ["projects", "list"])

    assert result.exit_code == 0
    assert "Platform" in result.stdout


def test_whoami_command_renders_name(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Render current user name for whoami command."""

    def fake_whoami(options):  # type: ignore[no-untyped-def]
        return {"name": "Charlie"}

    monkeypatch.setattr(cli_app, "whoami_command", fake_whoami)

    runner = CliRunner()
    result = runner.invoke(cli_app.build_app(), ["whoami"])

    assert result.exit_code == 0
    assert "Charlie" in result.stdout


def test_search_command_surfaces_error(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Exit with code 1 and print user-friendly error when command fails."""

    def failing_search(options, query, *, max_results=None):  # type: ignore[no-untyped-def]
        raise FogBugzClientError("bad request", status_code=400)

    monkeypatch.setattr(cli_app, "search_command", failing_search)

    runner = CliRunner()
    result = runner.invoke(cli_app.build_app(), ["search", "status:open"])

    assert result.exit_code == 1
    assert "Error: bad request" in result.stderr
