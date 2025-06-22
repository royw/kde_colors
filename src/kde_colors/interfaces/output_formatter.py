"""
OutputFormatter interface for formatting theme data into different output formats.
"""

from __future__ import annotations

from typing import Any, Protocol


class OutputFormatterInterface(Protocol):
    """Format theme data into different output formats."""

    def format(self, theme_data: dict[str, Any]) -> str:
        """
        Format theme data into the desired output format.

        Args:
            theme_data: The theme data to format

        Returns:
            The formatted output as a string
        """
        ...
