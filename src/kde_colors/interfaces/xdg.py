from __future__ import annotations

from pathlib import Path
from typing import Protocol


class XDGInterface(Protocol):
    """XDG Base Directory Specification injector."""

    def xdg_cache_home(self) -> Path:
        """Return a Path corresponding to XDG_CACHE_HOME."""
        ...

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

    def xdg_runtime_dir(self) -> Path | None:
        """Return a Path corresponding to XDG_RUNTIME_DIR or None if not available."""
        ...

    def xdg_state_home(self) -> Path:
        """Return a Path corresponding to XDG_STATE_HOME."""
        ...
