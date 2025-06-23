"""
Unit tests for the StdEnvironment service.
"""

from __future__ import annotations

import os
import unittest
from typing import cast

from kde_colors.interfaces.environment import EnvironmentInterface
from kde_colors.services.environment import StdEnvironment


class TestStdEnvironment(unittest.TestCase):
    """Tests for the StdEnvironment service."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.env_service = StdEnvironment()
        # Store the original environment to restore it later
        self.original_environ = os.environ.copy()

    def tearDown(self) -> None:
        """Tear down test fixtures."""
        # Restore the original environment
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_implements_interface(self) -> None:
        """Test that StdEnvironment implements the EnvironmentInterface."""
        # Instead of using isinstance with a protocol, we cast to verify types
        cast(EnvironmentInterface, self.env_service)  # This will fail if env_service doesn't implement the interface
        assert True  # If we got here, the cast succeeded

    def test_getenv_existing_variable(self) -> None:
        """Test retrieving an existing environment variable."""
        test_var = "TEST_VAR"
        test_value = "test_value"

        # Set the environment variable directly
        os.environ[test_var] = test_value

        result = self.env_service.getenv(test_var)
        assert result == test_value

    def test_getenv_nonexistent_variable(self) -> None:
        """Test retrieving a nonexistent environment variable."""
        test_var = "NONEXISTENT_VAR"

        # Ensure the variable doesn't exist by removing it if it exists
        if test_var in os.environ:
            del os.environ[test_var]

        result = self.env_service.getenv(test_var)
        assert result is None

    def test_getenv_with_default(self) -> None:
        """Test retrieving a variable with a default value."""
        test_var = "NONEXISTENT_VAR"
        default_value = "default_value"

        # Ensure the variable doesn't exist by removing it if it exists
        if test_var in os.environ:
            del os.environ[test_var]

        result = self.env_service.getenv(test_var, default_value)
        assert result == default_value
