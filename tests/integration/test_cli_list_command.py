"""
Integration tests for the list command in the CLI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from kde_colors.cli.cli_runner import ExitCode, run_cli
from kde_colors.interfaces.file_system import FileSystemInterface
from kde_colors.interfaces.theme_loader import ThemeLoaderInterface
from tests.support.file_system_double import FileSystemDouble
from tests.support.xdg_double import XDGDouble


class ThemeLoaderDouble(ThemeLoaderInterface):
    """Test double for ThemeLoader."""

    def __init__(self, themes: list[str]) -> None:
        """Initialize with list of test themes.

        Args:
            themes: List of theme names to return
        """
        self.themes = themes

    def list_themes(self) -> list[str]:
        """Return the list of test themes."""
        return self.themes

    def load_themes(self) -> dict[str, Any]:
        """Return test themes in the format expected by CLIRunner."""
        result = {}
        for theme in self.themes:
            result[theme] = {
                "Name": theme,
                "Id": theme.lower().replace(" ", "-"),
                "Normalized Name": theme.lower().replace(" ", ""),
                "Path": f"/fake/path/{theme.lower().replace(' ', '-')}",
                "Colors": {"BackgroundNormal": "255,255,255"},
            }
        return result

    def get_theme_data(self, theme_name: str | None = None) -> dict[str, dict[str, str]]:
        """Return dummy theme data for the given theme."""
        if theme_name not in self.themes and theme_name is not None:
            return {}

        # Return a simple theme data structure
        return {
            "Colors:Button": {"BackgroundNormal": "255,255,255", "ForegroundNormal": "0,0,0"},
            "Colors:View": {"BackgroundNormal": "240,240,240", "ForegroundNormal": "10,10,10"},
        }

    def get_current_theme(self) -> str:
        """Return the name of the current theme."""
        return self.themes[0] if self.themes else ""

    def load(self, theme_name: str | None = None) -> dict[str, Any]:
        """Load a specific theme by name.

        Args:
            theme_name: Name of the theme to load, or None for current theme

        Returns:
            Theme data dictionary
        """
        # Use the first theme if no specific theme is requested
        actual_theme = theme_name if theme_name is not None else self.get_current_theme()

        # Find the theme in our test data
        themes_data = self.load_themes()
        if actual_theme in themes_data:
            # Apply cast to fix the [no-any-return] error
            return cast(dict[str, Any], themes_data[actual_theme])
        # Also use cast on the empty dict return
        return cast(dict[str, Any], {})


def test_list_command() -> None:
    """Test that the list command returns the correct list of themes."""
    # Setup
    themes = ["Breeze", "Breeze Dark", "Oxygen"]
    theme_loader = ThemeLoaderDouble(themes)
    file_system = FileSystemDouble()
    xdg_double = XDGDouble()

    # Run command
    exit_code = run_cli(
        args=["list"], file_system=cast(FileSystemInterface, file_system), xdg=xdg_double, theme_loader=theme_loader
    )

    # Verify results
    assert exit_code == ExitCode.SUCCESS
    assert file_system.stdout_capture  # Should have output

    # Check that each theme is in the output
    output = file_system.stdout_capture
    for theme in themes:
        assert theme in output


def test_list_command_with_json_output() -> None:
    """Test that the list command with JSON output works correctly."""
    # Setup
    themes = ["Breeze", "Breeze Dark", "Oxygen"]
    theme_loader = ThemeLoaderDouble(themes)
    file_system = FileSystemDouble()
    xdg_double = XDGDouble()

    # Create test output file
    output_path = Path("/tmp/themes.json")
    file_system.file_exists = lambda p: str(p) == str(output_path)  # type: ignore[assignment]

    # Run command
    exit_code = run_cli(
        args=["list", "--format", "json", "--output", str(output_path)],
        file_system=cast(FileSystemInterface, file_system),
        xdg=xdg_double,
        theme_loader=theme_loader,
    )

    # Verify results
    assert exit_code == ExitCode.SUCCESS

    # Check that file was written
    assert file_system.file_exists(str(output_path))

    # Check content
    content = file_system.read_text(output_path)
    assert '"themes"' in content
    for theme in themes:
        assert theme in content


def test_list_command_empty() -> None:
    """Test that the list command handles empty theme list correctly."""
    # Setup
    theme_loader = ThemeLoaderDouble([])
    file_system = FileSystemDouble()
    xdg_double = XDGDouble()

    # Run command
    exit_code = run_cli(
        args=["list"], file_system=cast(FileSystemInterface, file_system), xdg=xdg_double, theme_loader=theme_loader
    )

    # Verify results
    assert exit_code == ExitCode.SUCCESS
    assert "No themes found" in file_system.stdout_capture
