"""
Unit tests for the OutputFormatter service.
"""

from __future__ import annotations

import json
from typing import cast

import pytest

from kde_colors.interfaces.output_formatter import OutputFormatterInterface
from kde_colors.services.output_formatter import (
    ListJsonOutputFormatter,
    ListTextOutputFormatter,
    PathsJsonOutputFormatter,
    PathsTextOutputFormatter,
    ThemeJsonOutputFormatter,
    ThemeTextOutputFormatter,
    get_output_formatter,
)


class TestListTextOutputFormatter:
    """Tests for the ListTextOutputFormatter class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.formatter = ListTextOutputFormatter()

    def test_implements_interface(self) -> None:
        """Test that ListTextOutputFormatter implements the OutputFormatterInterface."""
        cast(OutputFormatterInterface, self.formatter)
        assert True  # If we got here, the cast succeeded

    def test_format_empty_data(self) -> None:
        """Test formatting with empty data."""
        result = self.formatter.format({})
        assert result == "No themes found."

    def test_format_no_themes_key(self) -> None:
        """Test formatting with data missing the 'themes' key."""
        result = self.formatter.format({"other_data": "value"})
        assert result == "No themes found."

    def test_format_empty_themes(self) -> None:
        """Test formatting with empty themes dictionary."""
        result = self.formatter.format({"themes": {}})
        assert result == "No themes found."

    def test_format_with_themes(self) -> None:
        """Test formatting with actual themes data."""
        themes_data = {
            "themes": {
                "breeze": {"current": False},
                "breeze-dark": {"current": True},
                "oxygen": {"current": False},
            }
        }

        expected = "Available desktop themes (current theme marked with *):\n  breeze\n  * breeze-dark\n  oxygen"

        result = self.formatter.format(themes_data)
        assert result == expected


class TestListJsonOutputFormatter:
    """Tests for the ListJsonOutputFormatter class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.formatter = ListJsonOutputFormatter()

    def test_implements_interface(self) -> None:
        """Test that ListJsonOutputFormatter implements the OutputFormatterInterface."""
        cast(OutputFormatterInterface, self.formatter)
        assert True  # If we got here, the cast succeeded

    def test_format_empty_data(self) -> None:
        """Test formatting with empty data."""
        result = self.formatter.format({})
        parsed = json.loads(result)
        assert parsed == {"current": None, "themes": []}

    def test_format_no_themes(self) -> None:
        """Test formatting with data missing the 'themes' key."""
        result = self.formatter.format({"other_data": "value"})
        parsed = json.loads(result)
        assert parsed == {"current": None, "themes": []}

    def test_format_with_themes(self) -> None:
        """Test formatting with actual themes data."""
        themes_data = {
            "themes": {
                "breeze": {"current": False},
                "breeze-dark": {"current": True},
                "oxygen": {"current": False},
            }
        }

        result = self.formatter.format(themes_data)
        parsed = json.loads(result)

        assert parsed == {
            "current": "breeze-dark",
            "themes": ["breeze", "breeze-dark", "oxygen"],
        }

    def test_format_no_current_theme(self) -> None:
        """Test formatting when no theme is marked as current."""
        themes_data = {
            "themes": {
                "breeze": {"current": False},
                "oxygen": {"current": False},
            }
        }

        result = self.formatter.format(themes_data)
        parsed = json.loads(result)

        assert parsed == {
            "current": None,
            "themes": ["breeze", "oxygen"],
        }


