"""Integration tests for the 'paths' CLI command."""

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

    def __init__(self, themes: list[str]) -> None:
        """Initialize test double.

        Args:
            themes: List of theme names to return
        """
        self.themes = themes

    def load(self, theme_name: str | None = None) -> dict[str, Any]:
        """Load a theme by name, or current theme if None."""
        return {"name": theme_name or self.themes[0] if self.themes else ""}

    def load_themes(self) -> dict[str, Any]:
        """Load all available themes."""
        return {theme: {"name": theme} for theme in self.themes}

    def list_themes(self) -> list[str]:
        """Return list of available themes."""
        return self.themes

    def get_current_theme(self) -> str:
        """Return name of current theme."""
        return self.themes[0] if self.themes else ""


def test_paths_command() -> None:
    """Test that the paths command returns the correct paths."""
    # Setup
    themes = ["Breeze", "Breeze Dark", "Oxygen"]
    theme_loader = ThemeLoaderDouble(themes)
    file_system = FileSystemDouble()
    xdg_double = XDGDouble()

    # Run command
    exit_code = run_cli(
        args=["paths"], file_system=cast(FileSystemInterface, file_system), xdg=xdg_double, theme_loader=theme_loader
    )

    # Verify results
    assert exit_code == ExitCode.SUCCESS

    # Check stdout output was captured
    assert file_system.stdout_capture
    stdout = file_system.stdout_capture

    # Verify it contains expected paths information
    assert "KDE Theme Search Paths:" in stdout
    assert "Config paths:" in stdout
    assert "Theme paths:" in stdout
    assert "Color scheme paths:" in stdout


def test_paths_command_with_json_output() -> None:
    """Test that the paths command with JSON output works correctly."""
    # Setup
    themes = ["Breeze", "Breeze Dark", "Oxygen"]
    theme_loader = ThemeLoaderDouble(themes)
    file_system = FileSystemDouble()
    xdg_double = XDGDouble()
    output_path = Path("/tmp/paths.json")

    # Run command
    exit_code = run_cli(
        args=["paths", "--format", "json", "--output", str(output_path)],
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
    assert "config_paths" in content
    assert "theme_paths" in content
    assert "color_scheme_paths" in content
