"""
Unit tests for the CLI argument parser.
"""

from __future__ import annotations

import unittest

import pytest

from kde_colors.cli.cli_arg_parser import create_parser, parse_args


class TestCliArgParser(unittest.TestCase):
    """Tests for the CLI argument parser."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.parser = create_parser()

    def test_create_parser(self) -> None:
        """Test that create_parser returns an ArgumentParser with expected configuration."""
        parser = create_parser()

        # Check basic parser configuration
        assert parser.prog == "kde-colors"
        assert "extracts color schemes" in (parser.description or "")

    def test_version_argument(self) -> None:
        """Test that the parser has a --version argument."""
        # We can't easily test the action="version" directly
        # but we can verify it's in the parser's actions
        has_version_action = any(action.dest == "version" for action in self.parser._actions)
        assert has_version_action

    def test_verbose_argument(self) -> None:
        """Test the verbose argument."""
        # Parse with no verbosity
        args = parse_args(["list"])
        assert args.log_level == 0

        # Parse with one level of verbosity
        args = parse_args(["list", "-v"])
        assert args.log_level == 1

        # Parse with multiple levels of verbosity
        args = parse_args(["list", "-vvv"])
        assert args.log_level == 3

    def test_list_command(self) -> None:
        """Test the 'list' command parsing."""
        # Basic command
        args = parse_args(["list"])
        assert args.command == "list"
        assert not args.json  # Default is text format (not JSON)
        assert args.output is None

        # With json and output options
        args = parse_args(["list", "--json", "--output", "themes.json"])
        assert args.command == "list"
        assert args.json
        assert args.output == "themes.json"

    def test_paths_command(self) -> None:
        """Test the 'paths' command parsing."""
        # Basic command
        args = parse_args(["paths"])
        assert args.command == "paths"
        assert not args.json  # Default is text format (not JSON)
        assert args.output is None

        # With json and output options
        args = parse_args(["paths", "--json", "--output", "paths.json"])
        assert args.command == "paths"
        assert args.json
        assert args.output == "paths.json"

    def test_theme_command(self) -> None:
        """Test the 'theme' command parsing."""
        # Without theme name (current theme)
        args = parse_args(["theme"])
        assert args.command == "theme"
        assert args.theme_name is None
        assert not args.json  # Default is text format (not JSON)

        # With specific theme
        args = parse_args(["theme", "Breeze"])
        assert args.command == "theme"
        assert args.theme_name == "Breeze"

        # With all options
        args = parse_args(["theme", "Breeze", "--json", "--output", "theme.json"])
        assert args.command == "theme"
        assert args.theme_name == "Breeze"
        assert args.json
        assert args.output == "theme.json"

    def test_required_command(self) -> None:
        """Test that a command is required."""
        # This should raise a SystemExit because no command was provided
        with pytest.raises(SystemExit):
            parse_args([])

    def test_invalid_command(self) -> None:
        """Test handling of invalid command."""
        # This should raise SystemExit for an unknown command
        with pytest.raises(SystemExit):
            parse_args(["invalid-command"])
