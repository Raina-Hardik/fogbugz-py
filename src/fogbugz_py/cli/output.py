"""CLI output formatting and rendering."""

from __future__ import annotations


class OutputFormatter:
    """Format CLI output using rich for pretty printing."""

    @staticmethod
    def format_table(data: list[dict[str, str]], *, title: str | None = None) -> None:
        """Format data as a table.

        Args:
            data: List of dictionaries to display
            title: Optional table title
        """
        raise NotImplementedError("Output formatter implementation pending")
