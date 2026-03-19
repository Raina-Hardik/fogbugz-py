"""Additional coverage-focused tests for small utility modules."""

from __future__ import annotations

import builtins
from collections.abc import Sequence
from types import ModuleType
from typing import Any

import pytest


def test_constants_values() -> None:
    from fogbugz_py import constants

    assert constants.API_PATH == "/f/api/0/jsonapi"
    assert constants.DEFAULT_TIMEOUT == 30.0
    assert constants.DEFAULT_MAX_RETRIES == 3
    assert constants.DEFAULT_MAX_WAIT_SECONDS == 60
    assert constants.USER_AGENT.startswith("fogbugz-py/")


def test_http_errors_exports() -> None:
    from fogbugz_py.exceptions import FogBugzAuthError
    from fogbugz_py.http import errors

    assert "FogBugzAuthError" in errors.__all__
    assert errors.FogBugzAuthError is FogBugzAuthError


def test_timeout_config_total() -> None:
    from fogbugz_py.http.timeouts import TimeoutConfig

    config = TimeoutConfig(connect=1.0, read=2.0, write=3.0, pool=4.0)
    assert config.total == 4.0


def test_setup_logging_import_error(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from fogbugz_py.logging.setup import setup_logging

    original_import = builtins.__import__

    def fake_import(
        name: str,
        globals: dict[str, Any] | None = None,
        locals: dict[str, Any] | None = None,
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> ModuleType:
        if name == "structlog":
            raise ImportError("missing structlog")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ImportError):
        setup_logging()


def test_setup_logging_not_implemented() -> None:
    from fogbugz_py.logging.setup import setup_logging

    with pytest.raises(NotImplementedError):
        setup_logging()


def test_json_typing_aliases() -> None:
    from fogbugz_py.utils.typing import JSONDict

    value: JSONDict = {"ok": True, "items": [1, "two", None], "obj": {"k": "v"}}
    assert value["ok"] is True
