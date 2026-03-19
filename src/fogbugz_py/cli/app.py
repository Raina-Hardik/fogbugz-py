"""Main CLI application using Typer.

Only available when fogbugz-py[typer] is installed.
"""

from __future__ import annotations

from typing import Any

from fogbugz_py.cli.commands.case import get_case_command
from fogbugz_py.cli.commands.people import get_person_command, search_people_command
from fogbugz_py.cli.commands.projects import list_projects_command
from fogbugz_py.cli.commands.search import search_command
from fogbugz_py.cli.commands.whoami import whoami_command
from fogbugz_py.cli.context import CLIOptions
from fogbugz_py.cli.output import OutputFormatter
from fogbugz_py.exceptions import FogBugzError

try:
    import typer
except ImportError as e:  # pragma: no cover
    typer = None
    _TYPER_IMPORT_ERROR = e
else:
    _TYPER_IMPORT_ERROR = None


def build_app() -> Any:
    """Build and return the Typer application."""
    if typer is None:
        raise ImportError(
            "typer is required for CLI functionality. Install with: uv add '.[typer]'"
        ) from _TYPER_IMPORT_ERROR

    app = typer.Typer(help="FogBugz CLI")
    case_app = typer.Typer(help="Case commands")
    people_app = typer.Typer(help="People commands")
    projects_app = typer.Typer(help="Project commands")

    app.add_typer(case_app, name="case")
    app.add_typer(people_app, name="people")
    app.add_typer(projects_app, name="projects")

    @app.callback()
    def main_callback(
        ctx: typer.Context,
        config: str | None = typer.Option(None, "--config", help="Path to config TOML file"),
        base_url: str | None = typer.Option(None, "--base-url", help="FogBugz base URL"),
        token: str | None = typer.Option(None, "--token", help="API token"),
        username: str | None = typer.Option(None, "--username", help="Username"),
        password: str | None = typer.Option(None, "--password", help="Password"),
        timeout: int | None = typer.Option(None, "--timeout", help="HTTP timeout in seconds"),
        max_retries: int | None = typer.Option(
            None,
            "--max-retries",
            help="Maximum retry attempts",
        ),
        max_wait_seconds: int | None = typer.Option(
            None,
            "--max-wait-seconds",
            help="Maximum wait between retries",
        ),
    ) -> None:
        """Initialize shared CLI options."""
        ctx.obj = CLIOptions(
            config_path=config,
            base_url=base_url,
            token=token,
            username=username,
            password=password,
            timeout=timeout,
            max_retries=max_retries,
            max_wait_seconds=max_wait_seconds,
        )

    @app.command("search")
    def search(
        ctx: typer.Context,
        query: str = typer.Argument(..., help="FogBugz search query"),
        max_results: int | None = typer.Option(None, "--max", help="Maximum results"),
    ) -> None:
        """Search for cases by query string."""
        options = _ctx_options(ctx)
        _run_command(lambda: _render_search(options, query, max_results=max_results))

    @case_app.command("get")
    def case_get(
        ctx: typer.Context,
        case_id: int = typer.Argument(..., help="Case ID"),
    ) -> None:
        """Get a specific case by ID."""
        options = _ctx_options(ctx)
        _run_command(lambda: _render_case(options, case_id))

    @projects_app.command("list")
    def projects_list(ctx: typer.Context) -> None:
        """List all projects."""
        options = _ctx_options(ctx)
        _run_command(lambda: _render_projects(options))

    @people_app.command("search")
    def people_search(
        ctx: typer.Context,
        name: str = typer.Argument(..., help="Name to search"),
    ) -> None:
        """Search people by name."""
        options = _ctx_options(ctx)
        _run_command(lambda: _render_people_search(options, name))

    @people_app.command("get")
    def people_get(
        ctx: typer.Context,
        person_id: int = typer.Argument(..., help="Person ID"),
    ) -> None:
        """Get a person by ID."""
        options = _ctx_options(ctx)
        _run_command(lambda: _render_people_get(options, person_id))

    @app.command("whoami")
    def whoami(ctx: typer.Context) -> None:
        """Show currently authenticated user."""
        options = _ctx_options(ctx)
        _run_command(lambda: _render_whoami(options))

    return app


def _ctx_options(ctx: Any) -> CLIOptions:
    if isinstance(ctx.obj, CLIOptions):
        return ctx.obj
    return CLIOptions()


def _run_command(fn: Any) -> None:
    if typer is None:  # pragma: no cover
        raise RuntimeError("Typer is not available")

    try:
        fn()
    except FogBugzError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from e
    except (ValueError, RuntimeError) as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from e


def _render_search(options: CLIOptions, query: str, *, max_results: int | None) -> None:
    cases = search_command(options, query, max_results=max_results)
    rows = [
        {
            "ID": case.id,
            "Title": case.title,
            "Status": case.status,
            "Assigned": case.assigned_to,
            "Priority": case.priority,
            "Project": case.project,
        }
        for case in cases
    ]
    OutputFormatter.format_table(rows, title=f"Search Results ({len(cases)})")


def _render_case(options: CLIOptions, case_id: int) -> None:
    case = get_case_command(options, case_id)
    rows = [
        {
            "ID": case.id,
            "Title": case.title,
            "Status": case.status,
            "Assigned": case.assigned_to,
            "Priority": case.priority,
            "Project": case.project,
            "Area": case.area,
            "Category": case.category,
        }
    ]
    OutputFormatter.format_table(rows, title=f"Case {case.id}")


def _render_projects(options: CLIOptions) -> None:
    projects = list_projects_command(options)
    rows = [
        {
            "ID": project.id,
            "Name": project.name,
            "Status": project.status,
            "Description": project.description,
        }
        for project in projects
    ]
    OutputFormatter.format_table(rows, title=f"Projects ({len(projects)})")


def _render_people_search(options: CLIOptions, name: str) -> None:
    people = search_people_command(options, name)
    rows = [
        {
            "ID": person.id,
            "Name": person.name,
            "Email": person.email,
            "Phone": person.phone,
        }
        for person in people
    ]
    OutputFormatter.format_table(rows, title=f"People ({len(people)})")


def _render_people_get(options: CLIOptions, person_id: int) -> None:
    person = get_person_command(options, person_id)
    rows = [
        {
            "ID": person.id,
            "Name": person.name,
            "Email": person.email,
            "Phone": person.phone,
        }
    ]
    OutputFormatter.format_table(rows, title=f"Person {person.id}")


def _render_whoami(options: CLIOptions) -> None:
    user_data = whoami_command(options)
    OutputFormatter.format_table(
        [
            {
                "ID": user_data.get("id", ""),
                "Name": user_data.get("name", "unknown"),
                "Email": user_data.get("email", ""),
            }
        ],
        title="Current User",
    )


def main() -> None:
    """Main entry point for the fogbugz CLI.

    Raises:
        ImportError: If typer is not installed
    """
    app = build_app()
    app()


if __name__ == "__main__":
    main()
