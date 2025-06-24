"""Theme loader service implementation module.

This module provides the concrete implementation of the ThemeLoaderInterface responsible for
discovering, loading, and parsing KDE Plasma desktop themes from the file system.

It handles:
- Finding all available themes in standard KDE theme directories
- Loading theme metadata and color information from theme files
- Parsing color values from various formats (RGB strings, hex codes)
- Identifying the currently active theme from KDE configuration

The module uses the dependency injection pattern, requiring a FileSystemInterface
to perform file operations, making it testable and decoupled from direct file system access.
"`cached_property` decorators are used to optimize performance by caching expensive
file system operations results.
"""

from __future__ import annotations

import configparser
from functools import cached_property
from pathlib import Path
from typing import Any

from loguru import logger

from kde_colors.interfaces.file_system import FileSystemInterface
from kde_colors.interfaces.theme_loader import ThemeLoaderInterface
from kde_colors.interfaces.xdg import XDGInterface


class ThemeLoader(ThemeLoaderInterface):
    # KDE config file containing the current theme name
    # Config file names and keys
    KDEDEFAULTS_PACKAGE_FILE = "kdedefaults/package"
    KDEDEFAULTS_KDEGLOBALS_FILE = "kdedefaults/kdeglobals"
    KDEGLOBALS_FILE = "kdeglobals"
    PLASMA_CONFIG_FILE = "plasmarc"

    # Config keys
    THEME_KEY = "Theme"
    LOOK_AND_FEEL_KEY = "LookAndFeelPackage"
    PLASMA_THEME_CONFIG_KEY = "Theme"
    PLASMA_THEME_NAME_KEY = "name"

    def __init__(self, file_system: FileSystemInterface, xdg: XDGInterface) -> None:
        self.file_system = file_system
        self.xdg = xdg

    def load(self, theme_name: str) -> Any | None:
        """Load a theme from the given theme name."""
        normalized_theme_name = self._normalize(theme_name)
        themes = self.load_themes()
        for theme in themes:
            if themes[theme]["Normalized Name"] == normalized_theme_name:
                return themes[theme]
        return None

    @cached_property
    def _themes_cache(self) -> dict[str, Any]:
        """Cached property for themes to avoid repeated file system access."""
        return self._load_themes_impl()

    def load_themes(self) -> dict[str, Any]:
        """
        Load all available themes.

        The output dictionary should look like:

        {
            "Theme Name": {
                "Name": "Theme Name",
                "Id": "theme-name",
                "Normalized Name": "themename",
                "Package": "org.kde.themename.desktop",
                "Path": "/usr/share/plasma/desktoptheme/Theme Name"
                "Colors": {
                    "[Colors:View]": ...
                }
            },
            ...
        }

        Returns:
            A dictionary of theme information
        """
        # Use the cached property but allow for cache refreshing when explicitly called
        return self._themes_cache

    def _load_themes_impl(self) -> dict[str, Any]:
        """Implementation for theme loading logic."""
        theme_paths = self._get_theme_paths_impl()
        themes: dict[str, Any] = {}
        current_theme_name = self.get_current_theme()

        for path in theme_paths:
            theme_name = path.name
            normalized_name = self._normalize(theme_name)
            theme_id = theme_name.lower().replace(" ", "-")
            package_name = f"org.kde.{normalized_name}.desktop"

            # Load colors from the theme directory
            colors = self._load_theme_colors(path)
            if not colors:
                # Skip themes with no colors
                continue

            # Determine if this is the current theme
            is_current = current_theme_name and self._normalize(current_theme_name) == normalized_name

            themes[theme_name] = {
                "Name": theme_name,
                "Id": theme_id,
                "Normalized Name": normalized_name,
                "Package": package_name,
                "Path": str(path),
                "Colors": colors,
                "current": is_current,
            }

        return themes

    def _load_theme_colors(self, theme_path: Path) -> dict[str, Any] | None:
        """
        Load colors from a theme directory following the hierarchy in color-files.md.

        1. Check for named color scheme files in colors/{scheme_name}.colors
        2. Check for root colors file in the theme directory
        3. Check for nested colors file in colors/colors
        4. Extract from metadata as fallback (not implemented yet)

        Args:
            theme_path: Path to the theme directory

        Returns:
            Dictionary with color data or None if no colors found
        """
        colors_data: dict[str, Any] = {}
        theme_path_str = str(theme_path)

        # First check for named color scheme files
        colors_dir = f"{theme_path_str}/colors"
        if self.file_system.exists(colors_dir) and self.file_system.is_dir(colors_dir):
            try:
                color_files = self.file_system.glob(f"{colors_dir}/*.colors")
                if color_files:
                    # Use the first .colors file found
                    colors_data = self._parse_colors_file(color_files[0])
                    if colors_data:
                        return colors_data
            except Exception:
                logger.debug("Failed to parse colors files ({})", color_files, exc_info=True)

        # Next check for root colors file
        root_colors_file = f"{theme_path_str}/colors"
        if self.file_system.exists(root_colors_file) and self.file_system.is_file(root_colors_file):
            colors_data = self._parse_colors_file(root_colors_file)
            if colors_data:
                return colors_data

        # Then check for nested colors file
        nested_colors_file = f"{colors_dir}/colors"
        if self.file_system.exists(nested_colors_file) and self.file_system.is_file(nested_colors_file):
            colors_data = self._parse_colors_file(nested_colors_file)
            if colors_data:
                return colors_data

        # As a last resort, we might try in the future to extract colors from metadata
        logger.debug("Failed to parse colors from theme ({})", theme_path)

        return None

    def _parse_colors_file(self, colors_file_path: str) -> dict[str, Any]:
        """
        Parse a KDE colors file (INI format with sections and key-value pairs).

        Args:
            colors_file_path: Path to the colors file as a string

        Returns:
            Dictionary with parsed color data
        """
        try:
            if not self.file_system.exists(colors_file_path) or not self.file_system.is_file(colors_file_path):
                return {}

            # Read the file content
            file_content = self.file_system.read_file(colors_file_path)

            # Parse the INI content using configparser
            config = configparser.ConfigParser()
            config.read_string(file_content)

            result: dict[str, Any] = {}

            for section in config.sections():
                # Type the section data dictionary to accept either strings or lists
                section_data: dict[str, str | list[int]] = {}
                for key, value in config[section].items():
                    parsed_value = self._parse_color_value(value)
                    section_data[key] = parsed_value

                result[section] = section_data

            return result

        except Exception:
            # Log the error or handle it appropriately
            logger.error("Failed to parse colors file ({})", colors_file_path, exc_info=True)
            return {}

    def _parse_color_value(self, value: str) -> str | list[int]:
        """
        Parse a color value which could be in several formats:
        - RGB comma-separated integers: "255,255,255"
        - Hex color: "#FFFFFF" or "#ffffff"
        - Named colors or other string values

        Args:
            value: The color value string to parse

        Returns:
            Either a list of RGB integers or the original string
        """
        # Check if it's a comma-separated RGB value
        if "," in value and all(part.strip().isdigit() for part in value.split(",")):
            return [int(part.strip()) for part in value.split(",")]

        # Try to parse hex color values
        if value.startswith("#") and len(value) in (7, 9):  # #RRGGBB or #RRGGBBAA
            try:
                # Remove the # prefix
                hex_value = value[1:]

                # Parse the RGB components
                if len(hex_value) >= 6:  # At least RGB components
                    r = int(hex_value[0:2], 16)
                    g = int(hex_value[2:4], 16)
                    b = int(hex_value[4:6], 16)
                    return [r, g, b]
            except ValueError:
                # If parsing fails, return the original string
                logger.debug("Failed to parse hex color ({})", value, exc_info=True)

        # Return the original value if no conversion applied
        return value

    def _normalize(self, name: str) -> str:
        """Normalize the theme name."""
        return name.lower().replace(" ", "").replace("-", "")

    def get_current_theme(self) -> str | None:
        """
                Get the name of the current active KDE theme.

                Checks configuration files in the following order of precedence:
        {{ ... }}
                1. $XDG_CONFIG_HOME/kdedefaults/package
                2. $XDG_CONFIG_HOME/kdedefaults/kdeglobals
                3. $XDG_CONFIG_HOME/kdeglobals
                4. $XDG_CONFIG_HOME/plasmarc

                Returns:
                    The current theme name or None if not found
        """
        config_home = self.xdg.xdg_config_home()
        logger.debug("config_home: {}", config_home)

        # Check configuration files in order of precedence
        theme_name = self._check_kdedefaults_package(config_home)
        logger.debug("theme_name: {}", theme_name)
        if theme_name:
            return theme_name

        theme_name = self._check_kdedefaults_kdeglobals(config_home)
        logger.debug("theme_name: {}", theme_name)
        if theme_name:
            return theme_name

        theme_name = self._check_kdeglobals(config_home)
        logger.debug("theme_name: {}", theme_name)
        if theme_name:
            return theme_name

        theme_name = self._check_plasmarc([config_home, *self.xdg.xdg_config_dirs()])
        logger.debug("theme_name: {}", theme_name)
        if theme_name:
            return theme_name

        return None

    def _check_kdedefaults_package(self, config_home: Path) -> str | None:
        """Check the kdedefaults/package file for theme name."""
        package_path = config_home / self.KDEDEFAULTS_PACKAGE_FILE
        if not (self.file_system.exists(str(package_path)) and self.file_system.is_file(str(package_path))):
            return None

        try:
            content = self.file_system.read_file(str(package_path))
            # File contains the package name directly (e.g. org.kde.breezedark.desktop)
            package_name = content.strip()
            if not package_name:
                return None

            return self._extract_theme_from_package(package_name)
        except Exception:
            logger.debug("Failed to parse package file ({})", package_path, exc_info=True)
            return None

    def _check_kdedefaults_kdeglobals(self, config_home: Path) -> str | None:
        """Check the kdedefaults/kdeglobals file for theme name."""
        kdeglobals_path = config_home / self.KDEDEFAULTS_KDEGLOBALS_FILE
        if not (self.file_system.exists(str(kdeglobals_path)) and self.file_system.is_file(str(kdeglobals_path))):
            return None

        try:
            content = self.file_system.read_file(str(kdeglobals_path))
            config = configparser.ConfigParser()
            config.read_string(content)

            # Look for Theme key in the [KDE] or [General] section
            for section in ["KDE", "General"]:
                if section in config and self.THEME_KEY in config[section]:
                    return config[section][self.THEME_KEY]
            return None
        except Exception:
            logger.debug("Failed to parse kdedefaults/kdeglobals file ({})", kdeglobals_path, exc_info=True)
            return None

    def _check_kdeglobals(self, config_home: Path) -> str | None:
        """Check the kdeglobals file for theme name."""
        kdeglobals_path = config_home / self.KDEGLOBALS_FILE
        if not (self.file_system.exists(str(kdeglobals_path)) and self.file_system.is_file(str(kdeglobals_path))):
            return None

        try:
            content = self.file_system.read_file(str(kdeglobals_path))
            config = configparser.ConfigParser()
            config.read_string(content)

            # Look for LookAndFeelPackage key in the [KDE] section
            if "KDE" in config and self.LOOK_AND_FEEL_KEY in config["KDE"]:
                package_name = config["KDE"][self.LOOK_AND_FEEL_KEY]
                return self._extract_theme_from_package(package_name)
            return None
        except Exception:
            logger.debug("Failed to parse kdeglobals file ({})", kdeglobals_path, exc_info=True)
            return None

    def _check_plasmarc(self, config_dirs: list[Path]) -> str | None:
        """Check the plasmarc file for theme name."""
        for config_dir in config_dirs:
            config_file = config_dir / self.PLASMA_CONFIG_FILE
            config_path = str(config_file)

            if not (self.file_system.exists(config_path) and self.file_system.is_file(config_path)):
                continue

            try:
                content = self.file_system.read_file(config_path)
                config = configparser.ConfigParser()
                config.read_string(content)

                # Get the theme name from the config
                if (
                    self.PLASMA_THEME_CONFIG_KEY in config
                    and self.PLASMA_THEME_NAME_KEY in config[self.PLASMA_THEME_CONFIG_KEY]
                ):
                    return config[self.PLASMA_THEME_CONFIG_KEY][self.PLASMA_THEME_NAME_KEY]
            except Exception:
                logger.debug("Failed to parse plasmarc file ({})", config_path, exc_info=True)

        return None

    def _extract_theme_from_package(self, package_name: str) -> str | None:
        """Extract theme name from package name (e.g., org.kde.breezedark.desktop)."""
        theme_parts = package_name.split(".")
        if len(theme_parts) >= 3:
            # Convert org.kde.breezedark.desktop to breeze-dark
            theme_name = theme_parts[2].replace("desktop", "").strip(".")
            return theme_name.replace("dark", "-dark")
        return None

    def _get_theme_paths_impl(self) -> list[Path]:
        """
        Get the paths to theme directories that contain color data.

        Searches both XDG config paths and XDG data paths for plasma themes.
        Only includes directories that exist and contain a 'colors' file.

        Returns:
            A list of Path objects pointing to valid theme directories
        """
        theme_paths: list[Path] = []

        # Check XDG config paths first (e.g., ~/.config, /etc/xdg)
        config_paths = [self.xdg.xdg_config_home(), *self.xdg.xdg_config_dirs()]
        for config_path in config_paths:
            plasma_theme_dir_path = str(config_path / "plasma" / "desktoptheme")
            if self.file_system.exists(plasma_theme_dir_path) and self.file_system.is_dir(plasma_theme_dir_path):
                theme_paths.extend(self._find_valid_theme_dirs(Path(plasma_theme_dir_path)))

        # Check XDG data paths next (e.g., ~/.local/share, /usr/share)
        data_dirs = self.xdg.xdg_data_dirs()
        data_home = self.xdg.xdg_data_home()

        # Add data_home first since it takes precedence
        if data_home not in data_dirs:
            data_dirs.insert(0, data_home)

        for data_dir in data_dirs:
            plasma_theme_dir_path = f"{data_dir}/plasma/desktoptheme"
            if self.file_system.exists(plasma_theme_dir_path) and self.file_system.is_dir(plasma_theme_dir_path):
                theme_paths.extend(self._find_valid_theme_dirs(Path(plasma_theme_dir_path)))

        return theme_paths

    def _find_valid_theme_dirs(self, parent_dir: Path) -> list[Path]:
        """
        Find valid theme directories under the given parent directory.

        A valid theme directory must contain color files in one of the following locations:
        1. Named color scheme file (colors/{scheme_name}.colors)
        2. Root colors file (colors in the theme directory root)
        3. Nested colors file (colors/colors)
        4. Theme metadata as fallback (not checked here)

        See docs/color-files.md for details.

        Args:
            parent_dir: The parent directory to search in

        Returns:
            A list of valid theme directory paths
        """
        valid_dirs: list[Path] = []
        parent_dir_str = str(parent_dir)

        try:
            # List all entries in the parent directory
            dir_entries = self.file_system.list_dir(parent_dir_str)

            for entry in dir_entries:
                child_path = f"{parent_dir_str}/{entry}"

                # Check if it's a directory
                if self.file_system.is_dir(child_path):
                    # Check for root colors file (most common)
                    root_colors_file = f"{child_path}/colors"

                    # Check for nested colors file
                    nested_colors_dir = f"{child_path}/colors"
                    nested_colors_file = f"{nested_colors_dir}/colors"

                    # Check for any *.colors files in the colors directory
                    has_colors_files = False
                    if self.file_system.exists(nested_colors_dir) and self.file_system.is_dir(nested_colors_dir):
                        try:
                            colors_files = self.file_system.glob(f"{nested_colors_dir}/*.colors")
                            has_colors_files = len(colors_files) > 0
                        except Exception:
                            logger.debug("Failed to access directory ({})", child_path, exc_info=True)

                    # If any of the conditions are met, consider it a valid theme directory
                    if (
                        (self.file_system.exists(root_colors_file) and self.file_system.is_file(root_colors_file))
                        or (
                            self.file_system.exists(nested_colors_file)
                            and self.file_system.is_file(nested_colors_file)
                        )
                        or has_colors_files
                    ):
                        valid_dirs.append(Path(child_path))

        except Exception:
            # Silently skip directories we can't access
            logger.debug("Skipping.  Failed to access directory ({})", child_path, exc_info=True)

        return valid_dirs
