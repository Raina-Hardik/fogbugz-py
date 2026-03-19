"""Projects resource for listing and retrieving projects."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fogbugz_py.models.project import Project

if TYPE_CHECKING:
    from fogbugz_py.client import FogBugzClient

logger = logging.getLogger("fogbugz_py.resources.projects")


class ProjectsResource:
    """Resource for interacting with FogBugz projects.

    Accessed via `client.projects`.
    """

    def __init__(self, client: FogBugzClient) -> None:
        """Initialize projects resource.

        Args:
            client: Parent FogBugz client
        """
        self._client = client

    async def list(self) -> list[Project]:
        """List all projects.

        Returns:
            List of Project objects

        Raises:
            FogBugzAuthError: If authentication fails
            FogBugzHTTPError: If API request fails

        Example:
            >>> projects = await client.projects.list()
            >>> for project in projects:
            ...     print(project.id, project.name)
        """
        logger.debug("Listing all projects")

        response = await self._client._request(
            "POST",
            "/f/api/0/jsonapi",
            json={"cmd": "listProjects"},
        )

        projects_data = response.get("data", {}).get("projects", [])
        projects = [Project(**self._normalize_project_data(project_data)) for project_data in projects_data]

        logger.debug("Found %d projects", len(projects))
        return projects

    async def get(self, project_id: int) -> Project:
        """Get a specific project by ID.

        Args:
            project_id: Project ID to retrieve

        Returns:
            Project object

        Raises:
            FogBugzNotFoundError: If project doesn't exist
            FogBugzAuthError: If authentication fails
            FogBugzHTTPError: If API request fails

        Example:
            >>> project = await client.projects.get(1)
            >>> print(project.name)
        """
        logger.debug("Getting project %d", project_id)

        response = await self._client._request(
            "POST",
            "/f/api/0/jsonapi",
            json={"cmd": "viewProject", "ixProject": project_id},
        )

        project_data = response.get("data", {}).get("project", {})
        if not project_data:
            raise ValueError(f"Project {project_id} not found")

        project = Project(**self._normalize_project_data(project_data))

        logger.debug("Retrieved project %d", project_id)
        return project

    @staticmethod
    def _normalize_project_data(project_data: dict) -> dict:
        normalized = dict(project_data)

        # Legacy API uses sProject, while the model supports sProjectName.
        if "sProjectName" not in normalized and "sProject" in normalized:
            normalized["sProjectName"] = normalized["sProject"]

        return normalized
