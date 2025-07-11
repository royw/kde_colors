"""
CLI command execution module.

This module provides the implementation for executing CLI commands based on parsed arguments.
It serves as the core orchestrator that connects the user's command line input to the appropriate
application logic and service implementations.

Why this module exists:
- Decouples command execution from argument parsing
- Coordinates dependency injection for required services
- Manages command execution flow and exit codes
- Handles output formatting and redirection

How it works:
- Creates all required service instances (FileSystem, ThemeLoader, etc.)
- Maps command names to handler methods using a dispatch dictionary
- Calls the appropriate handler based on the command from parsed arguments
- Formats and outputs the results using output formatters
- Returns appropriate exit codes to the shell

Key Functions:
- run_cli(): The main entry point for the application, responsible for instantiating and running the CLIRunner class.
  This function is called directly by __main__.py and serves as the package's console script entry point and a test entry point.

This module implements the Command pattern, where each CLI command is handled by a dedicated
method that processes arguments and delegates to appropriate services.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from enum import IntEnum
from pathlib import Path
from typing import Any

from loguru import logger

from kde_colors.cli.cli_arg_parser import parse_args
from kde_colors.interfaces.environment import EnvironmentInterface
from kde_colors.interfaces.file_system import FileSystemInterface
from kde_colors.interfaces.output_formatter import OutputFormatterInterface
from kde_colors.interfaces.theme_loader import ThemeLoaderInterface
from kde_colors.interfaces.xdg import XDGInterface
from kde_colors.services.environment import StdEnvironment
from kde_colors.services.file_system import StdFileSystem
from kde_colors.services.output_formatter import get_output_formatter
from kde_colors.services.theme_loader import ThemeLoader
from kde_colors.services.xdg import StdXDG


class ExitCode(IntEnum):
    """Exit codes used by the application."""

    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_ARGUMENTS = 2
    THEME_NOT_FOUND = 3
    IO_ERROR = 4


class CLIRunner:
    """Orchestrates the execution of commands."""

    def __init__(
        self,
        file_system: FileSystemInterface | None = None,
        xdg: XDGInterface | None = None,
        environment: EnvironmentInterface | None = None,
        theme_loader: ThemeLoaderInterface | None = None,
    ) -> None:
        """Initialize the CLI runner."""
        self.file_system = file_system or StdFileSystem()
        environment = environment or StdEnvironment()
        self.xdg = xdg or StdXDG(file_system or StdFileSystem(), environment)
        self.environment = environment
        self.theme_loader = theme_loader or ThemeLoader(self.file_system, self.xdg)

    def _setup_logging(self, log_level: str) -> None:
        # log_level contains the number of -v arguments
        # log_level = 0 => warning
        # log_level = 1 => info
        # log_level = 2 => debug
        # log_level = 3 => trace
        logger.remove()
        levels = ["WARNING", "INFO", "DEBUG", "TRACE"]
        if int(log_level) >= len(levels):
            log_level = str(len(levels) - 1)
        level = levels[int(log_level)]
        # Add normal logs to stdout
        logger.add(sys.stdout, level=level, filter=lambda record: record["level"].no < logger.level("ERROR").no)
        # Add error logs to stderr
        logger.add(sys.stderr, level="ERROR")
        logger.info("log level: {}", level)

    def run(self, args: list[str] | None = None) -> int:
        """Run the CLI with the given arguments.

        Args:
            args: Command line arguments (defaults to sys.argv[1:] if None)

        Returns:
            Exit code as defined in ExitCode enum
        """
        try:
            # Parse the arguments
            arguments = parse_args(args or sys.argv[1:])
            self._setup_logging(arguments.log_level)
            logger.debug("arguments: {}", arguments)

            # Get the output formatter
            format = "json" if arguments.json else "text"
            formatter: OutputFormatterInterface = get_output_formatter(format, arguments.command)
            logger.debug("formatter: {}", formatter)

            # Get the command handler
            handlers: dict[str, Callable[[str | None], dict[str, Any]]] = {
                "list": self._cmd_list,
                "paths": self._cmd_paths,
                "theme": self._cmd_theme,
            }
            handler = handlers.get(arguments.command)
            if not handler:
                # This should not happen if the argument parser is configured correctly
                error_msg = f"Unknown command '{arguments.command}'"
                logger.error(error_msg)
                return ExitCode.INVALID_ARGUMENTS

            # Execute the command handler
            # Only theme command expects theme_name, others don't need it
            result = handler(arguments.theme_name) if arguments.command == "theme" else handler(None)

            # Check if the command handler returned an error
            if "error" in result:
                logger.error(f"Error: {result['error']}")
                # Ensure exit_code is an int
                exit_code = result.get("exit_code", ExitCode.GENERAL_ERROR)
                return int(exit_code)

            # Format and write the result from the command handler
            return self._write(formatter.format(result), arguments.output)

        except ValueError as e:
            # Handle expected value errors (e.g., missing theme name)
            logger.error(f"Error: {e}")
            return ExitCode.INVALID_ARGUMENTS

        except FileNotFoundError as e:
            # Handle file system errors
            logger.error(f"Error: {e}")
            return ExitCode.IO_ERROR

        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Error: {e}")
            return ExitCode.GENERAL_ERROR

    def _write(self, data: str, output_path: Path | None = None) -> int:
        """Write data to output path or stdout.

        Args:
            data: The formatted data to write
            output_path: Optional path to write the data to instead of stdout

        Returns:
            Exit code as defined in ExitCode enum
        """
        try:
            if output_path:
                # Ensure the parent directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                # Write to file
                logger.info("Writing output to file: {}", output_path)
                self.file_system.write_text(output_path, data)
            else:
                # Write to stdout
                self.file_system.write_stdout(data)
            return ExitCode.SUCCESS
        except Exception as e:
            logger.error(f"Error writing output: {e}")
            return ExitCode.IO_ERROR

    def _cmd_paths(self, _: str | None = None) -> dict[str, Any]:
        """Handle the 'paths' command.

        Returns a dictionary with paths where KDE theme files are located.

        Args:
            _: Unused theme name parameter (required for handler signature)

        Returns:
            Dictionary with config and theme file paths
        """
        config_paths = [self.xdg.xdg_config_home(), *self.xdg.xdg_config_dirs()]
        theme_paths = [str(path / "plasma" / "desktoptheme") for path in config_paths]
        color_scheme_paths = [str(path / "color-schemes") for path in config_paths]

        return {
            "config_paths": [str(path) for path in config_paths],
            "theme_paths": theme_paths,
            "color_scheme_paths": color_scheme_paths,
        }

    def _cmd_list(self, _: str | None = None) -> dict[str, Any]:
        """Handle the 'list' command.

        Lists all available themes with names and locations.

        Returns:
            Dictionary with theme information
        """
        themes = self.theme_loader.load_themes()
        current_theme = self.theme_loader.get_current_theme()
        return {"current_theme": current_theme, "themes": themes}

    def _cmd_theme(self, theme_name: str | None = None) -> dict[str, Any]:
        """
        Handle the 'theme' command.

        Shows detailed information about a specific theme including its colors.
        If no theme name is provided, the current theme will be used.

        Args:
            theme_name: Name of the theme to display information for (optional)

        Returns:
            Dictionary with theme details or an error if theme not found
        """
        # If no theme name provided, use the current theme
        if not theme_name:
            current_theme = self.theme_loader.get_current_theme()
            if not current_theme:
                return {"error": "No current theme found", "exit_code": ExitCode.THEME_NOT_FOUND}
            logger.debug(f"Using current theme: {current_theme}")
            theme_name = current_theme

        theme = self.theme_loader.load(theme_name)
        if not theme:
            return {"error": f"Theme '{theme_name}' not found", "exit_code": ExitCode.THEME_NOT_FOUND}

        return {"theme": theme}


def run_cli(
    args: list[str] | None = None,
    file_system: FileSystemInterface | None = None,
    xdg: XDGInterface | None = None,
    environment: EnvironmentInterface | None = None,
    theme_loader: ThemeLoaderInterface | None = None,
) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:] if None)
        file_system: FileSystem implementation to use
        xdg: XDG implementation to use
        environment: Environment implementation to use
        theme_loader: ThemeLoader implementation to use

    Returns:
        Exit code as defined in ExitCode enum
    """
    return CLIRunner(file_system, xdg, environment, theme_loader).run(args)
