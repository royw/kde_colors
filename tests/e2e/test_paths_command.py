"""
End-to-end tests for the paths command.

These tests verify that the paths command works correctly when run as a real CLI command.
"""

from __future__ import annotations

from collections.abc import Callable as CallableABC
from pathlib import Path
from typing import Any


def test_paths_text_output(
    kde_home: Path, run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]
) -> None:
    """Test the paths command with default text output."""
    # Run the CLI command
    exit_code, stdout, stderr = run_cli(["paths"], None)

    # Check that the command succeeded
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Verify output contains expected sections
    assert "KDE Theme Search Paths:" in stdout
    assert "Config paths:" in stdout
    assert "Theme paths:" in stdout
    assert "Color scheme paths:" in stdout

    # Verify output contains paths in the temporary home directory
    assert str(kde_home) in stdout


def test_paths_json_output(
    kde_home: Path,
    run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]],
    parse_json: CallableABC[[str], Any],
) -> None:
    """Test the paths command with JSON output."""
    # Run the CLI command
    exit_code, stdout, stderr = run_cli(["paths", "--json"], None)

    # Check that the command succeeded
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Parse JSON and verify structure
    data = parse_json(stdout)

    # Check that we have the expected path categories
    assert "config_paths" in data
    assert "theme_paths" in data
    assert "color_scheme_paths" in data

    # Verify paths in the temporary home directory are included
    all_paths = []
    all_paths.extend(data["config_paths"])
    all_paths.extend(data["theme_paths"])
    all_paths.extend(data["color_scheme_paths"])

    temp_home_in_paths = False
    for path in all_paths:
        if str(kde_home) in path:
            temp_home_in_paths = True
            break

    assert temp_home_in_paths, f"No paths contain temporary home directory: {kde_home}"


def test_paths_output_to_file(
    kde_home: Path, run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]
) -> None:
    """Test the paths command with output to a file."""
    # Create output file path in the temporary directory
    output_path = kde_home / "paths.txt"

    # Run the CLI command
    exit_code, stdout, stderr = run_cli(["paths", "--output", str(output_path)], None)

    # Check that the command succeeded
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Verify stdout is empty (output went to file instead)
    assert not stdout.strip()

    # Verify file content
    content = output_path.read_text()
    assert "KDE Theme Search Paths:" in content
    assert "Config paths:" in content
    assert "Theme paths:" in content
    assert "Color scheme paths:" in content
    assert str(kde_home) in content


def test_paths_json_output_to_file(
    kde_home: Path,
    run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]],
    parse_json: CallableABC[[str], Any],
) -> None:
    """Test the paths command with JSON output to a file."""
    # Create output file path in the temporary directory
    output_path = kde_home / "paths.json"

    # Run the CLI command
    exit_code, stdout, stderr = run_cli(["paths", "--json", "--output", str(output_path)], None)

    # Check that the command succeeded
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Verify stdout is empty (output went to file instead)
    assert not stdout.strip()

    # Read file and parse JSON
    json_content = output_path.read_text()
    data = parse_json(json_content)

    # Verify structure
    assert "config_paths" in data
    assert "theme_paths" in data
    assert "color_scheme_paths" in data

    # Verify paths in the temporary home directory are included
    all_paths = []
    all_paths.extend(data["config_paths"])
    all_paths.extend(data["theme_paths"])
    all_paths.extend(data["color_scheme_paths"])

    temp_home_in_paths = False
    for path in all_paths:
        if str(kde_home) in path:
            temp_home_in_paths = True
            break

    assert temp_home_in_paths, f"No paths contain temporary home directory: {kde_home}"
