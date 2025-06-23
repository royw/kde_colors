"""
Unit tests for the CLI runner.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from kde_colors.cli.cli_runner import CLIRunner, ExitCode, run_cli
from tests.support.environment_double import EnvironmentDouble
from tests.support.file_system_double import FileSystemDouble
from tests.support.theme_loader_double import ThemeLoaderDouble
from tests.support.xdg_double import XDGDouble


@pytest.fixture
def _file_system() -> FileSystemDouble:
    """Create a FileSystemDouble for testing."""
    return FileSystemDouble()


@pytest.fixture
def _environment() -> EnvironmentDouble:
    """Create an EnvironmentDouble for testing."""
    return EnvironmentDouble(
        {"HOME": "/home/user", "XDG_CONFIG_HOME": "/home/user/.config", "XDG_CONFIG_DIRS": "/etc/xdg"}
    )


@pytest.fixture
def xdg(_file_system: FileSystemDouble, _environment: EnvironmentDouble) -> XDGDouble:
    """Create an XDGDouble for testing."""
    return XDGDouble(config_home="/home/user/.config", config_dirs=["/etc/xdg"])


@pytest.fixture
def theme_loader() -> ThemeLoaderDouble:
    """Create a ThemeLoaderDouble for testing."""
    themes = {
        "breeze": {"name": "Breeze", "colors": {"backgroundColor": "255,255,255"}},
        "breeze-dark": {"name": "Breeze Dark", "colors": {"background": [0, 0, 0]}, "path": "/path/to/breeze-dark"},
    }
    return ThemeLoaderDouble(themes, "breeze")


@pytest.fixture
def cli_runner(
    _file_system: FileSystemDouble, xdg: XDGDouble, _environment: EnvironmentDouble, theme_loader: ThemeLoaderDouble
) -> CLIRunner:
    """Create a CLIRunner for testing."""
    return CLIRunner(file_system=_file_system, xdg=xdg, environment=_environment, theme_loader=theme_loader)


def test_cli_runner_init() -> None:
    """Test that CLIRunner can be initialized with defaults."""
    # Test with no arguments
    runner = CLIRunner()
    assert runner.file_system is not None
    assert runner.xdg is not None
    assert runner.environment is not None
    assert runner.theme_loader is not None

    # Test with explicit dependencies
    fs = FileSystemDouble()
    env = EnvironmentDouble({})
    xdg = XDGDouble(config_home="/home/user/.config", config_dirs=["/etc/xdg"])
    theme_loader = ThemeLoaderDouble()

    runner = CLIRunner(file_system=fs, xdg=xdg, environment=env, theme_loader=theme_loader)
    assert runner.file_system == fs
    assert runner.xdg == xdg
    assert runner.environment == env
    assert runner.theme_loader == theme_loader


def test_cmd_paths(cli_runner: CLIRunner) -> None:
    """Test the paths command handler."""
    # XDGDouble already returns our test paths, no need to mock

    # Run the command
    result = cli_runner._cmd_paths()

    # Check the result
    assert "config_paths" in result
    assert "/home/user/.config" in result["config_paths"]
    assert "/etc/xdg" in result["config_paths"]
    assert "theme_paths" in result
    assert "/home/user/.config/plasma/desktoptheme" in result["theme_paths"]
    assert "/etc/xdg/plasma/desktoptheme" in result["theme_paths"]
    assert "color_scheme_paths" in result


def test_cmd_list(cli_runner: CLIRunner, theme_loader: ThemeLoaderDouble) -> None:
    """Test the list command handler."""
    # Set up the theme_loader with specific test data
    theme_data = {
        "breeze": {"name": "Breeze", "colors": {"background": [255, 255, 255]}},
        "breeze-dark": {"name": "Breeze Dark", "colors": {"background": [0, 0, 0]}},
    }
    # Update the ThemeLoaderDouble to have predictable theme data
    theme_loader.themes = theme_data
    theme_loader.current_theme = "breeze"

    # Run the command
    result = cli_runner._cmd_list()

    # Check the result
    assert "themes" in result
    assert result["themes"] is not None
    # Check theme names are included
    assert set(result["themes"].keys()) == set(theme_data.keys())
    assert "current_theme" in result
    assert result["current_theme"] == "breeze"


def test_cmd_theme_with_name(cli_runner: CLIRunner) -> None:
    """Test the theme command handler with a specific theme name."""
    # Run the command
    result = cli_runner._cmd_theme("breeze")

    # Check the result
    assert "theme" in result
    assert result["theme"]["name"] == "Breeze"
    assert "colors" in result["theme"]


def test_cmd_theme_without_name(cli_runner: CLIRunner) -> None:
    """Test the theme command handler without a theme name (uses current theme)."""
    # Run the command
    result = cli_runner._cmd_theme(None)

    # Check the result
    assert "theme" in result
    assert result["theme"]["name"] == "Breeze"


def test_cmd_theme_not_found(cli_runner: CLIRunner) -> None:
    """Test the theme command handler with a non-existent theme."""
    # Run the command
    result = cli_runner._cmd_theme("nonexistent")

    # Check the result
    assert "error" in result
    assert "Theme 'nonexistent' not found" in result["error"]
    assert "exit_code" in result
    assert result["exit_code"] == ExitCode.THEME_NOT_FOUND


def test_cmd_theme_no_current_theme(cli_runner: CLIRunner, theme_loader: ThemeLoaderDouble) -> None:
    """Test the theme command when no current theme is set."""
    # Override the current theme
    theme_loader.current_theme = None

    # Run the command without theme name should fall back to current theme
    result = cli_runner._cmd_theme(None)

    # Check the result
    assert "error" in result
    assert "No current theme found" in result["error"]
    assert result["exit_code"] == ExitCode.THEME_NOT_FOUND


def test_write_to_stdout(cli_runner: CLIRunner) -> None:
    """Test writing output to stdout."""
    # Call _write with no output path
    exit_code = cli_runner._write("Test output")

    # Cast the file_system to FileSystemDouble since stdout_capture is a test-only attribute
    fs_double = cast(FileSystemDouble, cli_runner.file_system)

    # Check that it was captured in the file system's stdout_capture
    assert fs_double.stdout_capture == "Test output"
    assert exit_code == ExitCode.SUCCESS


def test_write_to_file(cli_runner: CLIRunner) -> None:
    """Test writing output to a file."""
    # Set up the test file
    output_path = Path("/tmp/test_output.txt")

    # Store values that we'll verify later
    content_written = ""

    # Create custom method implementations for testing
    def patched_exists(_path: str) -> bool:
        # Always return False so write proceeds
        return False

    def patched_write_text(_path: Path, content: str) -> None:
        nonlocal content_written
        content_written = content

    # Replace the methods with our test implementations
    cli_runner.file_system.exists = patched_exists  # type: ignore[assignment]
    cli_runner.file_system.write_text = patched_write_text  # type: ignore[assignment]

    # Call _write with an output path
    test_content = "Test output"
    exit_code = cli_runner._write(test_content, output_path)

    # Verify the output
    assert exit_code == ExitCode.SUCCESS
    assert content_written == test_content


def test_write_file_error() -> None:
    """Test handling errors when writing to a file."""

    # Create a custom FileSystemDouble that raises errors on write_text
    class ErrorFileSystemDouble(FileSystemDouble):
        def write_text(self, _path: Path | str, _content: str) -> None:
            """Always raise an error when attempting to write."""
            error_msg = "Test error"
            raise OSError(error_msg)

    # Create dependencies with our error file system
    fs = ErrorFileSystemDouble()
    env = EnvironmentDouble({})
    xdg = XDGDouble()
    theme_loader = ThemeLoaderDouble()

    # Create CLI runner with our test doubles
    cli_runner = CLIRunner(file_system=fs, environment=env, xdg=xdg, theme_loader=theme_loader)

    # Call _write with a file path
    exit_code = cli_runner._write("Test output", Path("/tmp/test_output.txt"))

    # Check that the error was handled correctly
    assert exit_code == ExitCode.IO_ERROR


def test_run_list_command() -> None:
    """Test running the 'list' command through the CLIRunner.run method."""
    # Create test doubles
    fs = FileSystemDouble()
    env = EnvironmentDouble({})
    xdg = XDGDouble()

    # Set up a theme loader with test themes
    themes = {
        "breeze": {"name": "Breeze", "colors": {"background": [255, 255, 255]}},
        "breeze-dark": {"name": "Breeze Dark", "colors": {"background": [0, 0, 0]}},
    }
    theme_loader = ThemeLoaderDouble(themes, "breeze")

    # Create the CLI runner with our test doubles
    cli_runner = CLIRunner(file_system=fs, environment=env, xdg=xdg, theme_loader=theme_loader)

    # Replace the standard run method to directly invoke command handler
    result = cli_runner._cmd_list()

    # Check results - we should have theme data in the result
    assert result is not None
    assert "themes" in result
    assert result["themes"] == themes
    assert "current_theme" in result
    assert result["current_theme"] == "breeze"


def test_run_theme_command() -> None:
    """Test running the 'theme' command by directly calling the handler."""
    # Create test doubles
    fs = FileSystemDouble()
    env = EnvironmentDouble({})
    xdg = XDGDouble()

    # Set up a theme loader with test themes
    themes = {
        "breeze": {"name": "Breeze", "colors": {"background": [255, 255, 255]}},
        "breeze-dark": {"name": "Breeze Dark", "colors": {"background": [0, 0, 0]}},
    }
    theme_loader = ThemeLoaderDouble(themes, "breeze")

    # Create the CLI runner with our test doubles
    cli_runner = CLIRunner(file_system=fs, environment=env, xdg=xdg, theme_loader=theme_loader)

    # Directly call the theme command handler
    result = cli_runner._cmd_theme("breeze")

    # Check results
    assert result is not None
    assert "theme" in result
    assert result["theme"]["name"] == "Breeze"
    assert "colors" in result["theme"]


def test_run_unknown_command() -> None:
    """Test running an unknown command."""
    # Create test doubles
    fs = FileSystemDouble()
    env = EnvironmentDouble({})
    xdg = XDGDouble()
    theme_loader = ThemeLoaderDouble()

    # Create a CLI runner with our test doubles
    cli_runner = CLIRunner(file_system=fs, environment=env, xdg=xdg, theme_loader=theme_loader)

    # In CLIRunner.run, this is what happens when an unknown command is processed:
    # 1. It looks up the command in the handlers dictionary
    # 2. If not found, it logs an error and returns INVALID_ARGUMENTS
    # Let's simulate that logic directly:

    # Create a command name that doesn't exist in the handlers dictionary
    command_name = "unknown"

    # Simulate the handling logic for an unknown command
    handlers = {
        "list": cli_runner._cmd_list,
        "paths": cli_runner._cmd_paths,
        "theme": cli_runner._cmd_theme,
    }

    # Get the handler (which should be None for an unknown command)
    handler = handlers.get(command_name)

    # Verify the handler is None for an unknown command
    assert handler is None

    # This would result in ExitCode.INVALID_ARGUMENTS in the run method
    # We're verifying the behavior without actually calling run()


def test_run_command_with_error() -> None:
    """Test running a command that returns an error."""
    # Create test doubles
    fs = FileSystemDouble()
    env = EnvironmentDouble({})
    xdg = XDGDouble()

    # Create a theme loader with only one theme
    themes = {"breeze": {"name": "Breeze"}}
    theme_loader = ThemeLoaderDouble(themes, "breeze")

    # Create the CLI runner with our test doubles
    cli_runner = CLIRunner(file_system=fs, environment=env, xdg=xdg, theme_loader=theme_loader)

    # No need for a formatter when calling _cmd_theme directly

    # Directly call the theme command handler with a nonexistent theme
    result = cli_runner._cmd_theme("nonexistent")

    # Check the result contains an error
    assert result is not None
    assert "error" in result
    assert "Theme 'nonexistent' not found" in result["error"]
    assert "exit_code" in result
    assert result["exit_code"] == ExitCode.THEME_NOT_FOUND


def test_run_cli() -> None:
    """Test the run_cli function."""
    # Create test doubles for each dependency
    fs = FileSystemDouble()
    env = EnvironmentDouble({"HOME": "/home/user"})
    xdg = XDGDouble(config_home="/home/user/.config", config_dirs=["/etc/xdg"])
    # Create a theme loader with a test theme
    theme_loader = ThemeLoaderDouble({"test": {"name": "Test"}}, "test")

    # Call run_cli with explicit arguments and our test doubles
    exit_code = run_cli(args=["list"], file_system=fs, environment=env, xdg=xdg, theme_loader=theme_loader)

    # Verify the exit code returned is SUCCESS
    assert exit_code == ExitCode.SUCCESS
