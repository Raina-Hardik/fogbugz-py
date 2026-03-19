"""Tests for CLI output formatter."""

from __future__ import annotations

import builtins

from fogbugz_py.cli.output import OutputFormatter


def test_format_table_empty(capsys) -> None:
    OutputFormatter.format_table([])
    captured = capsys.readouterr()
    assert "No results found." in captured.out


def test_format_table_fallback_without_rich(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # type: ignore[no-untyped-def]
        if name.startswith("rich"):
            raise ImportError("missing rich")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    OutputFormatter.format_table([{"ID": 1, "Name": "A", "NoneField": None}], title="Results")
    captured = capsys.readouterr()

    assert "Results" in captured.out
    assert "ID | Name | NoneField" in captured.out
    assert "1 | A |" in captured.out
