"""Main CLI application using Typer.

Only available when fogbugz-py[typer] is installed.
"""

from __future__ import annotations


def main() -> None:
    """Main entry point for the fogbugz CLI.

    Raises:
        ImportError: If typer is not installed
    """
    try:
        import typer  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "typer is required for CLI functionality. Install with: pip install fogbugz-py[typer]"
        ) from e

    # Implementation pending
    raise NotImplementedError("CLI implementation pending")


if __name__ == "__main__":
    main()
