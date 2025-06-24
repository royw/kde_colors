"""
Environment service implementation module.

This module provides the concrete implementation (StdEnvironment) of the EnvironmentInterface,
responsible for accessing and interacting with operating system environment variables.

Why this module exists:
- Abstracts direct environment variable access to improve testability
- Provides a consistent interface for environment operations
- Allows for dependency injection to replace real environment access with test doubles

The implementation handles:
- Retrieving environment variable values
- Providing fallback values for missing environment variables
- Getting the current user's home directory

This service is particularly important for the application to locate user-specific
KDE configuration directories that may vary based on environment settings.
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
