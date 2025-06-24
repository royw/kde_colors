"""
ThemeLoader interface module.

This module defines the ThemeLoaderInterface protocol that establishes the contract
for loading and querying KDE Plasma themes. It serves as the boundary between the CLI
commands and the underlying theme implementation details.

Why this interface exists:
- Enforces a consistent API for accessing theme data
- Allows alternative implementations for testing or different backends
- Decouples theme discovery/loading logic from CLI command handlers

Implementations of this interface are responsible for:
- Finding all available KDE themes in the system
- Retrieving the currently active theme
- Loading detailed theme information (colors, metadata)
- Parsing theme files and color values

CLI commands interact only with this interface, not directly with any specific implementation,
following the dependency inversion principle of clean architecture.
"""

from __future__ import annotations

from typing import Any, Protocol


class ThemeLoaderInterface(Protocol):
    """Load and query KDE themes using XDG and FileSystem Interfaces."""

    def load(self, theme_name: str) -> Any | None:
        """
        Load a theme from the given theme name.

        Args:
            theme_name: Name of the theme to load

        Returns:
            Theme data dictionary or None if not found
        """
        ...

    def load_themes(self) -> dict[str, Any]:
        """
        Load all available themes.

        Returns:
            A dictionary of theme information with structure:
            {
                "Theme Name": {
                    "Name": "Theme Name",
                    "Id": "theme-name",
                    "Normalized Name": "themename",
                    "Package": "org.kde.themename.desktop",
                    "Path": "/path/to/theme",
                    "Colors": { ... }
                },
                ...
            }
        """
        ...

    def get_current_theme(self) -> str | None:
        """
        Get the current theme name.

        Returns:
            Current theme name or None if not found
        """
        ...
