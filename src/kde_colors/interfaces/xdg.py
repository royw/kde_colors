from __future__ import annotations

from pathlib import Path
from typing import Protocol


class XDGInterface(Protocol):
    """XDG Base Directory Specification injector."""

    def xdg_config_dirs(self) -> list[Path]:
        """Return a list of Paths corresponding to XDG_CONFIG_DIRS."""
        ...

    def xdg_config_home(self) -> Path:
        """Return a Path corresponding to XDG_CONFIG_HOME."""
        ...

    def xdg_data_dirs(self) -> list[Path]:
        """Return a list of Paths corresponding to XDG_DATA_DIRS."""
        ...

    def xdg_data_home(self) -> Path:
        """Return a Path corresponding to XDG_DATA_HOME."""
        ...

    def get_config_dir(self) -> str:
        """Get the application config directory path."""
        ...

    def get_cache_dir(self) -> str:
        """Get the application cache directory path."""
        ...

    def get_data_dir(self) -> str:
        """Get the application data directory path."""
        ...
