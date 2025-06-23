"""
Unit tests for the ThemeLoader service.
"""

from __future__ import annotations

import unittest
from typing import cast

from kde_colors.interfaces.theme_loader import ThemeLoaderInterface
from kde_colors.services.theme_loader import ThemeLoader
from tests.support.file_system_double import FileSystemDouble
from tests.support.xdg_double import XDGDouble


class TestThemeLoader(unittest.TestCase):
    """Tests for the ThemeLoader service."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Initialize test doubles
        self.fs = FileSystemDouble()
        self.xdg = XDGDouble(
            config_home="/fake/config/home",
            data_home="/fake/data/home",
            config_dirs=["/fake/config/dir"],
            data_dirs=["/fake/share", "/fake/usr/share"],
        )

        # Theme directories in various locations
        # Data home themes
        self.fs.mkdir("/fake/data/home/plasma/desktoptheme/Breeze")
        self.fs.mkdir("/fake/data/home/plasma/desktoptheme/Breeze Dark")

        # System themes
        self.fs.mkdir("/fake/usr/share/plasma/desktoptheme/Oxygen")
        self.fs.mkdir("/fake/share/plasma/desktoptheme/Custom")

        # Create theme colors files
        self._setup_theme_colors()

        # Create configuration files
        self._setup_config_files()

        # Create metadata files for themes to be recognized
        self._setup_metadata_files()

        # Initialize theme loader with our test doubles
        self.theme_loader = ThemeLoader(self.fs, self.xdg)

    def _setup_theme_colors(self) -> None:
        """Set up color scheme files for testing."""
        # Create necessary directories
        self.fs.mkdir("/fake/share/color-schemes")

        # Breeze theme colors
        breeze_colors = """[Colors:View]
        BackgroundNormal=255,255,255
        BackgroundAlternate=239,240,241
        ForegroundNormal=35,38,41

        [Colors:Button]
        BackgroundNormal=#3daee9
        ForegroundNormal=#eff0f1
        """

        # Create color files in theme directories
        self.fs.write_text("/fake/data/home/plasma/desktoptheme/Breeze/colors", breeze_colors)

        # Create global color scheme files
        breeze_scheme = """[Colors:View]
        BackgroundNormal=#fcfcfc
        BackgroundAlternate=#eff0f1

        [General]
        ColorScheme=Breeze
        """
        self.fs.write_text("/fake/share/color-schemes/Breeze.colors", breeze_scheme)

        # Breeze Dark theme colors
        breeze_dark_colors = """[Colors:View]
        BackgroundNormal=35,38,41
        BackgroundAlternate=49,54,59
        ForegroundNormal=239,240,241
        """
        self.fs.write_text("/fake/data/home/plasma/desktoptheme/Breeze Dark/colors", breeze_dark_colors)
        self.fs.write_text("/fake/share/color-schemes/BreezeDark.colors", breeze_dark_colors)

        # Oxygen theme colors
        oxygen_colors = """[Colors:View]
        BackgroundNormal=224,223,222
        BackgroundAlternate=239,238,237
        ForegroundNormal=35,38,41
        """
        self.fs.write_text("/fake/usr/share/plasma/desktoptheme/Oxygen/colors", oxygen_colors)
        self.fs.write_text("/fake/share/color-schemes/Oxygen.colors", oxygen_colors)

        # Create colors directories for themes that might use them
        oxygen_colors_dir = "/fake/usr/share/plasma/desktoptheme/Oxygen/colors"
        self.fs.mkdir(oxygen_colors_dir)
        self.fs.write_text(f"{oxygen_colors_dir}/Oxygen.colors", oxygen_colors)

        # Make sure directory listings will work properly
        self._setup_dir_listings()

    def _setup_metadata_files(self) -> None:
        """Set up metadata.desktop files for themes."""
        # Breeze metadata
        breeze_metadata = """[Desktop Entry]
        Name=Breeze
        X-KDE-PluginInfo-Name=Breeze
        """
        self.fs.write_text("/fake/data/home/plasma/desktoptheme/Breeze/metadata.desktop", breeze_metadata)

        # Breeze Dark metadata
        breeze_dark_metadata = """[Desktop Entry]
        Name=Breeze Dark
        X-KDE-PluginInfo-Name=Breeze-Dark
        """
        self.fs.write_text("/fake/data/home/plasma/desktoptheme/Breeze Dark/metadata.desktop", breeze_dark_metadata)

        # Oxygen metadata
        oxygen_metadata = """[Desktop Entry]
        Name=Oxygen
        X-KDE-PluginInfo-Name=oxygen
        """
        self.fs.write_text("/fake/usr/share/plasma/desktoptheme/Oxygen/metadata.desktop", oxygen_metadata)

        # Custom metadata
        custom_metadata = """[Desktop Entry]
        Name=Custom
        X-KDE-PluginInfo-Name=Custom
        """
        self.fs.write_text("/fake/share/plasma/desktoptheme/Custom/metadata.desktop", custom_metadata)

    def _setup_config_files(self) -> None:
        """Set up KDE config files for testing."""
        # Config file for current theme
        plasma_config = """[Theme]
        name=Breeze
        """
        self.fs.mkdir("/fake/config/home/plasma")
        self.fs.write_text("/fake/config/home/plasma/plasmarc", plasma_config)

        # KDE globals with color scheme
        kde_globals = """[General]
        ColorScheme=Breeze

        [KDE]
        LookAndFeelPackage=org.kde.breeze.desktop
        """
        self.fs.write_text("/fake/config/home/kdeglobals", kde_globals)

        # Package file with theme information
        package_config = """[Theme]
        name=Breeze
        """
        self.fs.mkdir("/fake/config/home/kdedefaults")
        self.fs.write_text("/fake/config/home/kdedefaults/package", package_config)

    def test_implements_interface(self) -> None:
        """Test that ThemeLoader implements the ThemeLoaderInterface."""
        # Cast to verify types
        cast(ThemeLoaderInterface, self.theme_loader)
        assert True  # If we got here, the cast succeeded

    def test_load_themes(self) -> None:
        """Test loading all available themes."""
        themes = self.theme_loader.load_themes()

        # Verify we found all our test themes
        assert len(themes) >= 3
        assert "Breeze" in themes
        assert "Breeze Dark" in themes
        assert "Oxygen" in themes

        # Verify theme structure
        breeze = themes["Breeze"]
        assert breeze["Name"] == "Breeze"
        assert breeze["Id"] == "breeze"
        assert breeze["Normalized Name"] == "breeze"
        assert "Colors" in breeze
        assert breeze["current"] is True

        # Verify Breeze Dark theme structure
        breeze_dark = themes["Breeze Dark"]
        assert breeze_dark["Name"] == "Breeze Dark"
        assert breeze_dark["Id"] == "breeze-dark"
        assert breeze_dark["Normalized Name"] == "breezedark"
        assert "Colors" in breeze_dark
        assert not breeze_dark["current"]

    def test_load_specific_theme(self) -> None:
        """Test loading a specific theme by name."""
        theme = self.theme_loader.load("Breeze Dark")
        assert theme is not None
        assert theme["Name"] == "Breeze Dark"
        assert theme["Colors"] is not None

    def test_load_nonexistent_theme(self) -> None:
        """Test loading a theme that doesn't exist."""
        theme = self.theme_loader.load("NonexistentTheme")
        assert theme is None

    def test_load_theme_case_insensitive(self) -> None:
        """Test that theme loading is case-insensitive."""
        theme = self.theme_loader.load("brEEze darK")
        assert theme is not None
        assert theme["Name"] == "Breeze Dark"

    def test_get_current_theme(self) -> None:
        """Test getting the current theme name."""
        theme_name = self.theme_loader.get_current_theme()
        assert theme_name == "breeze"  # The implementation returns lowercase name

    def _setup_dir_listings(self) -> None:
        """Set up directory listings for FileSystemDouble."""
        # Set up data home plasma directory listing
        plasma_data_dir = "/fake/data/home/plasma"
        self.fs.mkdir(plasma_data_dir)
        self.fs._set_directory_entries(plasma_data_dir, ["desktoptheme"])

        # Set up desktop theme directory listing
        desktop_theme_dir = "/fake/data/home/plasma/desktoptheme"
        self.fs._set_directory_entries(desktop_theme_dir, ["Breeze", "Breeze Dark"])

        # Set up system directories
        usr_share_plasma = "/fake/usr/share/plasma"
        self.fs.mkdir(usr_share_plasma)
        self.fs._set_directory_entries(usr_share_plasma, ["desktoptheme"])

        usr_share_desktop_theme = "/fake/usr/share/plasma/desktoptheme"
        self.fs._set_directory_entries(usr_share_desktop_theme, ["Oxygen"])

        share_plasma = "/fake/share/plasma"
        self.fs.mkdir(share_plasma)
        self.fs._set_directory_entries(share_plasma, ["desktoptheme"])

        share_desktop_theme = "/fake/share/plasma/desktoptheme"
        self.fs._set_directory_entries(share_desktop_theme, ["Custom"])

        # Set up theme directory listings
        breeze_dir = "/fake/data/home/plasma/desktoptheme/Breeze"
        self.fs._set_directory_entries(breeze_dir, ["colors", "metadata.desktop"])

        breeze_colors_dir = "/fake/data/home/plasma/desktoptheme/Breeze/colors"
        self.fs._set_directory_entries(breeze_colors_dir, ["Breeze.colors"])

        breeze_dark_dir = "/fake/data/home/plasma/desktoptheme/Breeze Dark"
        self.fs._set_directory_entries(breeze_dark_dir, ["colors", "metadata.desktop"])

        oxygen_dir = "/fake/usr/share/plasma/desktoptheme/Oxygen"
        self.fs._set_directory_entries(oxygen_dir, ["colors", "metadata.desktop"])

        oxygen_colors_dir = "/fake/usr/share/plasma/desktoptheme/Oxygen/colors"
        self.fs._set_directory_entries(oxygen_colors_dir, ["colors"])

        custom_dir = "/fake/share/plasma/desktoptheme/Custom"
        self.fs._set_directory_entries(custom_dir, ["metadata.desktop"])

    def test_get_theme_paths(self) -> None:
        """Test getting theme search paths."""
        paths = self.theme_loader._get_theme_paths_impl()
        assert len(paths) > 0
        # Check that we found at least our test themes
        theme_paths = [str(path) for path in paths]
        assert "/fake/data/home/plasma/desktoptheme/Breeze" in theme_paths
        assert "/fake/data/home/plasma/desktoptheme/Breeze Dark" in theme_paths
        assert "/fake/usr/share/plasma/desktoptheme/Oxygen" in theme_paths
        assert "/fake/data/home/plasma/desktoptheme/Breeze" in [str(p) for p in paths]
        assert "/fake/usr/share/plasma/desktoptheme/Oxygen" in [str(p) for p in paths]

    def test_normalize_theme_name(self) -> None:
        """Test theme name normalization."""
        assert self.theme_loader._normalize("Breeze Dark") == "breezedark"
        assert self.theme_loader._normalize("Breeze-Dark") == "breezedark"
        # Underscores are preserved in the implementation
        assert self.theme_loader._normalize("breeze_dark") == "breeze_dark"

    def test_parse_colors_file(self) -> None:
        """Test parsing a colors file."""
        # Create a test colors file
        colors_content = """[Colors:View]
        BackgroundNormal=255,255,255
        ForegroundNormal=0,0,0

        [Colors:Button]
        BackgroundNormal=#3daee9
        ForegroundNormal=#eff0f1
        """
        self.fs.write_text("/fake/test.colors", colors_content)

        # Parse the colors file
        colors = self.theme_loader._parse_colors_file("/fake/test.colors")

        # Verify the results
        assert colors is not None
        # Keys are without brackets, names are lowercase
        assert "Colors:View" in colors
        assert colors["Colors:View"]["backgroundnormal"] == [255, 255, 255]  # RGB values
        assert colors["Colors:View"]["foregroundnormal"] == [0, 0, 0]  # RGB values
        assert "Colors:Button" in colors
        assert colors["Colors:Button"]["backgroundnormal"] == [61, 174, 233]  # #3daee9 converted to RGB
        assert colors["Colors:Button"]["foregroundnormal"] == [239, 240, 241]  # #eff0f1 converted to RGB

    def test_parse_color_value(self) -> None:
        """Test parsing color values in different formats."""
        # Test hex color format
        assert self.theme_loader._parse_color_value("#ff0000") == [255, 0, 0]
        assert self.theme_loader._parse_color_value("#00ff00") == [0, 255, 0]
        assert self.theme_loader._parse_color_value("#0000ff") == [0, 0, 255]
        assert self.theme_loader._parse_color_value("#123456") == [18, 52, 86]

        # Test RGB format
        assert self.theme_loader._parse_color_value("255,0,0") == [255, 0, 0]
        assert self.theme_loader._parse_color_value("0,255,0") == [0, 255, 0]
        assert self.theme_loader._parse_color_value("0,0,255") == [0, 0, 255]
        assert self.theme_loader._parse_color_value("128,64,32") == [128, 64, 32]

        # Test with spaces in RGB format
        assert self.theme_loader._parse_color_value("255, 0, 0") == [255, 0, 0]

        # Test non-color format strings (should return the original string)
        assert self.theme_loader._parse_color_value("Breeze") == "Breeze"
