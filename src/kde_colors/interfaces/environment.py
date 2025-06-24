"""Environment interface module.

This module defines the EnvironmentInterface protocol that establishes the contract
for accessing operating system environment variables. It serves as an abstraction layer
between the application and the actual environment access mechanisms.

Why this interface exists:
- Decouples the application from direct OS environment variable access
- Enables unit testing by allowing test doubles to replace real environment access
- Provides a consistent API for environment operations across the application

Implementations of this interface are responsible for:
- Retrieving environment variable values from the operating system
- Providing fallback values for missing variables
- Handling environment-specific paths like the user's home directory

This interface is particularly important for the application to locate user-specific
configuration directories that may vary based on system environment settings.
"""

from __future__ import annotations

from typing import Protocol


class EnvironmentInterface(Protocol):
    """Environment interface for accessing environment variables."""

    def getenv(self, name: str) -> str | None:
        """Get the value of an environment variable."""
        ...
