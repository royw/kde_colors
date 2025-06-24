"""XDG Base Directory interface module.

This module defines the XDGInterface protocol that establishes the contract for accessing
XDG Base Directory paths in the system. These paths are used to locate configuration files,
themes, and other resources following the XDG specification commonly used in Linux desktop
environments.

Why this interface exists:
- Abstracts XDG path resolution from the rest of the application
- Provides a consistent API for accessing standard paths on different systems
- Enables testing by allowing path resolution to be replaced with test doubles
- Centralizes knowledge of KDE-specific path conventions

Implementations of this interface are responsible for:
- Resolving user-specific configuration directories
- Finding system-wide configuration directories
- Locating KDE theme and color scheme directories
- Determining standard XDG data and config paths

The XDG Base Directory specification is essential for correctly interacting with KDE
configuration across different Linux distributions and user environments.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class XDGInterface(Protocol):
    """XDG Base Directory Specification injector."""

    def xdg_config_dirs(self) -> list[Path]:
        """Return a list of Paths corresponding to XDG_CONFIG_DIRS."""
        ...

    def xdg_config_home(self) -> Path:
        """Return a Path corresponding to XDG_CONFIG_HOME."""
        ...

    def xdg_data_dirs(self) -> list[Path]:
        """Return a list of Paths corresponding to XDG_DATA_DIRS."""
        ...

    def xdg_data_home(self) -> Path:
        """Return a Path corresponding to XDG_DATA_HOME."""
        ...
