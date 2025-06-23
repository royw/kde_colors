"""Integration tests for the 'config' CLI command."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from kde_colors.cli.cli_runner import ExitCode, run_cli
from kde_colors.interfaces.file_system import FileSystemInterface
from kde_colors.interfaces.xdg import XDGInterface
from tests.support.file_system_double import FileSystemDouble
from tests.support.xdg_double import XDGDouble


def test_config_command() -> None:
    """Test that the config command returns the correct configuration path information."""
    # Setup
    file_system = FileSystemDouble()
    xdg_double = XDGDouble()

    # Set up expected paths
    config_dir = Path("/fake/config/dir")
    cache_dir = Path("/fake/cache/dir")
    data_dir = Path("/fake/data/dir")

    # Configure XDG double with test paths
    xdg_double.config_dir = str(config_dir)
    xdg_double.cache_dir = str(cache_dir)
    xdg_double.data_dir = str(data_dir)

    # Run command
    exit_code = run_cli(
        args=["config"], file_system=cast(FileSystemInterface, file_system), xdg=cast(XDGInterface, xdg_double)
    )

    # Verify results
    assert exit_code == ExitCode.SUCCESS

    # Check stdout output was captured
    assert file_system.stdout_capture
    stdout = file_system.stdout_capture

    # Verify it contains expected config information
    assert str(config_dir) in stdout
    assert str(cache_dir) in stdout
    assert str(data_dir) in stdout


def test_config_command_with_json_output() -> None:
    """Test that the config command with JSON output works correctly."""
    # Setup
    file_system = FileSystemDouble()
    xdg_double = XDGDouble()

    # Set up expected paths
    config_dir = Path("/fake/config/dir")
    cache_dir = Path("/fake/cache/dir")
    data_dir = Path("/fake/data/dir")

    # Configure XDG double with test paths
    xdg_double.config_dir = str(config_dir)
    xdg_double.cache_dir = str(cache_dir)
    xdg_double.data_dir = str(data_dir)

    output_path = Path("/tmp/config.json")

    # Run command
    exit_code = run_cli(
        args=["config", "--format", "json", "--output", str(output_path)],
        file_system=cast(FileSystemInterface, file_system),
        xdg=cast(XDGInterface, xdg_double),
    )

    # Verify results
    assert exit_code == ExitCode.SUCCESS

    # Check that file was written
    assert file_system.file_exists(str(output_path))

    # Check content
    content = file_system.read_text(output_path)
    assert str(config_dir).replace("\\", "\\\\") in content
    assert str(cache_dir).replace("\\", "\\\\") in content
    assert str(data_dir).replace("\\", "\\\\") in content
