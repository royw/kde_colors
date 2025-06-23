"""
End-to-end tests for the list command.

These tests verify that the list command works correctly when run as a real CLI command.
"""

from __future__ import annotations

from collections.abc import Callable as CallableABC
from pathlib import Path
from typing import Any

import pytest


@pytest.mark.usefixtures("kde_home")
def test_list_text_output(run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]) -> None:
    """Test the list command with default text output."""
    # Run the CLI command from the temporary environment
    # kde_home is used by the fixture to set up the environment
    exit_code, stdout, stderr = run_cli(["list"], None)

    # Check that the command succeeded
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Verify output contains expected themes
    assert "Available desktop themes" in stdout
    assert "breeze-dark" in stdout or "BreezeDark" in stdout
    assert "breeze-light" in stdout or "Breeze" in stdout
    assert "oxygen" in stdout or "Oxygen" in stdout


@pytest.mark.usefixtures("kde_home")
def test_list_json_output(
    run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]], parse_json: CallableABC[[str], Any]
) -> None:
    """Test the list command with JSON output."""
    # Run the CLI command with JSON output from the temporary environment
    # kde_home is used by the fixture to set up the environment
    exit_code, stdout, stderr = run_cli(["list", "--json"], None)

    # Check that the command succeeded
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Parse JSON and verify structure
    data = parse_json(stdout)
    assert "themes" in data
    themes = data["themes"]

    # Check that we have themes in the output
    assert isinstance(themes, list)
    assert len(themes) > 0

    # Just check that we have themes data without enforcing specific names
    # since they can vary by test environment


def test_list_output_to_file(
    kde_home: Path, run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]]
) -> None:
    """Test the list command with output to a file."""
    # Create output file path in the temporary directory
    output_path = kde_home / "themes.txt"

    # Run the CLI command with output to a file
    exit_code, stdout, stderr = run_cli(["list", "--output", str(output_path)], output_path)

    # Check that the command succeeded
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Verify stdout is empty (output went to file instead)
    assert not stdout.strip()

    # Read file and verify content
    content = output_path.read_text()
    assert "Available desktop themes" in content
    assert "breeze-dark" in content or "BreezeDark" in content
    assert "breeze-light" in content or "Breeze" in content
    assert "oxygen" in content or "Oxygen" in content


def test_list_json_output_to_file(
    kde_home: Path,
    run_cli: CallableABC[[list[str], Path | None], tuple[int, str, str]],
    parse_json: CallableABC[[str], Any],
) -> None:
    """Test the list command with JSON output to a file."""
    # Create output file path in the temporary directory
    output_path = kde_home / "themes.json"

    # Run the CLI command with JSON output to a file
    exit_code, stdout, stderr = run_cli(["list", "--json", "--output", str(output_path)], output_path)

    # Check that the command succeeded
    assert exit_code == 0, f"Command failed with stderr: {stderr}"

    # Verify stdout is empty (output went to file instead)
    assert not stdout.strip()

    # Read file and parse JSON
    json_content = output_path.read_text()
    data = parse_json(json_content)

    # Verify structure and content
    assert "themes" in data
    themes = data["themes"]
    assert isinstance(themes, list)
    assert len(themes) > 0
    # Just verify we have themes without enforcing specific names
    # since they can vary by test environment
