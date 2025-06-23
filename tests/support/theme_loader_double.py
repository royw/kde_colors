"""
Test double for ThemeLoaderInterface.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from kde_colors.interfaces.theme_loader import ThemeLoaderInterface


class ThemeLoaderDouble(ThemeLoaderInterface):
    """Test double for ThemeLoaderInterface."""

    def __init__(self, themes: dict[str, dict[str, Any]] | None = None, current_theme: str | None = None) -> None:
        """
        Initialize the double with pre-configured themes.

        Args:
            themes: Dictionary of theme name to theme data
            current_theme: Name of the current theme
        """
        self.themes = themes or {}
        self.current_theme = current_theme
        self._paths_called = False

    def get_paths(self) -> dict[str, Sequence[str]]:
        """
        Get paths where themes are located.

        Returns:
            Dict with 'theme_dirs' and 'config_file' keys
        """
        self._paths_called = True
        return {
            "theme_dirs": ["/usr/share/color-schemes", "/home/user/.local/share/color-schemes"],
            "config_file": "/home/user/.config/plasmarc",
        }

    def get_available_themes(self) -> dict[str, dict[str, Any]]:
        """
        Get all available themes.

        Returns:
            Dictionary with theme names as keys and theme info as values
        """
        return self.themes

    def load_themes(self) -> dict[str, dict[str, Any]]:
        """
        Load all available themes.

        Returns:
            Dictionary with theme names as keys and theme info as values
        """
        return self.themes

    def get_current_theme(self) -> str | None:
        """
        Get the name of the current theme.

        Returns:
            Name of the current theme or None if not set
        """
        return self.current_theme

    def load(self, theme_name: str | None = None) -> dict[str, Any] | None:
        """
        Load a theme by name.

        Args:
            theme_name: Name of the theme to load (or current theme if None)

        Returns:
            Theme data or None if not found
        """
        if theme_name is None:
            theme_name = self.current_theme
            if theme_name is None:
                return None

        return self.themes.get(theme_name)
