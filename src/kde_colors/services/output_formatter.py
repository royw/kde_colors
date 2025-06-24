"""Output formatter service implementations module.

This module provides concrete implementations of the OutputFormatterInterface for different
output formats (text and JSON) and CLI commands. It's responsible for formatting data from
the application's internal representation into user-friendly output formats.

The module contains formatter classes for each command (list, path, theme) and output format
combination. This separation allows for specialized formatting logic tailored to each
command's unique data structure while maintaining a consistent interface.

It also provides a factory function that selects the appropriate formatter based on
command name and desired output format, decoupling the CLI runner from formatter implementation
details.
"""

from __future__ import annotations

import json
from typing import Any

from kde_colors.interfaces.output_formatter import OutputFormatterInterface


class ListTextOutputFormatter(OutputFormatterInterface):
    """Text formatter for the list command output."""

    def __str__(self) -> str:
        return "Text formatter for the list command output"

    def format(self, data: dict[str, Any]) -> str:
        """Format themes list data into human-readable text format.

        Example:
            Available desktop themes (current theme marked with *):
              oxygen
            * breeze-dark
              kubuntu
              default
              breeze-light

        Args:
            data: Dictionary containing themes data with 'themes' key

        Returns:
            Formatted text string
        """
        if not data or "themes" not in data:
            return "No themes found."

        themes = data["themes"]
        if not themes:
            return "No themes found."

        result = ["Available desktop themes (current theme marked with *):"]

        # Sort themes by name for consistent output
        sorted_themes = sorted(themes.keys())
        current_theme = data.get("current_theme", "")

        for theme_name in sorted_themes:
            # Check for current theme in two ways:
            # 1. theme_name matches current_theme at the root level
            # 2. theme has a current=True property
            if (theme_name == current_theme) or (themes[theme_name].get("current", False)):
                result.append(f"  * {theme_name}")
            else:
                result.append(f"  {theme_name}")

        return "\n".join(result)


class ListJsonOutputFormatter(OutputFormatterInterface):
    """JSON formatter for the list command output."""

    def __str__(self) -> str:
        return "JSON formatter for the list command output"

    def format(self, data: dict[str, Any]) -> str:
        """Format themes list data into JSON format.

        Example:

        {
            "current": "oxygen",
            "themes": [
                "oxygen",
                "breeze-dark",
                "breeze-light",
                "kubuntu",
                "default"
            ]
        }

        Args:
            data: Dictionary containing themes data with 'themes' key

        Returns:
            JSON formatted string
        """
        # Extract themes from the data
        themes_dict = data.get("themes", {})

        # Find the current theme
        current_theme = None
        theme_names = []

        for theme_name, theme_info in themes_dict.items():
            theme_names.append(theme_name)
            if theme_info.get("current", False):
                current_theme = theme_name

        # Build the result dictionary
        result = {"current": current_theme, "themes": sorted(theme_names)}

        return json.dumps(result, indent=2)


class ThemeTextOutputFormatter(OutputFormatterInterface):
    """Text formatter for the theme command output."""

    def __str__(self) -> str:
        return "Text formatter for the theme command output"

    def format(self, data: dict[str, Any]) -> str:
        """Format theme data into human-readable text format.

        Example:
            Name: Breeze (Breeze)
            Id: breeze
            Package: org.kde.breeze.desktop
            Path: /usr/share/plasma/desktoptheme/Breeze

            Colors:
            [Colors:View]
        Args:
            data: Theme data dictionary

        Returns:
            Formatted text representation of theme data
        """
        if "error" in data:
            return f"Error: {data['error']}"

        if not data or "theme" not in data:
            return "No theme data found."

        theme = data["theme"]
        result = []

        # Format theme header
        result.extend(self._format_theme_header(theme))

        # Format color sections if present
        if "Colors" in theme:
            result.extend(self._format_color_sections(theme["Colors"]))

        return "\n".join(result)

    def _format_theme_header(self, theme: dict[str, Any]) -> list[str]:
        """Format basic theme information.

        Args:
            theme: Theme data dictionary

        Returns:
            List of formatted lines with theme header information
        """
        return [
            f"Name: {theme.get('Name', 'Unknown')}",
            f"Id: {theme.get('Id', 'Unknown')}",
            f"Package: {theme.get('Package', 'Unknown')}",
            f"Path: {theme.get('Path', 'Unknown')}",
        ]

    def _format_color_sections(self, colors: dict[str, Any]) -> list[str]:
        """Format all color sections.

        Args:
            colors: Dictionary of color sections

        Returns:
            List of formatted lines for all color sections
        """
        result = ["\nColors:"]

        # Sort the color sections for consistent output
        color_sections = sorted(colors.keys())

        for section in color_sections:
            result.append(f"[{section}]")

            if isinstance(colors[section], dict):
                result.extend(self._format_color_entries(colors[section]))
                # Add blank line after each section
                result.append("")

        return result

    def _format_color_entries(self, section_colors: dict[str, Any]) -> list[str]:
        """Format individual color entries within a section.

        Args:
            section_colors: Dictionary of color entries for a section

        Returns:
            List of formatted lines for color entries
        """
        result = []

        # Sort color entries for consistent output
        color_entries = sorted(section_colors.keys())

        for color_key in color_entries:
            color_value = section_colors[color_key]
            result.append(self._format_color_entry(color_key, color_value))

        return result

    def _format_color_entry(self, key: str, value: Any) -> str:
        """Format a single color entry.

        Args:
            key: Color name/key
            value: Color value (either RGB list or string)

        Returns:
            Formatted color entry line
        """
        # Format RGB values as hex if they're lists of integers
        if isinstance(value, list) and len(value) == 3:
            r, g, b = value
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            return f"    {key}: {hex_color} (RGB: {r},{g},{b})"

        return f"    {key}: {value}"


