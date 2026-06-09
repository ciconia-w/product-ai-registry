import re


class ProjectMixin:
    """Mixin class for project-related operations."""

    def list_projects(self):
        """List all projects."""
        path = "/project-all.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def view_project(self, project_id):
        """View project details."""
        path = f"/project-view-{project_id}.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def list_project_tasks(self):
        """List tasks in a project."""
        path = f"/project-task-{project_id}.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def project_builds(self):
        """List builds in a project."""
        path = f"/project-build-{project_id}.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def project_team(self):
        """List team members in a project."""
        path = f"/project-team-{project_id}.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def project_dynamics(self):
        """View project activity log."""
        path = f"/project-dynamic-{project_id}.html"
        headers = {}
        return self._request("GET", path, headers=headers)
