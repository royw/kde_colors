# KDE Theme Colors - User Guide

KDE Theme Colors is a command-line tool that extracts color schemes from KDE Plasma desktop themes. This guide explains how to use the CLI, including all available commands, options, and output formats.

## Installation

```bash
pip install kde-colors
```

## Basic Usage

The basic syntax for the KDE Theme Colors CLI is:

```bash
kde-colors [GLOBAL OPTIONS] COMMAND [COMMAND OPTIONS]
```

## Global Options

These options can be used with any command:

| Option | Description |
|--------|-------------|
| `-v`, `--verbose` | Increase verbosity level. Can be specified multiple times for more detail (e.g., `-vv` for debug level). |
| `--version` | Show the version number and exit. |
| `-h`, `--help` | Show help message and exit. |

## Commands

### List Command

Lists all available KDE themes installed on the system.

```bash
kde-colors list [OPTIONS]
```

#### List Options

| Option | Description |
|--------|-------------|
| `-f`, `--format {text,json}` | Output format (default: json) |
| `-o`, `--output PATH` | Write output to the specified file instead of stdout |

#### List Example

```bash
# List all themes in text format
kde-colors list --format text

# Save the list of themes to a file in JSON format
kde-colors list --output themes.json
```

#### List Output

**Text Format**:

```text
Available desktop themes (current theme marked with *):
  oxygen
* breeze-dark
  kubuntu
  default
  breeze-light
```

**JSON Format**:

```json
{
  "current_theme": "Breeze",
  "themes": [
    {
      "name": "Breeze",
      "display_name": "Breeze",
      "description": "Default KDE theme"
    },
    {
      "name": "BreezeDark",
      "display_name": "Breeze Dark",
      "description": "Dark version of Breeze"
    },
    ...
  ]
}
```

### Paths Command

Shows the system paths where KDE searches for theme files.

```bash
kde-colors paths [OPTIONS]
```

#### Paths Options

| Option | Description |
|--------|-------------|
| `-f`, `--format {text,json}` | Output format (default: json) |
| `-o`, `--output PATH` | Write output to the specified file instead of stdout |

#### Paths Example

```bash
# View theme paths in text format
kde-colors paths --format text
```

#### Paths Output

**Text Format**:

```text
KDE Theme Search Paths:
- System-wide: /usr/share/plasma/desktoptheme
- User-specific: /home/username/.local/share/plasma/desktoptheme
...
```

**JSON Format**:

```json
{
  "theme_paths": [
    {
      "type": "system",
      "path": "/usr/share/plasma/desktoptheme"
    },
    {
      "type": "user",
      "path": "/home/username/.local/share/plasma/desktoptheme"
    },
    ...
  ]
}
```

### Theme Command

Extracts colors from the specified KDE theme. If no theme name is provided, information about the current theme is displayed.

```bash
kde-colors theme [THEME_NAME] [OPTIONS]
```

#### Theme Arguments

| Argument | Description |
|----------|-------------|
| `THEME_NAME` | (Optional) Name of the theme to extract colors from. If not specified, the current theme will be used. |

#### Theme Options

| Option | Description |
|--------|-------------|
| `-f`, `--format {text,json}` | Output format (default: json) |
| `-o`, `--output PATH` | Write output to the specified file instead of stdout |

#### Theme Example

```bash
# Extract colors from the Breeze theme in text format
kde-colors theme Breeze --format text

# Extract colors from the Breeze Dark theme and save as JSON
kde-colors theme "Breeze Dark" --output breeze-dark-colors.json

# Extract colors from the current theme
kde-colors theme
```

#### Theme Output

**Text Format**:

```text
Theme: Breeze (Breeze)
Author: KDE Visual Design Group
Version: 1.0
Description: KDE's default theme
Path: /usr/share/plasma/desktoptheme/Breeze

Colors:
  [Colors:View]
    BackgroundNormal: #fcfcfc
    BackgroundAlternate: #eff0f1
    ForegroundNormal: #232629
    ForegroundInactive: #7f8c8d
    ...

  [Colors:Window]
    BackgroundNormal: #eff0f1
    BackgroundAlternate: #e3e5e7
    ...
```

**JSON Format**:

```json
{
  "theme": {
    "name": "Breeze",
    "display_name": "Breeze",
    "author": "KDE Visual Design Group",
    "version": "1.0",
    "description": "KDE's default theme",
    "path": "/usr/share/plasma/desktoptheme/Breeze"
  },
  "colors": {
    "Colors:View": {
      "BackgroundNormal": "#fcfcfc",
      "BackgroundAlternate": "#eff0f1",
      "ForegroundNormal": "#232629",
      "ForegroundInactive": "#7f8c8d"
    },
    "Colors:Window": {
      "BackgroundNormal": "#eff0f1",
      "BackgroundAlternate": "#e3e5e7"
    },
    ...
  }
}
```

## Exit Codes

The CLI uses the following exit codes to indicate the result of the operation:

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Theme not found |
| 4 | I/O error |

## Examples

### Extract Colors from Current Theme

```bash
kde-colors theme current --format text
```

### Find the Current Theme

```bash
kde-colors list --format text | grep "(current)"
```

### Extract Colors and Format with jq

```bash
kde-colors theme Breeze | jq '.colors."Colors:View"'
```

### List All Dark Themes

```bash
kde-colors list | jq '.themes[] | select(.name | contains("Dark"))'
```

## Troubleshooting

### Common Issues

1. **Theme not found**
   - Check if the theme name is correct (use `kde-colors list` to verify)
   - Theme names are case-sensitive
   - Use quotes for theme names with spaces: `kde-colors theme "Breeze Dark"`

2. **Permission errors**
   - Ensure you have read access to KDE theme directories
   - For writing output files, ensure you have write permission to the target directory

3. **Invalid output format**
   - Only `text` and `json` formats are supported
   - Check for typos in the format option

If you encounter any issues, increase verbosity with `-v` or `-vv` to get more information about the error.
