# KDE Theme Files

This document provides an overview of KDE theme files, their locations, and how the `kde-colors` tool locates and processes them.

## freedesktop.org Compliance

Except from https://userbase.kde.org/KDE_System_Administration/Environment_Variables

The following environment variables are defined in the freedesktop.org base directory specification and are supported by all XDG-compliant environments and applications, such as KDE.

### XDG_DATA_HOME

Defines the base directory relative to which user specific data files should be stored. If $XDG_DATA_HOME is either not set or empty, a default equal to $HOME/.local/share is used.

### XDG_CONFIG_HOME

Defines the base directory relative to which user specific configuration files should be stored. If $XDG_CONFIG_HOME is either not set or empty, a default equal to $HOME/.config is used.

### XDG_DATA_DIRS

Defines the preference-ordered set of base directories to search for data files in addition to the $XDG_DATA_HOME base directory. The directories in $XDG_DATA_DIRS should be separated with a colon ':'. If $XDG_DATA_DIRS is either not set or empty, a value equal to /usr/local/share/:/usr/share/ is used.

### XDG_CONFIG_DIRS

Defines the preference-ordered set of base directories to search for configuration files in addition to the $XDG_CONFIG_HOME base directory. The directories in $XDG_CONFIG_DIRS should be separated with a colon ':'. If $XDG_CONFIG_DIRS is either not set or empty, a value equal to /etc/xdg is used.

## Current Theme Configuration Locations

The currently active KDE theme is determined by checking several configuration files, in the following order of precedence:

1. `$XDG_CONFIG_HOME/kdedefaults/package` - Contains the theme name directly (e.g., `org.kde.breezedark.desktop`).
2. `$XDG_CONFIG_HOME/kdedefaults/kdeglobals` - Contains theme information in the following keys:
   - `Theme=breeze-dark` - Theme name in the desktoptheme directory
   - `ColorScheme=BreezeDark` - Associated color scheme name
3. `$XDG_CONFIG_HOME/kdeglobals` - Contains the following key:
   - `LookAndFeelPackage=org.kde.breezedark.desktop` - Theme package name
4. `$XDG_CONFIG_HOME/plasmarc` - Contains theme information in the `[Theme]` section:
   - `name=breeze-dark` - Theme name

Example configuration of Breeze Dark theme:

```ini
/home/user/.config/kdedefaults/kdeglobals:Theme=breeze-dark
/home/user/.config/kdedefaults/kdeglobals:ColorScheme=BreezeDark
/home/user/.config/kdedefaults/package:org.kde.breezedark.desktop
/home/user/.config/kdeglobals:LookAndFeelPackage=org.kde.breezedark.desktop
```

Example configuration of Breeze Light theme:

```ini
/home/user/.config/kdedefaults/kdeglobals:Theme=breeze
/home/user/.config/kdedefaults/package:org.kde.breeze.desktop
/home/user/.config/kdedefaults/kdeglobals:ColorScheme=BreezeLight
/home/user/.config/kdeglobals:LookAndFeelPackage=org.kde.breeze.desktop
```

## Theme Directory Structure

A valid KDE theme directory typically contains the following elements:

theme-name/

- metadata.desktop or metadata.json
- colors/ or colors or *.colors

### Theme Identification

A directory is identified as a valid theme if it contains at least one of the following:

1. A valid metadata file:
   - `metadata.desktop` with `Type=Theme` or a Look and Feel section
   - `metadata.json` with theme information

2. Color scheme files:
   - `*.colors` files in the root directory
   - `colors/*.colors` files in a subdirectory
   - A `colors` file with color scheme content

## Theme Metadata

Theme metadata is extracted from either `metadata.desktop` or `metadata.json` files, with `metadata.json` taking precedence when both files exist. The following information is typically included:

- Theme name
- Display name
- Description
- Author
- Version

### metadata.desktop Format

The `metadata.desktop` file uses a standard INI-like format and includes sections like:

```ini
[Desktop Entry]
Name=Theme Name
Comment=Theme description

[KDE]
DefaultTheme=breeze

[X-KDE-PluginInfo]
Author=Theme Author
Version=1.0
```

### metadata.json Format

The `metadata.json` file uses JSON format with a primary `KPlugin` section that contains key theme information:

```json
{
  "KPlugin": {
    "Id": "breeze-dark",
    "Name": "Breeze Dark",
    "Description": "A dark theme for KDE",
    "Author": "KDE Visual Design Group",
    "Version": "1.0"
  }
}
```

### Key Fields

- **KPlugin.Id**: The theme's internal identifier (e.g., "breeze-dark")
- **KPlugin.Name**: The human-readable display name (e.g., "Breeze Dark")

### Theme Name Normalization

When searching for themes, the tool uses a normalization strategy to improve matching between different variations of the same theme name. The normalization process:

1. Converts the name to lowercase
2. Removes all spaces
3. Removes all hyphens

For example, these would all match the same normalized theme "breezedark":

- "Breeze Dark"
- "breeze-dark"
- "BreezeDark"

- Plugin information

### Example metadata.desktop

```ini
[Desktop Entry]
Name=Breeze Dark
Comment=KDE Plasma Theme
X-KDE-PluginInfo-Author=KDE Visual Design Group
X-KDE-PluginInfo-Email=plasma-devel@kde.org
X-KDE-PluginInfo-Name=breeze-dark
X-KDE-PluginInfo-Version=5.0
X-KDE-PluginInfo-Website=https://plasma.kde.org
X-Plasma-API=5.0

[KDE Color Scheme]
ActiveBackground=49,54,59
ActiveForeground=239,240,241
...
```

## Color Files

Color files (`.colors` files) are INI-format files that define color schemes for the KDE environment. They contain sections like:

- `[Colors:View]` - Colors for view backgrounds and text
- `[Colors:Window]` - Colors for window elements
- `[Colors:Button]` - Colors for buttons
- `[Colors:Selection]` - Colors for selected items
- `[Colors:Tooltip]` - Colors for tooltips
- `[WM]` - Colors for window manager elements

### Example color file section

```ini
[Colors:View]
BackgroundAlternate=71,80,87
BackgroundNormal=49,54,59
DecorationFocus=61,174,233
DecorationHover=61,174,233
ForegroundActive=61,174,233
...
```

## Theme Inheritance

Themes can inherit from other themes using the `X-KDE-PluginInfo-Name` property. When a theme inherits from another, missing color values will be taken from the parent theme.

## Theme Discovery Process

The `kde-colors` tool discovers themes through the following process:

1. Collect all search paths (user and system)
2. For each path, check if it's a theme directory
3. If not, recursively search its subdirectories for theme directories
4. Build a mapping of theme names to their file system locations
5. Resolve any theme inheritance
