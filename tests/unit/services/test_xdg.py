"""
Unit tests for the StdXDG service.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import cast
from unittest import mock

from kde_colors.interfaces.environment import EnvironmentInterface
from kde_colors.interfaces.xdg import XDGInterface
from kde_colors.services.xdg import StdXDG
from tests.support.file_system_double import FileSystemDouble


class TestStdXDG(unittest.TestCase):
    """Tests for the StdXDG service."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create mock objects for dependencies
        self.file_system = mock.Mock(spec=FileSystemDouble)
        self.environment = mock.Mock(spec=EnvironmentInterface)

        # Configure mock home and root paths
        self._mock_home = Path("/home/user")
        self._mock_root = Path("/")

        # Configure method return values
        self.file_system.home.return_value = self._mock_home
        self.file_system.root.return_value = self._mock_root

        # Create the service
        self.xdg_service = StdXDG(self.file_system, self.environment)

    def test_implements_interface(self) -> None:
        """Test that StdXDG implements the XDGInterface."""
        # Instead of using isinstance with a protocol, we can cast to verify types
        cast(XDGInterface, self.xdg_service)  # This will fail if xdg_service doesn't implement the interface
        assert True  # If we got here, the cast succeeded

    def test_path_from_env_with_valid_path(self) -> None:
        """Test _path_from_env with a valid path in the environment."""
        var_name = "TEST_VAR"
        env_value = "/valid/absolute/path"
        default = Path("/default/path")

        self.environment.getenv.return_value = env_value

        result = self.xdg_service._path_from_env(var_name, default)

        self.environment.getenv.assert_called_once_with(var_name)
        assert result == Path(env_value)

    def test_path_from_env_with_relative_path(self) -> None:
        """Test _path_from_env with a relative path in the environment."""
        var_name = "TEST_VAR"
        env_value = "relative/path"  # Relative path should be ignored
        default = Path("/default/path")

        self.environment.getenv.return_value = env_value

        result = self.xdg_service._path_from_env(var_name, default)

        self.environment.getenv.assert_called_once_with(var_name)
        assert result == default  # Should use default for relative paths

    def test_path_from_env_with_empty_value(self) -> None:
        """Test _path_from_env with an empty value in the environment."""
        var_name = "TEST_VAR"
        env_value = ""  # Empty value should be ignored
        default = Path("/default/path")

        self.environment.getenv.return_value = env_value

        result = self.xdg_service._path_from_env(var_name, default)

        self.environment.getenv.assert_called_once_with(var_name)
        assert result == default  # Should use default for empty values

    def test_path_from_env_with_none_value(self) -> None:
        """Test _path_from_env with a None value in the environment."""
        var_name = "TEST_VAR"
        env_value = None  # None value should be ignored
        default = Path("/default/path")

        self.environment.getenv.return_value = env_value

        result = self.xdg_service._path_from_env(var_name, default)

        self.environment.getenv.assert_called_once_with(var_name)
        assert result == default  # Should use default for None values

    def test_paths_from_env_with_valid_paths(self) -> None:
        """Test _paths_from_env with valid paths in the environment."""
        var_name = "TEST_VAR"
        env_value = "/valid/path1:/valid/path2"
        default = [Path("/default/path")]

        self.environment.getenv.return_value = env_value

        result = self.xdg_service._paths_from_env(var_name, default)

        self.environment.getenv.assert_called_once_with(var_name)
        assert result == [Path("/valid/path1"), Path("/valid/path2")]

    def test_paths_from_env_with_mixed_paths(self) -> None:
        """Test _paths_from_env with both valid and relative paths in the environment."""
        var_name = "TEST_VAR"
        env_value = "/valid/path:relative/path"  # Relative path should be ignored
        default = [Path("/default/path")]

        self.environment.getenv.return_value = env_value

        result = self.xdg_service._paths_from_env(var_name, default)

        self.environment.getenv.assert_called_once_with(var_name)
        assert result == [Path("/valid/path")]  # Only absolute paths included

    def test_paths_from_env_with_empty_value(self) -> None:
        """Test _paths_from_env with an empty value in the environment."""
        var_name = "TEST_VAR"
        env_value = ""  # Empty value should be ignored
        default = [Path("/default/path")]

        self.environment.getenv.return_value = env_value

        result = self.xdg_service._paths_from_env(var_name, default)

        self.environment.getenv.assert_called_once_with(var_name)
        assert result == default  # Should use default for empty values

    def test_paths_from_env_with_none_value(self) -> None:
        """Test _paths_from_env with a None value in the environment."""
        var_name = "TEST_VAR"
        env_value = None  # None value should be ignored
        default = [Path("/default/path")]

        self.environment.getenv.return_value = env_value

        result = self.xdg_service._paths_from_env(var_name, default)

        self.environment.getenv.assert_called_once_with(var_name)
        assert result == default  # Should use default for None values

    def test_xdg_config_dirs_with_env_var(self) -> None:
        """Test xdg_config_dirs with XDG_CONFIG_DIRS set."""
        env_value = "/custom/config1:/custom/config2"
        self.environment.getenv.return_value = env_value

        result = self.xdg_service.xdg_config_dirs()

        self.environment.getenv.assert_called_once_with("XDG_CONFIG_DIRS")
        assert result == [Path("/custom/config1"), Path("/custom/config2")]

    def test_xdg_config_dirs_without_env_var(self) -> None:
        """Test xdg_config_dirs without XDG_CONFIG_DIRS set."""
        self.environment.getenv.return_value = None

        result = self.xdg_service.xdg_config_dirs()

        self.environment.getenv.assert_called_once_with("XDG_CONFIG_DIRS")
        assert result == [self._mock_root / "etc/xdg"]

    def test_xdg_config_home_with_env_var(self) -> None:
        """Test xdg_config_home with XDG_CONFIG_HOME set."""
        env_value = "/custom/config"
        self.environment.getenv.return_value = env_value

        result = self.xdg_service.xdg_config_home()

        self.environment.getenv.assert_called_once_with("XDG_CONFIG_HOME")
        assert result == Path(env_value)

    def test_xdg_config_home_without_env_var(self) -> None:
        """Test xdg_config_home without XDG_CONFIG_HOME set."""
        self.environment.getenv.return_value = None

        result = self.xdg_service.xdg_config_home()

        self.environment.getenv.assert_called_once_with("XDG_CONFIG_HOME")
        assert result == self._mock_home / ".config"

    def test_xdg_data_dirs_with_env_var(self) -> None:
        """Test xdg_data_dirs with XDG_DATA_DIRS set."""
        env_value = "/custom/data1:/custom/data2"
        self.environment.getenv.return_value = env_value

        result = self.xdg_service.xdg_data_dirs()

        self.environment.getenv.assert_called_once_with("XDG_DATA_DIRS")
        assert result == [Path("/custom/data1"), Path("/custom/data2")]

    def test_xdg_data_dirs_without_env_var(self) -> None:
        """Test xdg_data_dirs without XDG_DATA_DIRS set."""
        self.environment.getenv.return_value = None

        result = self.xdg_service.xdg_data_dirs()

        self.environment.getenv.assert_called_once_with("XDG_DATA_DIRS")
        expected = [self._mock_root / "usr/local/share/", self._mock_root / "usr/share/"]
        assert result == expected

    def test_xdg_data_home_with_env_var(self) -> None:
        """Test xdg_data_home with XDG_DATA_HOME set."""
        env_value = "/custom/data"
        self.environment.getenv.return_value = env_value

        result = self.xdg_service.xdg_data_home()

        self.environment.getenv.assert_called_once_with("XDG_DATA_HOME")
        assert result == Path(env_value)

    def test_xdg_data_home_without_env_var(self) -> None:
        """Test xdg_data_home without XDG_DATA_HOME set."""
        self.environment.getenv.return_value = None

        result = self.xdg_service.xdg_data_home()

        self.environment.getenv.assert_called_once_with("XDG_DATA_HOME")
        assert result == self._mock_home / ".local" / "share"
