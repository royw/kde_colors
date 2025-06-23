"""
Test double for OutputFormatterInterface.
"""

from __future__ import annotations

from typing import Any

from kde_colors.interfaces.output_formatter import OutputFormatterInterface


class OutputFormatterDouble(OutputFormatterInterface):
    """Test double for OutputFormatterInterface."""

    def __init__(self, fixed_output: str | None = None) -> None:
        """
        Initialize the double.

        Args:
            fixed_output: If provided, this string will always be returned by format()
        """
        self.fixed_output = fixed_output
        self.last_data: dict[str, Any] | None = None

    def format(self, data: dict[str, Any]) -> str:
        """
        Format the data with the specified format.

        Args:
            data: Data to format

        Returns:
            Formatted string
        """
        self.last_data = data
        if self.fixed_output is not None:
            return self.fixed_output
        return str(data)