class ThemeJsonOutputFormatter(OutputFormatterInterface):
    """JSON formatter for the theme command output."""

    def __str__(self) -> str:
        return "JSON formatter for the theme command output"

    def format(self, data: dict[str, Any]) -> str:
        """Format theme data into JSON format.

        Args:
            data: Dictionary containing theme data

        Returns:
            JSON formatted string
        """
        return json.dumps(data, indent=2)


class PathsTextOutputFormatter(OutputFormatterInterface):
    """Text formatter for the paths command output."""

    def __str__(self) -> str:
        return "Text formatter for the paths command output"

    def format(self, data: dict[str, Any]) -> str:
        """Format paths data into human-readable text format.

        Example:
            KDE Theme Search Paths:
            - Config paths:
              - /home/username/.config
              - /etc/xdg

            - Theme paths:
              - /home/username/.local/share/plasma/desktoptheme
              - /usr/share/plasma/desktoptheme

            - Color scheme paths:
              - /home/username/.local/share/color-schemes
              - /usr/share/color-schemes

        Args:
            data: Dictionary containing paths data

        Returns:
            Formatted text string
        """
        if not data:
            return "No path information available."

        result = ["KDE Theme Search Paths:"]

        # Format config paths
        config_paths = data.get("config_paths", [])
        if config_paths:
            result.append("- Config paths:")
            for path in config_paths:
                result.append(f"  - {path}")
            result.append("")

        # Format theme paths
        theme_paths = data.get("theme_paths", [])
        if theme_paths:
            result.append("- Theme paths:")
            for path in theme_paths:
                result.append(f"  - {path}")
            result.append("")

        # Format color scheme paths
        color_scheme_paths = data.get("color_scheme_paths", [])
        if color_scheme_paths:
            result.append("- Color scheme paths:")
            for path in color_scheme_paths:
                result.append(f"  - {path}")

        return "\n".join(result)


class PathsJsonOutputFormatter(OutputFormatterInterface):
    """JSON formatter for the paths command output."""

    def __str__(self) -> str:
        return "JSON formatter for the paths command output"

    def format(self, data: dict[str, Any]) -> str:
        """Format paths data into JSON format.

        Args:
            data: Dictionary containing paths data

        Returns:
            JSON formatted string
        """
        return json.dumps(data, indent=2)


def get_output_formatter(format: str, command: str) -> OutputFormatterInterface:
    """Get the output formatter for the given format."""
    formatters: dict[str, dict[str, OutputFormatterInterface]] = {
        "list": {"text": ListTextOutputFormatter(), "json": ListJsonOutputFormatter()},
        "theme": {"text": ThemeTextOutputFormatter(), "json": ThemeJsonOutputFormatter()},
        "paths": {"text": PathsTextOutputFormatter(), "json": PathsJsonOutputFormatter()},
    }
    if command not in formatters:
        msg = f"Unknown command: {command}"
        raise ValueError(msg)

    if format not in formatters[command]:
        msg = f"Unknown format: {format}"
        raise ValueError(msg)

    return formatters[command][format]
