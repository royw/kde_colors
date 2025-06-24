"""Main entry point for running the KDE Colors CLI tool as a module.

This module serves as the execution entry point when the package is run directly with
`python -m kde_colors` rather than through the installed console script.

Why this module exists:
- Provides a standard Python package execution entry point
- Ensures the application can be run without installation
- Maintains Python best practices for module execution

How it works:
- Imports the run_cli function from the cli_runner module
- Calls run_cli when this module is executed directly
- Passes the return code from run_cli to sys.exit to properly set the process exit code

This approach follows the standard Python pattern where __main__.py serves as a thin
wrapper around the actual application logic located elsewhere in the package.
"""

from __future__ import annotations

import sys

from kde_colors.cli.cli_runner import run_cli

if __name__ == "__main__":
    sys.exit(run_cli())
