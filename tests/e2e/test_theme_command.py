"""
End-to-end tests for the theme command.

These tests verify that the theme command works correctly when run as a real CLI command.
"""

from __future__ import annotations

from collections.abc import Callable as CallableABC
from pathlib import Path

import pytest


@pytest.mark.usefixtures("kde_home")
def test_theme_success(run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]) -> None:
    """Test the theme command with an existing theme name."""
    # kde_home is used by the fixture to set up the environment
    # Run the CLI command with a theme that exists (Alfa)
    exit_code, stdout, stderr = run_cli(["theme", "Alfa"], None)

    # The command should succeed
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Verify output contains expected theme data
    assert stdout.strip(), "Expected output but got empty string"
    assert "Alfa" in stdout
    assert "ColorScheme" in stdout or "Name" in stdout or "Colors" in stdout


@pytest.mark.usefixtures("kde_home")
def test_theme_with_name(run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]) -> None:
    """Test the theme command with a specific theme name."""
    # kde_home is used by the fixture to set up the environment
    # Run the CLI command with a specific theme - we'll use "Foxtrot" which doesn't exist
    # to ensure deterministic behavior
    exit_code, stdout, stderr = run_cli(["theme", "Foxtrot"], None)

    # Since we're using a theme name that definitely doesn't exist, we expect an error
    assert exit_code != 0, "Expected non-zero exit code for non-existent theme"
    assert "Error" in stderr
    assert "not found" in stderr
    assert stdout.strip() == "", "Expected empty stdout when theme not found"


@pytest.mark.usefixtures("kde_home")
def test_theme_current(run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]) -> None:
    """Test the theme command with no theme name (current theme)."""
    # kde_home is used by the fixture to set up the environment
    # Run the CLI command with no theme specified (should use current theme)
    # In our test environment, the current theme won't exist, so we expect an error
    exit_code, stdout, stderr = run_cli(["theme"], None)

    # Since our test environment doesn't have a properly configured KDE theme,
    # we expect an error about the theme not being found
    assert exit_code != 0, "Expected non-zero exit code for missing current theme"
    assert "Error" in stderr
    assert "not found" in stderr
    assert stdout.strip() == "", "Expected empty stdout when theme not found"


@pytest.mark.usefixtures("kde_home")
def test_theme_success_json(run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]) -> None:
    """Test the theme command with JSON output for an existing theme."""
    # kde_home is used by the fixture to set up the environment
    # Run the CLI command with a theme that exists (Alfa) and JSON output
    exit_code, stdout, stderr = run_cli(["theme", "Alfa", "--json"], None)

    # The command should succeed
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Verify output contains valid JSON
    assert stdout.strip(), "Expected output but got empty string"
    # Basic JSON structure check
    json_output = stdout.strip()
    assert json_output.startswith("{"), "JSON should start with {"
    assert json_output.endswith("}"), "JSON should end with }"
    assert "Alfa" in stdout


@pytest.mark.usefixtures("kde_home")
def test_theme_with_json_output(run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]) -> None:
    """Test the theme command with JSON output."""
    # kde_home is used by the fixture to set up the environment
    # Run the CLI command with a non-existent theme and JSON output
    exit_code, stdout, stderr = run_cli(["theme", "Foxtrot", "--json"], None)

    # Since we're using a theme name that definitely doesn't exist, we expect an error
    assert exit_code != 0, "Expected non-zero exit code for non-existent theme"
    assert "Error" in stderr
    assert "not found" in stderr
    assert stdout.strip() == "", "Expected empty stdout when theme not found"


def test_theme_success_output_to_file(
    kde_home: Path, run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]
) -> None:
    """Test the theme command with successful output to a file."""
    # Create output file path in the temporary directory
    output_path = kde_home / "alfa-theme.txt"

    # Run the CLI command with a theme that exists
    exit_code, stdout, stderr = run_cli(["theme", "Alfa", "--output", str(output_path)], output_path)

    # The command should succeed
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Verify stdout is empty (output went to file instead)
    assert not stdout.strip(), "Expected empty stdout when output is sent to file"

    # Verify file exists and contains theme data
    assert output_path.exists(), "Output file should exist"
    content = output_path.read_text()
    assert content.strip(), "Expected non-empty file"
    assert "Alfa" in content
    assert "ColorScheme" in content or "Name" in content or "Colors" in content


def test_theme_with_output_to_file(
    kde_home: Path, run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]
) -> None:
    """Test the theme command with output to a file."""
    # Create output file path in the temporary directory
    output_path = kde_home / "theme.txt"

    # Run the CLI command with a non-existent theme
    exit_code, stdout, stderr = run_cli(["theme", "Foxtrot", "--output", str(output_path)], output_path)

    # Since we're using a theme name that definitely doesn't exist, we expect an error
    assert exit_code != 0, "Expected non-zero exit code for non-existent theme"
    assert "Error" in stderr
    assert "not found" in stderr

    # Verify stdout is empty
    assert not stdout.strip(), "Expected empty stdout when theme not found"

    # File should not be created when there's an error
    assert not output_path.exists(), "Expected no output file to be created when theme not found"


def test_theme_success_json_output_to_file(
    kde_home: Path, run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]
) -> None:
    """Test the theme command with JSON output to a file (success case)."""
    # Create output file path in the temporary directory
    output_path = kde_home / "alfa-theme.json"

    # Run the CLI command with a theme that exists and JSON output
    exit_code, stdout, stderr = run_cli(["theme", "Alfa", "--json", "--output", str(output_path)], output_path)

    # The command should succeed
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Verify stdout is empty (output went to file instead)
    assert not stdout.strip(), "Expected empty stdout when output is sent to file"

    # Verify file exists and contains JSON data
    assert output_path.exists(), "Output file should exist"
    content = output_path.read_text()
    assert content.strip(), "Expected non-empty file"
    # Basic JSON structure check
    assert content.strip().startswith("{"), "JSON should start with {"
    assert content.strip().endswith("}"), "JSON should end with }"
    assert "Alfa" in content


def test_theme_with_json_output_to_file(
    kde_home: Path, run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]
) -> None:
    """Test the theme command with JSON output to a file."""
    # Create output file path in the temporary directory
    output_path = kde_home / "theme.json"

    # Run the CLI command with a non-existent theme
    exit_code, stdout, stderr = run_cli(["theme", "Foxtrot", "--json", "--output", str(output_path)], output_path)

    # Since we're using a theme name that definitely doesn't exist, we expect an error
    assert exit_code != 0, "Expected non-zero exit code for non-existent theme"
    assert "Error" in stderr
    assert "not found" in stderr

    # Verify stdout is empty
    assert not stdout.strip(), "Expected empty stdout when theme not found"

    # File should not be created when there's an error
    assert not output_path.exists(), "Expected no output file to be created when theme not found"


@pytest.mark.usefixtures("kde_home")
def test_theme_not_found(run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]) -> None:
    """Test the theme command with a non-existent theme."""
    # Run the CLI command with a theme that definitely doesn't exist
    exit_code, stdout, stderr = run_cli(["theme", "Golf"], None)

    # Verify that error message appears in stderr
    assert "Error" in stderr
    assert "not found" in stderr

    # Exit code should be non-zero for errors
    assert exit_code != 0, "Expected non-zero exit code for theme not found error"

    # Verify stdout is empty
    assert stdout.strip() == "", "Expected empty stdout when theme not found"