class TestThemeTextOutputFormatter:
    """Tests for the ThemeTextOutputFormatter class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.formatter = ThemeTextOutputFormatter()

    def test_implements_interface(self) -> None:
        """Test that ThemeTextOutputFormatter implements the OutputFormatterInterface."""
        cast(OutputFormatterInterface, self.formatter)
        assert True  # If we got here, the cast succeeded

    def test_format_error(self) -> None:
        """Test formatting when there's an error message."""
        result = self.formatter.format({"error": "Theme not found"})
        assert result == "Error: Theme not found"

    def test_format_empty_data(self) -> None:
        """Test formatting with empty data."""
        result = self.formatter.format({})
        assert result == "No theme data found."

    def test_format_no_theme_key(self) -> None:
        """Test formatting with data missing the 'theme' key."""
        result = self.formatter.format({"other_data": "value"})
        assert result == "No theme data found."

    def test_format_basic_theme_info(self) -> None:
        """Test formatting with basic theme info."""
        theme_data = {
            "theme": {
                "Name": "Breeze",
                "Id": "breeze",
                "Package": "org.kde.breeze.desktop",
                "Path": "/usr/share/plasma/desktoptheme/Breeze",
            }
        }

        expected = (
            "Name: Breeze\nId: breeze\nPackage: org.kde.breeze.desktop\nPath: /usr/share/plasma/desktoptheme/Breeze"
        )

        result = self.formatter.format(theme_data)
        assert result == expected

    def test_format_missing_theme_fields(self) -> None:
        """Test formatting with missing theme fields."""
        theme_data = {"theme": {"Name": "Breeze"}}

        expected = "Name: Breeze\nId: Unknown\nPackage: Unknown\nPath: Unknown"

        result = self.formatter.format(theme_data)
        assert result == expected

    def test_format_with_colors(self) -> None:
        """Test formatting with color information."""
        theme_data = {
            "theme": {
                "Name": "Breeze",
                "Id": "breeze",
                "Colors": {
                    "Colors:View": {
                        "BackgroundNormal": "#fcfcfc",
                        "ForegroundNormal": "#232629",
                    },
                    "Colors:Window": {"BackgroundNormal": "#eff0f1"},
                },
            }
        }

        expected = (
            "Name: Breeze\n"
            "Id: breeze\n"
            "Package: Unknown\n"
            "Path: Unknown\n\n"
            "Colors:\n"
            "[Colors:View]\n"
            "    BackgroundNormal: #fcfcfc\n"
            "    ForegroundNormal: #232629\n\n"
            "[Colors:Window]\n"
            "    BackgroundNormal: #eff0f1\n"
        )

        result = self.formatter.format(theme_data)
        assert result == expected

    def test_format_with_rgb_colors(self) -> None:
        """Test formatting with RGB color values."""
        theme_data = {
            "theme": {
                "Name": "Breeze",
                "Id": "breeze",
                "Colors": {
                    "Colors:View": {
                        "BackgroundNormal": [252, 252, 252],  # RGB values
                        "ForegroundNormal": "#232629",  # Hex value
                    },
                },
            }
        }

        expected = (
            "Name: Breeze\n"
            "Id: breeze\n"
            "Package: Unknown\n"
            "Path: Unknown\n\n"
            "Colors:\n"
            "[Colors:View]\n"
            "    BackgroundNormal: #fcfcfc (RGB: 252,252,252)\n"
            "    ForegroundNormal: #232629\n"
        )

        result = self.formatter.format(theme_data)
        assert result == expected


