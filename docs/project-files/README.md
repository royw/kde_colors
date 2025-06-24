# KDE Colors

A CLI tool that helps you discover, explore, and extract color schemes from KDE Plasma desktop themes.

[![CI](https://github.com/royw/kde_colors/actions/workflows/ci.yml/badge.svg)](https://github.com/royw/kde_colors/actions/workflows/ci.yml)
[![Documentation](https://github.com/royw/kde_colors/actions/workflows/docs.yml/badge.svg)](https://royw.github.io/kde_colors/)
[![PyPI version](https://badge.fury.io/py/kde-colors.svg)](https://badge.fury.io/py/kde-colors)
[![codecov](https://codecov.io/gh/royw/kde_colors/branch/main/graph/badge.svg)](https://codecov.io/gh/royw/kde_colors)

## Installation

```bash
pip install kde-colors
```

## Usage

KDE Colors offers several commands to help you discover and explore themes in your KDE Plasma desktop environment:

### List Available Themes

View all available KDE themes on your system:

```bash
kde-colors list
```

Output as JSON:

```bash
kde-colors list --json
```

Save output to a file:

```bash
kde-colors list --output themes.txt
```

### Show Theme Color Details

View details of the currently active theme:

```bash
kde-colors theme
```

View details of a specific theme:

```bash
kde-colors theme "Breeze Dark"
```

Output as JSON:

```bash
kde-colors theme --json
```

### Show Theme File Paths

View paths to theme files:

```bash
kde-colors paths
```

Output as JSON:

```bash
kde-colors paths --json
```

## License

MIT
