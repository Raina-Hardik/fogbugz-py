"""CLI output formatting and rendering."""

from __future__ import annotations

from typing import Any


class OutputFormatter:
    """Format CLI output using rich for pretty printing."""

    @staticmethod
    def format_table(data: list[dict[str, Any]], *, title: str | None = None) -> None:
        """Format data as a table.

        Args:
            data: List of dictionaries to display
            title: Optional table title
        """
        if not data:
            print("No results found.")
            return

        columns = list(data[0].keys())

        try:
            from rich.console import Console
            from rich.table import Table

            table = Table(title=title)
            for column in columns:
                table.add_column(column)

            for row in data:
                table.add_row(
                    *[OutputFormatter._stringify(row.get(column, "")) for column in columns]
                )

            Console().print(table)
            return
        except ImportError:
            pass

        if title:
            print(title)

        print(" | ".join(columns))
        print("-+-".join("-" * len(column) for column in columns))
        for row in data:
            print(" | ".join(OutputFormatter._stringify(row.get(column, "")) for column in columns))

    @staticmethod
    def _stringify(value: Any) -> str:
        if value is None:
            return ""
        return str(value)
