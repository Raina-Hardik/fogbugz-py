"""Tests for CLI people commands."""

from __future__ import annotations

from types import SimpleNamespace

from typer.testing import CliRunner

from fogbugz_py.cli import app as cli_app


def test_people_search_renders_results(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Render a people table for search results."""

    def fake_people_search(options, name):  # type: ignore[no-untyped-def]
        assert name == "Alice"
        return [SimpleNamespace(id=11, name="Alice Smith", email="alice@example.com", phone="123")]

    monkeypatch.setattr(cli_app, "search_people_command", fake_people_search)

    runner = CliRunner()
    result = runner.invoke(cli_app.build_app(), ["people", "search", "Alice"])

    assert result.exit_code == 0
    assert "Alice Smith" in result.stdout


def test_people_get_renders_person(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Render one person row for people get command."""

    def fake_get_person(options, person_id):  # type: ignore[no-untyped-def]
        assert person_id == 21
        return SimpleNamespace(id=21, name="Bob Jones", email="bob@example.com", phone="")

    monkeypatch.setattr(cli_app, "get_person_command", fake_get_person)

    runner = CliRunner()
    result = runner.invoke(cli_app.build_app(), ["people", "get", "21"])

    assert result.exit_code == 0
    assert "Bob Jones" in result.stdout
