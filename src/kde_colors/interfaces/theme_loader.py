"""
ThemeLoader interface for loading and querying KDE themes.
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
