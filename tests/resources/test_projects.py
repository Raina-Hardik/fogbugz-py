"""Tests for projects resource."""

from __future__ import annotations

from typing import Any, cast

import pytest

from fogbugz_py.resources.projects import ProjectsResource


class _FakeClient:
    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        return self.response


@pytest.mark.asyncio
async def test_list_projects_normalizes_legacy_name_field() -> None:
    """Map legacy sProject field to Project.name."""
    client = _FakeClient(
        {
            "data": {
                "projects": [
                    {
                        "ixProject": 2,
                        "sProject": "IDesignSpec",
                        "sStatus": "Active",
                    }
                ]
            }
        }
    )
    resource = ProjectsResource(cast(Any, client))

    projects = await resource.list()

    assert len(projects) == 1
    assert projects[0].id == 2
    assert projects[0].name == "IDesignSpec"


@pytest.mark.asyncio
async def test_get_project_raises_value_error_when_missing() -> None:
    """Raise ValueError when requested project is absent."""
    resource = ProjectsResource(cast(Any, _FakeClient({"data": {"project": {}}})))

    with pytest.raises(ValueError, match="Project 22 not found"):
        await resource.get(22)


@pytest.mark.asyncio
async def test_get_project_returns_model() -> None:
    """Return parsed Project model for viewProject payload."""
    resource = ProjectsResource(
        cast(
            Any,
            _FakeClient(
                {
                    "data": {
                        "project": {
                            "ixProject": 11,
                            "sProject": "IDS-Verify",
                            "sStatus": "Active",
                            "sDesc": "Verification work",
                        }
                    }
                }
            ),
        )
    )

    project = await resource.get(11)

    assert project.id == 11
    assert project.name == "IDS-Verify"
    assert project.description == "Verification work"
