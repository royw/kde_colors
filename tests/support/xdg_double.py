"""
XDG test double that implements the XDGInterface for testing.
"""

from __future__ import annotations

from pathlib import Path

from kde_colors.interfaces.xdg import XDGInterface


class XDGDouble(XDGInterface):
    """
    Test double implementation of the XDGInterface for testing.

    Allows setting up specific XDG paths for testing.
    """

    def __init__(
        self,
        cache_home: Path | str | None = None,
        config_dirs: list[Path | str] | None = None,
        config_home: Path | str | None = None,
        data_dirs: list[Path | str] | None = None,
        data_home: Path | str | None = None,
        runtime_dir: Path | str | None = None,
        state_home: Path | str | None = None,
        # Additional attributes for direct setting in tests
        config_dir: str | None = None,
        cache_dir: str | None = None,
        data_dir: str | None = None,
    ):
        """
        Initialize the XDG test double with configurable paths.

        Args:
            cache_home: Path for XDG_CACHE_HOME
            config_dirs: Paths for XDG_CONFIG_DIRS
            config_home: Path for XDG_CONFIG_HOME
            data_dirs: Paths for XDG_DATA_DIRS
            data_home: Path for XDG_DATA_HOME
            runtime_dir: Path for XDG_RUNTIME_DIR
            state_home: Path for XDG_STATE_HOME
        """
        self._cache_home = Path(cache_home) if cache_home else Path.home() / ".cache"
        self._config_dirs = [Path(p) for p in config_dirs] if config_dirs else [Path("/etc/xdg")]
        self._config_home = Path(config_home) if config_home else Path.home() / ".config"
        self._data_dirs = (
            [Path(p) for p in data_dirs]
            if data_dirs
            else [
                Path("/usr/local/share"),
                Path("/usr/share"),
            ]
        )
        self._data_home = Path(data_home) if data_home else Path.home() / ".local" / "share"
        self._runtime_dir = Path(runtime_dir) if runtime_dir else None
        self._state_home = Path(state_home) if state_home else Path.home() / ".local" / "state"

        # These are used directly by tests
        self._config_dir = config_dir
        self._cache_dir = cache_dir
        self._data_dir = data_dir

    def xdg_cache_home(self) -> Path:
        """Return a Path corresponding to XDG_CACHE_HOME."""
        return self._cache_home

    def xdg_config_dirs(self) -> list[Path]:
        """Return a list of Paths corresponding to XDG_CONFIG_DIRS."""
        return self._config_dirs

    def xdg_config_home(self) -> Path:
        """Return a Path corresponding to XDG_CONFIG_HOME."""
        return self._config_home

    def xdg_data_dirs(self) -> list[Path]:
        """Return a list of Paths corresponding to XDG_DATA_DIRS."""
        return self._data_dirs

    def xdg_data_home(self) -> Path:
        """Return a Path corresponding to XDG_DATA_HOME."""
        return self._data_home

    def get_config_dir(self) -> str:
        """Get the application config directory path.

        Returns:
            String representation of the XDG config directory path
        """
        # Return directly set path if available, otherwise use default
        if self._config_dir is not None:
            return self._config_dir
        return str(self._config_home / "kde-colors")

    def get_cache_dir(self) -> str:
        """Get the application cache directory path.

        Returns:
            String representation of the XDG cache directory path
        """
        # Return directly set path if available, otherwise use default
        if self._cache_dir is not None:
            return self._cache_dir
        return str(self._cache_home / "kde-colors")

    def get_data_dir(self) -> str:
        """Get the application data directory path.

        Returns:
            String representation of the XDG data directory path
        """
        # Return directly set path if available, otherwise use default
        if self._data_dir is not None:
            return self._data_dir
        return str(self._data_home / "kde-colors")

    def xdg_runtime_dir(self) -> Path | None:
        """Return a Path corresponding to XDG_RUNTIME_DIR or None if not available."""
        return self._runtime_dir

    def xdg_state_home(self) -> Path:
        """Return a Path corresponding to XDG_STATE_HOME."""
        return self._state_home

    # Property getters and setters for test configuration
    @property
    def config_dir(self) -> str | None:
        """Get the config directory for testing."""
        return self._config_dir

    @config_dir.setter
    def config_dir(self, value: str) -> None:
        """Set the config directory for testing."""
        self._config_dir = value

    @property
    def cache_dir(self) -> str | None:
        """Get the cache directory for testing."""
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, value: str) -> None:
        """Set the cache directory for testing."""
        self._cache_dir = value

    @property
    def data_dir(self) -> str | None:
        """Get the data directory for testing."""
        return self._data_dir

    @data_dir.setter
    def data_dir(self, value: str) -> None:
        """Set the data directory for testing."""
        self._data_dir = value

    def set_config_home(self, path: Path | str) -> None:
        """
        Set the XDG_CONFIG_HOME path.

        Args:
            path: New path for XDG_CONFIG_HOME
        """
        self._config_home = Path(path)

    def set_data_home(self, path: Path | str) -> None:
        """
        Set the XDG_DATA_HOME path.

        Args:
            path: New path for XDG_DATA_HOME
        """
        self._data_home = Path(path)

    def set_config_dirs(self, paths: list[Path | str]) -> None:
        """
        Set the XDG_CONFIG_DIRS paths.

        Args:
            paths: New paths for XDG_CONFIG_DIRS
        """
        self._config_dirs = [Path(p) for p in paths]

    def set_data_dirs(self, paths: list[Path | str]) -> None:
        """
        Set the XDG_DATA_DIRS paths.

        Args:
            paths: New paths for XDG_DATA_DIRS
        """
        self._data_dirs = [Path(p) for p in paths]
