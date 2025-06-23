"""
End-to-end tests for the theme command.

These tests verify that the theme command works correctly when run as a real CLI command.
"""

from __future__ import annotations

from collections.abc import Callable as CallableABC
from pathlib import Path

import pytest


@pytest.mark.usefixtures("kde_home")
def test_theme_with_name(run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]) -> None:
    """Test the theme command with a specific theme name."""
    # kde_home is used by the fixture to set up the environment
    # Run the CLI command with a specific theme - we'll use "BreezeTest" which doesn't exist
    # to ensure deterministic behavior
    exit_code, stdout, stderr = run_cli(["theme", "BreezeTest"], None)

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
def test_theme_with_json_output(run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]) -> None:
    """Test the theme command with JSON output."""
    # kde_home is used by the fixture to set up the environment
    # Run the CLI command with a non-existent theme and JSON output
    exit_code, stdout, stderr = run_cli(["theme", "BreezeTest", "--json"], None)

    # Since we're using a theme name that definitely doesn't exist, we expect an error
    assert exit_code != 0, "Expected non-zero exit code for non-existent theme"
    assert "Error" in stderr
    assert "not found" in stderr
    assert stdout.strip() == "", "Expected empty stdout when theme not found"


def test_theme_with_output_to_file(
    kde_home: Path, run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]
) -> None:
    """Test the theme command with output to a file."""
    # Create output file path in the temporary directory
    output_path = kde_home / "theme.txt"

    # Run the CLI command with a non-existent theme
    exit_code, stdout, stderr = run_cli(["theme", "BreezeTest", "--output", str(output_path)], output_path)

    # Since we're using a theme name that definitely doesn't exist, we expect an error
    assert exit_code != 0, "Expected non-zero exit code for non-existent theme"
    assert "Error" in stderr
    assert "not found" in stderr

    # Verify stdout is empty
    assert not stdout.strip(), "Expected empty stdout when theme not found"

    # File should not be created when there's an error
    assert not output_path.exists(), "Expected no output file to be created when theme not found"


def test_theme_with_json_output_to_file(
    kde_home: Path, run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]
) -> None:
    """Test the theme command with JSON output to a file."""
    # Create output file path in the temporary directory
    output_path = kde_home / "theme.json"

    # Run the CLI command with a non-existent theme
    exit_code, stdout, stderr = run_cli(["theme", "BreezeTest", "--json", "--output", str(output_path)], output_path)

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
    exit_code, stdout, stderr = run_cli(["theme", "NonExistentTheme"], None)

    # Verify that error message appears in stderr
    assert "Error" in stderr
    assert "not found" in stderr

    # Exit code should be non-zero for errors
    assert exit_code != 0, "Expected non-zero exit code for theme not found error"

    # Verify stdout is empty
    assert stdout.strip() == "", "Expected empty stdout when theme not found"
