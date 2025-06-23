"""Main entry point for running the package as a module."""

from __future__ import annotations

import sys

from kde_colors.cli.cli_runner import run_cli

if __name__ == "__main__":
    sys.exit(run_cli())
