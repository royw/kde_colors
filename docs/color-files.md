# KDE Theme Color Files

This document describes how color files are located and processed in the KDE Theme Colors project.

## Color File Locations

KDE Theme Colors looks for color scheme files in several locations, checked in the following order:

1. **Named Color Scheme File**: If a theme specifies a color scheme name, it will check for `colors/{scheme_name}.colors` in the theme directory.
2. **Root Colors File**: A file named `colors` in the root of the theme directory.
3. **Nested Colors File**: A file named `colors` in the `colors/` subdirectory of the theme directory (`colors/colors`).
4. **Theme Metadata**: As a fallback, colors may be extracted from the theme's metadata.

## Color File Format

KDE color scheme files use an INI-like format with sections and key-value pairs:

```ini
[Colors:View]
BackgroundNormal=20,22,24
ForegroundNormal=239,240,241

[Colors:Window]
BackgroundNormal=49,54,59
ForegroundNormal=239,240,241

[General]
ColorScheme=ThemeName
```

### Sections and Keys

- Sections are defined by square brackets `[Section Name]`
- Each section contains key-value pairs separated by `=`
- Color values are typically represented as comma-separated RGB values (0-255)
- The `[General]` section may contain a `ColorScheme` key that specifies the name of the color scheme

### Comments and Whitespace

- Lines beginning with `#` are treated as comments and ignored
- Inline comments (starting with `#`) after a value are also supported
- Empty lines and extra whitespace are ignored
- Leading and trailing whitespace around keys and values is trimmed

### Case Sensitivity

- Section names are treated as case-sensitive (e.g., `[Colors:View]` vs `[colors:view]`)
- Keys are treated as case-insensitive (e.g., `BackgroundNormal` is equivalent to `backgroundnormal`)
- This is due to the use of `configparser` which lowercases keys but preserves section names

## Processing of Color Files

1. The loader attempts to read a color file from one of the locations listed above
2. The file is parsed using Python's `configparser` module
3. Sections and keys are extracted and organized into a structured dictionary
4. The color scheme name is extracted from the `[General]` section if available
5. The parsed colors are added to the theme's color dictionary
6. If a color scheme name is found in the file, it is set as the theme's `color_scheme` property

## Error Handling

- If a color file is missing or unreadable, the loader tries the next location
- If a color file is malformed, it is skipped with a warning
- If no colors are found in any location, the theme's colors remain empty
- Debug logging provides detailed information about the color loading process

## Testing with Color Files

When creating test cases for color loading:

- Ensure test color files follow the format described above
- Remember that keys will be lowercased by the parser, so use case-insensitive checks in tests
- Use the test doubles (`FakeFileSystem` and `FakeFileHandle`) for file operations
- For integration tests, place real color files in the appropriate test directories
