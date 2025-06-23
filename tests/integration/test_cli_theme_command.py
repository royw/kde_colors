"""Integration tests for the 'theme' CLI command."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from kde_colors.cli.cli_runner import ExitCode, run_cli
from kde_colors.interfaces.file_system import FileSystemInterface
from kde_colors.interfaces.theme_loader import ThemeLoaderInterface
from tests.support.file_system_double import FileSystemDouble
from tests.support.xdg_double import XDGDouble


class ThemeLoaderDouble(ThemeLoaderInterface):
    """Test double for ThemeLoaderInterface."""

    def __init__(self, themes: list[str], current_theme: str = "") -> None:
        """Initialize test double.

        Args:
            themes: List of theme names to return
            current_theme: Name of the current theme
        """
        self.themes = themes
        self.current = current_theme or (themes[0] if themes else "")

    def load(self, theme_name: str | None = None) -> dict[str, Any]:
        """Load a theme by name, or current theme if None."""
        name = theme_name or self.current
        if not name or name not in self.themes:
            return {}

        # Return a mock theme structure with capitalized keys expected by ThemeTextOutputFormatter
        return {
            "Name": name,
            "Id": name.lower().replace(" ", "-"),
            "Package": f"org.kde.{name.lower().replace(' ', '')}",
            "Path": f"/path/to/{name.lower().replace(' ', '-')}",
            "Colors": {
                "Window": {"Background": [255, 255, 255], "Foreground": [0, 0, 0]},
                "Button": {"Background": [238, 238, 238], "Foreground": [51, 51, 51]},
            },
        }

    def load_themes(self) -> dict[str, Any]:
        """Load all available themes."""
        return {theme: self.load(theme) for theme in self.themes}

    def get_current_theme(self) -> str:
        """Return name of current theme."""
        return self.current


def test_theme_command() -> None:
    """Test that the theme command returns the correct theme information."""
    # Setup
    themes = ["Breeze", "Breeze Dark", "Oxygen"]
    current_theme = "Breeze"
    theme_loader = ThemeLoaderDouble(themes, current_theme)
    file_system = FileSystemDouble()
    xdg_double = XDGDouble()

    # Run command - should use current theme when no name is provided
    exit_code = run_cli(
        args=["theme"], file_system=cast(FileSystemInterface, file_system), xdg=xdg_double, theme_loader=theme_loader
    )

    # Verify results
    assert exit_code == ExitCode.SUCCESS

    # Check stdout output was captured
    assert file_system.stdout_capture
    stdout = file_system.stdout_capture

    # Verify it contains expected theme information
    assert "Name: Breeze" in stdout
    assert "Id: breeze" in stdout
    assert "Package:" in stdout
    assert "Background:" in stdout
    assert "#ffffff" in stdout


def test_theme_command_with_name() -> None:
    """Test that the theme command with a specified name works correctly."""
    # Setup
    themes = ["Breeze", "Breeze Dark", "Oxygen"]
    theme_loader = ThemeLoaderDouble(themes)
    file_system = FileSystemDouble()
    xdg_double = XDGDouble()

    # Run command with explicit theme name
    exit_code = run_cli(
        args=["theme", "Oxygen"],
        file_system=cast(FileSystemInterface, file_system),
        xdg=xdg_double,
        theme_loader=theme_loader,
    )

    # Verify results
    assert exit_code == ExitCode.SUCCESS

    # Check stdout output was captured
    assert file_system.stdout_capture
    stdout = file_system.stdout_capture

    # Verify it contains expected theme information for Oxygen
    assert "Name: Oxygen" in stdout
    assert "Id: oxygen" in stdout


def test_theme_command_with_json_output() -> None:
    """Test that the theme command with JSON output works correctly."""
    # Setup
    themes = ["Breeze", "Breeze Dark", "Oxygen"]
    theme_loader = ThemeLoaderDouble(themes)
    file_system = FileSystemDouble()
    xdg_double = XDGDouble()
    output_path = Path("/tmp/theme.json")

    # Run command
    exit_code = run_cli(
        args=["theme", "Breeze", "--json", "--output", str(output_path)],
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
    assert "theme" in content
    assert "Name" in content
    assert "Breeze" in content
    assert "Colors" in content


def test_theme_command_not_found() -> None:
    """Test that the theme command handles non-existent themes correctly."""
    # Setup
    themes = ["Breeze", "Breeze Dark", "Oxygen"]
    theme_loader = ThemeLoaderDouble(themes)
    file_system = FileSystemDouble()
    xdg_double = XDGDouble()

    # Run command with non-existent theme name
    exit_code = run_cli(
        args=["theme", "NonExistentTheme"],
        file_system=cast(FileSystemInterface, file_system),
        xdg=xdg_double,
        theme_loader=theme_loader,
    )

    # Error code should be THEME_NOT_FOUND
    assert exit_code == ExitCode.THEME_NOT_FOUND

    # No need to check stdout since the error is logged directly and not
    # captured in our test double's stdout
