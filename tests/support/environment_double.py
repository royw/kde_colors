"""
Test double for EnvironmentInterface.
"""

from __future__ import annotations

from kde_colors.interfaces.environment import EnvironmentInterface


class EnvironmentDouble(EnvironmentInterface):
    """Test double for EnvironmentInterface."""

    def __init__(self, variables: dict[str, str]) -> None:
        """
        Initialize the double with environment variables.

        Args:
            variables: Dictionary of environment variables
        """
        self.variables = variables

    def getenv(self, name: str) -> str | None:
        """
        Get environment variable.

        Args:
            name: Name of the environment variable

        Returns:
            Value of the environment variable or None if not found
        """
        return self.variables.get(name)
