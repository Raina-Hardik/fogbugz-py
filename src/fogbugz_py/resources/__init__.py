"""FogBugz API resources."""

from __future__ import annotations

from fogbugz_py.resources.cases import CasesResource
from fogbugz_py.resources.people import PeopleResource
from fogbugz_py.resources.projects import ProjectsResource

__all__ = [
    "CasesResource",
    "PeopleResource",
    "ProjectsResource",
]
