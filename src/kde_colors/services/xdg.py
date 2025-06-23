from __future__ import annotations

from pathlib import Path

from kde_colors.interfaces.environment import EnvironmentInterface
from kde_colors.interfaces.file_system import FileSystemInterface
from kde_colors.interfaces.xdg import XDGInterface


class StdXDG(XDGInterface):
    """
    XDG Base Directory Specification injector using FileSystem and Environment interfaces.
    Based on xdg_base_dirs.py from the xdg-base-dirs package.
    """

    def __init__(self, file_system: FileSystemInterface, environment: EnvironmentInterface):
        self.file_system = file_system
        self.environment = environment

    # Copyright © Scott Stevenson <scott@stevenson.io>
    #
    # Permission to use, copy, modify, and/or distribute this software for
    # any purpose with or without fee is hereby granted, provided that the
    # above copyright notice and this permission notice appear in all
    # copies.
    #
    # THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
    # WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
    # WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
    # AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
    # DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
    # PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
    # TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
    # PERFORMANCE OF THIS SOFTWARE.

    """XDG Base Directory Specification variables.

    xdg_cache_home(), xdg_config_home(), xdg_data_home(), and xdg_state_home()
    return pathlib.Path objects containing the value of the environment variable
    named XDG_CACHE_HOME, XDG_CONFIG_HOME, XDG_DATA_HOME, and XDG_STATE_HOME
    respectively, or the default defined in the specification if the environment
    variable is unset, empty, or contains a relative path rather than absolute
    path.

    xdg_config_dirs() and xdg_data_dirs() return a list of pathlib.Path
    objects containing the value, split on colons, of the environment
    variable named XDG_CONFIG_DIRS and XDG_DATA_DIRS respectively, or the
    default defined in the specification if the environment variable is
    unset or empty. Relative paths are ignored, as per the specification.

    xdg_runtime_dir() returns a pathlib.Path object containing the value of
    the XDG_RUNTIME_DIR environment variable, or None if the environment
    variable is not set, or contains a relative path rather than absolute path.

    """

    def _path_from_env(self, variable: str, default: Path) -> Path:
        """Read an environment variable as a path.

        The environment variable with the specified name is read, and its
        value returned as a path. If the environment variable is not set, is
        set to the empty string, or is set to a relative rather than
        absolute path, the default value is returned.

        Parameters
        ----------
        variable : str
            Name of the environment variable.
        default : Path
            Default value.

        Returns
        -------
        Path
            Value from environment or default.

        """
        if (value := self.environment.getenv(variable)) and (path := Path(value)).is_absolute():
            return path
        return default

    def _paths_from_env(self, variable: str, default: list[Path]) -> list[Path]:
        """Read an environment variable as a list of paths.

        The environment variable with the specified name is read, and its
        value split on colons and returned as a list of paths. If the
        environment variable is not set or empty, the default value is returned.
        Relative paths are ignored, as per the specification.

        Parameters
        ----------
        variable : str
            Name of the environment variable.
        default : list[Path]
            Default value.

        Returns
        -------
        list[Path]
            Value from environment or default.
        """
        if value := self.environment.getenv(variable):
            paths = [Path(path) for path in value.split(":") if Path(path).is_absolute()]
            if paths:
                return paths
        return default

    def xdg_config_dirs(self) -> list[Path]:
        """Return a list of Paths corresponding to XDG_CONFIG_DIRS."""
        return self._paths_from_env("XDG_CONFIG_DIRS", [self.file_system.root() / "etc/xdg"])

    def xdg_config_home(self) -> Path:
        """Return a Path corresponding to XDG_CONFIG_HOME."""
        return self._path_from_env("XDG_CONFIG_HOME", self.file_system.home() / ".config")

    def xdg_data_dirs(self) -> list[Path]:
        """Return a list of Paths corresponding to XDG_DATA_DIRS."""
        return self._paths_from_env(
            "XDG_DATA_DIRS", [self.file_system.root() / "usr/local/share/", self.file_system.root() / "usr/share/"]
        )

    def xdg_data_home(self) -> Path:
        """Return a Path corresponding to XDG_DATA_HOME."""
        return self._path_from_env("XDG_DATA_HOME", self.file_system.home() / ".local" / "share")
