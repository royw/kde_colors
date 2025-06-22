from __future__ import annotations

from typing import Protocol


class EnvironmentInterface(Protocol):
    """Environment interface for accessing environment variables."""

    def getenv(self, name: str) -> str | None:
        """Get the value of an environment variable."""
        ...
