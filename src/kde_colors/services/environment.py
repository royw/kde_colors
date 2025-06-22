"""
EnvironmentService for handling environment variables and system environment.
"""

from __future__ import annotations

import os

from kde_colors.interfaces.environment import EnvironmentInterface


class StdEnvironment(EnvironmentInterface):
    """Abstract environment detection injector that encapsulates environment variables."""

    def getenv(self, name: str, default: str | None = None) -> str | None:
        """
        Retrieve the value of the environment variable.

        Args:
            name: The name of the environment variable
            default: A default value if the variable doesn't exist

        Returns:
            The value of the environment variable or the default
        """
        return os.environ.get(name, default)
