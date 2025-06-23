"""
End-to-end test fixtures for the KDE Colors CLI.

This module provides pytest fixtures to set up a temporary environment
with fake KDE theme files for end-to-end testing.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any, TypeVar

import pytest

T = TypeVar("T")


@pytest.fixture
def kde_home() -> Generator[Path, None, None]:
    """Create a temporary home directory with fake KDE theme files.

    This fixture sets up a temporary directory structure that mimics a KDE user's
    home directory with configuration and theme files. It also sets required
    environment variables to point to this temporary location.

    Returns:
        Path object to the temporary home directory
    """
    # Save original environment
    original_home = os.environ.get("HOME")
    original_xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    original_xdg_data_home = os.environ.get("XDG_DATA_HOME")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create directory structure
        temp_home = Path(temp_dir)

        # Create KDE config directories
        kde_config_dir = temp_home / ".config" / "kde"
        kde_config_dir.mkdir(parents=True, exist_ok=True)

        # Create KDE data directories
        kde_data_dir = temp_home / ".local" / "share" / "color-schemes"
        kde_data_dir.mkdir(parents=True, exist_ok=True)

        # Create a plasmarc file with active theme
        plasma_rc = kde_config_dir / "plasmarc"
        plasma_rc.parent.mkdir(parents=True, exist_ok=True)
        plasma_rc.write_text(
            """[Theme]
name=Breeze
"""
        )

        # Create example color scheme files
        themes = ["Breeze", "BreezeLight", "BreezeDark", "Kubuntu", "Oxygen"]
        for theme in themes:
            theme_file = kde_data_dir / f"{theme}.colors"
            theme_file.write_text(
                f"""[General]
Name={theme}
ColorScheme={theme}

[Colors:Button]
BackgroundNormal=255,255,255
ForegroundNormal=0,0,0

[Colors:View]
BackgroundNormal=240,240,240
ForegroundNormal=10,10,10
"""
            )

        # Set environment variables
        os.environ["HOME"] = str(temp_home)
        os.environ["XDG_CONFIG_HOME"] = str(temp_home / ".config")
        os.environ["XDG_DATA_HOME"] = str(temp_home / ".local" / "share")

        # Return the temporary directory path
        yield temp_home

        # Restore original environment
        if original_home:
            os.environ["HOME"] = original_home
        else:
            del os.environ["HOME"]

        if original_xdg_config_home:
            os.environ["XDG_CONFIG_HOME"] = original_xdg_config_home
        else:
            os.environ.pop("XDG_CONFIG_HOME", None)

        if original_xdg_data_home:
            os.environ["XDG_DATA_HOME"] = original_xdg_data_home
        else:
            os.environ.pop("XDG_DATA_HOME", None)


@pytest.fixture
def run_cli() -> Callable[[list[str], Path | None], tuple[int, str, str]]:
    """Run the KDE Colors CLI with the specified arguments.

    Args:
        args: A list of command-line arguments to pass to the CLI
        output_path: Optional path to check for output file existence

    Returns:
        A tuple of (exit_code, stdout, stderr)
    """

    def _run_cli(args: list[str], output_path: Path | None = None) -> tuple[int, str, str]:
        """Run kde-colors CLI with given arguments and return results."""
        # Get the project root directory (where pyproject.toml is)
        project_dir = Path(__file__).parent.parent.parent

        # Construct the command to run
        cmd = ["python", "-m", "kde_colors", *args]

        # Run the command and capture output
        # Explicitly pass all environment variables including the ones set in kde_home fixture
        process = subprocess.run(
            cmd,
            check=False,
            cwd=project_dir,
            capture_output=True,
            text=True,
            env=os.environ,  # This has the HOME, XDG_CONFIG_HOME, etc. from the kde_home fixture
        )

        # Check if output file exists if path specified and there's no error in stderr
        if output_path is not None and process.returncode == 0 and "Error" not in process.stderr:
            assert output_path.exists(), f"Output file {output_path} not created"

        return process.returncode, process.stdout, process.stderr

    return _run_cli


@pytest.fixture
def parse_json() -> Callable[[str], Any]:
    """Parse JSON output from the CLI.

    Args:
        text: JSON string to parse

    Returns:
        Parsed JSON data
    """

    def _parse_json(text: str) -> Any:
        """Parse JSON from string."""
        return json.loads(text)

    return _parse_json
