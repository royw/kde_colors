"""
Command-line argument parsing module.

This module defines and handles command-line argument parsing using the sub-parser pattern
from Python's argparse module.
"""

from __future__ import annotations

import argparse
import importlib.metadata


def create_parser() -> argparse.ArgumentParser:
    """
    Creates and configures the command-line argument parser.

    Returns:
        The configured argument parser with all subparsers and options.
    """
    # Create the main parser
    parser = argparse.ArgumentParser(
        prog="kde-colors",
        description="CLI tool that extracts color schemes from KDE themes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Add global options
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="log_level",
        default=0,
        help="Increase verbosity level. Can be specified multiple times for more detail.",
    )

    # Create subparsers
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="valid commands",
        help="command help",
        required=True,
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List all available KDE themes installed on the system",
        description="List all available KDE themes installed on the system",
    )
    list_parser.add_argument(
        "-f", "--format", choices=["text", "json"], default="json", help="Output format (default: %(default)s)"
    )
    list_parser.add_argument(
        "-o", "--output", metavar="PATH", help="Write output to the specified file instead of stdout"
    )

    # Paths command - keeping this from the architecture document
    paths_parser = subparsers.add_parser(
        "paths",
        help="Show theme search paths",
        description="Display the paths where KDE themes are searched for",
    )
    paths_parser.add_argument(
        "-f", "--format", choices=["text", "json"], default="text", help="Output format (default: %(default)s)"
    )
    paths_parser.add_argument(
        "-o", "--output", metavar="PATH", help="Write output to the specified file instead of stdout"
    )

    # Theme command
    theme_parser = subparsers.add_parser(
        "theme",
        help="Display theme details",
        description="Show detailed information about a specific theme",
    )
    theme_parser.add_argument(
        "theme_name",
        nargs="?",  # Make it optional to support getting the current theme
        help="Name of the theme to display. If not specified, the current theme will be used.",
    )
    theme_parser.add_argument(
        "-f", "--format", choices=["text", "json"], default="text", help="Output format (default: %(default)s)"
    )
    theme_parser.add_argument(
        "-o", "--output", metavar="PATH", help="Write output to the specified file instead of stdout"
    )

    return parser


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """
    Parses command-line arguments and applies defaults.

    Args:
        args: Command-line arguments to parse. If None, uses sys.argv[1:].

    Returns:
        Namespace containing the parsed command-line arguments.
    """
    parser = create_parser()
    return parser.parse_args(args)


def get_version() -> str:
    """
    Retrieves the application version.

    Returns:
        The package version string.
    """
    try:
        return importlib.metadata.version("kde_colors")
    except importlib.metadata.PackageNotFoundError:
        return "0.1.0"  # Default during development
