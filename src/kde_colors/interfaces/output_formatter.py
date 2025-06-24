"""
Output formatter interface module.

This module defines the OutputFormatterInterface protocol that establishes the contract
for formatting data into different presentation formats (e.g., text, JSON). It serves as
the boundary between the CLI command handlers and the specific output formatting implementations.

Why this interface exists:
- Separates data processing logic from presentation concerns
- Allows multiple output format implementations (text, JSON) with a consistent API
- Enables command handlers to remain agnostic about output formatting details
- Supports the Single Responsibility Principle by isolating formatting logic

Implementations of this interface are responsible for:
- Converting internal data structures into user-friendly output formats
- Handling specific formatting requirements for different commands (list, theme, paths)
- Managing output styles based on user preferences (e.g., human-readable vs. machine-readable)

The interface is deliberately minimal with a single method to keep implementations focused
and maintain a clean separation of concerns within the application architecture.
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
