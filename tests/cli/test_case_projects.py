"""Tests for case and project read commands in CLI."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from typer.testing import CliRunner

from fogbugz_py.cli import app as cli_app


def test_case_events_renders_rows(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Render events table for a case."""

    def fake_case_events(options, case_id, *, max_results=None):  # type: ignore[no-untyped-def]
        assert case_id == 28686
        assert max_results == 2
        events = [
            SimpleNamespace(
                id=901,
                timestamp=datetime(2026, 1, 1, 10, 0, 0),
                person="Alice",
                verb="edited",
                is_email=False,
            )
        ]
        return SimpleNamespace(events=events, count=1)

    monkeypatch.setattr(cli_app, "get_case_events_command", fake_case_events)

    runner = CliRunner()
    result = runner.invoke(cli_app.build_app(), ["case", "events", "28686", "--max", "2"])

    assert result.exit_code == 0
    assert "Case 28686 Events" in result.stdout
    assert "Alice" in result.stdout


def test_projects_get_renders_project(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Render one project row for projects get command."""

    def fake_project_get(options, project_id):  # type: ignore[no-untyped-def]
        assert project_id == 2
        return SimpleNamespace(id=2, name="IDesignSpec", status="Active", description="Core")

    monkeypatch.setattr(cli_app, "get_project_command", fake_project_get)

    runner = CliRunner()
    result = runner.invoke(cli_app.build_app(), ["projects", "get", "2"])

    assert result.exit_code == 0
    assert "Project 2" in result.stdout
    assert "IDesignSpec" in result.stdout