class TestThemeJsonOutputFormatter:
    """Tests for the ThemeJsonOutputFormatter class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.formatter = ThemeJsonOutputFormatter()

    def test_implements_interface(self) -> None:
        """Test that ThemeJsonOutputFormatter implements the OutputFormatterInterface."""
        cast(OutputFormatterInterface, self.formatter)
        assert True  # If we got here, the cast succeeded

    def test_format_empty_data(self) -> None:
        """Test formatting with empty data."""
        result = self.formatter.format({})
        parsed = json.loads(result)
        assert parsed == {}

    def test_format_theme_data(self) -> None:
        """Test formatting with theme data."""
        theme_data = {
            "theme": {
                "Name": "Breeze",
                "Id": "breeze",
                "Colors": {
                    "Colors:View": {"BackgroundNormal": "#fcfcfc"},
                },
            }
        }

        result = self.formatter.format(theme_data)
        parsed = json.loads(result)
        assert parsed == theme_data


class TestPathsTextOutputFormatter:
    """Tests for the PathsTextOutputFormatter class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.formatter = PathsTextOutputFormatter()

    def test_implements_interface(self) -> None:
        """Test that PathsTextOutputFormatter implements the OutputFormatterInterface."""
        cast(OutputFormatterInterface, self.formatter)
        assert True  # If we got here, the cast succeeded

    def test_format_empty_data(self) -> None:
        """Test formatting with empty data."""
        result = self.formatter.format({})
        assert result == "No path information available."

    def test_format_with_paths(self) -> None:
        """Test formatting with path data."""
        paths_data = {
            "config_paths": ["/home/user/.config", "/etc/xdg"],
            "theme_paths": ["/home/user/.local/share/plasma/desktoptheme"],
            "color_scheme_paths": ["/home/user/.local/share/color-schemes"],
        }

        expected = (
            "KDE Theme Search Paths:\n"
            "- Config paths:\n"
            "  - /home/user/.config\n"
            "  - /etc/xdg\n\n"
            "- Theme paths:\n"
            "  - /home/user/.local/share/plasma/desktoptheme\n\n"
            "- Color scheme paths:\n"
            "  - /home/user/.local/share/color-schemes"
        )

        result = self.formatter.format(paths_data)
        assert result == expected

    def test_format_with_missing_paths(self) -> None:
        """Test formatting with some missing path types."""
        paths_data = {
            "config_paths": ["/home/user/.config"],
            # No theme_paths
            "color_scheme_paths": ["/home/user/.local/share/color-schemes"],
        }

        expected = (
            "KDE Theme Search Paths:\n"
            "- Config paths:\n"
            "  - /home/user/.config\n\n"
            "- Color scheme paths:\n"
            "  - /home/user/.local/share/color-schemes"
        )

        result = self.formatter.format(paths_data)
        assert result == expected


class TestPathsJsonOutputFormatter:
    """Tests for the PathsJsonOutputFormatter class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.formatter = PathsJsonOutputFormatter()

    def test_implements_interface(self) -> None:
        """Test that PathsJsonOutputFormatter implements the OutputFormatterInterface."""
        cast(OutputFormatterInterface, self.formatter)
        assert True  # If we got here, the cast succeeded

    def test_format_empty_data(self) -> None:
        """Test formatting with empty data."""
        result = self.formatter.format({})
        parsed = json.loads(result)
        assert parsed == {}

    def test_format_with_paths(self) -> None:
        """Test formatting with path data."""
        paths_data = {
            "config_paths": ["/home/user/.config", "/etc/xdg"],
            "theme_paths": ["/home/user/.local/share/plasma/desktoptheme"],
            "color_scheme_paths": ["/home/user/.local/share/color-schemes"],
        }

        result = self.formatter.format(paths_data)
        parsed = json.loads(result)
        assert parsed == paths_data


class TestGetOutputFormatter:
    """Tests for the get_output_formatter function."""

    def test_get_list_text_formatter(self) -> None:
        """Test getting a list text formatter."""
        formatter = get_output_formatter("text", "list")
        assert isinstance(formatter, ListTextOutputFormatter)

    def test_get_list_json_formatter(self) -> None:
        """Test getting a list json formatter."""
        formatter = get_output_formatter("json", "list")
        assert isinstance(formatter, ListJsonOutputFormatter)

    def test_get_theme_text_formatter(self) -> None:
        """Test getting a theme text formatter."""
        formatter = get_output_formatter("text", "theme")
        assert isinstance(formatter, ThemeTextOutputFormatter)

    def test_get_theme_json_formatter(self) -> None:
        """Test getting a theme json formatter."""
        formatter = get_output_formatter("json", "theme")
        assert isinstance(formatter, ThemeJsonOutputFormatter)

    def test_get_paths_text_formatter(self) -> None:
        """Test getting a paths text formatter."""
        formatter = get_output_formatter("text", "paths")
        assert isinstance(formatter, PathsTextOutputFormatter)

    def test_get_paths_json_formatter(self) -> None:
        """Test getting a paths json formatter."""
        formatter = get_output_formatter("json", "paths")
        assert isinstance(formatter, PathsJsonOutputFormatter)

    def test_unknown_command(self) -> None:
        """Test error is raised for an unknown command."""
        with pytest.raises(ValueError, match="Unknown command: unknown"):
            get_output_formatter("text", "unknown")

    def test_unknown_format(self) -> None:
        """Test error is raised for an unknown format."""
        with pytest.raises(ValueError, match="Unknown format: yaml"):
            get_output_formatter("yaml", "list")
