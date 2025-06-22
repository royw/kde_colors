# Source Code Rules

This document outlines specific rules derived from the Software Design Document (SDD) to guide the implementation of source code for the KDE Theme Colors tool. Following these rules will ensure the code adheres to the design specifications and architectural principles.

## Architecture Rules

1. **Layered Architecture**:
   - Maintain strict separation between the CLI, Service, Interface, and Data Access layers.
   - Avoid direct dependencies between layers that aren't adjacent.
   - Use interfaces (protocols) to define contracts between layers.

2. **Component Organization**:
   - Organize code into clearly defined modules:
     - CLI module: Command-line interface
     - Services module: Core functionality
     - Interfaces module: Protocol definitions
   - Each module should focus on a single responsibility.

3. **Interface-First Design**:
   - Define interfaces (protocols) before implementing concrete classes.
   - Use Python's `typing.Protocol` for interface definitions.
   - All concrete implementations must properly implement their protocols.

4. **Dependency Direction**:
   - Dependencies should point inward (CLI → Services → Data Access).
   - Higher-level components should not depend on implementation details of lower-level ones.
   - Use dependency injection for all external dependencies.

## CLI Implementation Rules

1. **Argument Parsing**:
   - Use Python's `argparse` module for command-line interface.
   - Implement the sub-parser pattern for command organization.
   - Use a parent parser for common arguments to ensure consistency.
   - Validate all user inputs before processing.

2. **Command Structure**:
   - Implement all required commands:
     - `list` (default): List all available themes
     - `paths`: Show theme search paths
     - `theme NAME`: Extract colors from the specified theme

3. **Options Implementation**:
   - Support all specified options:
     - `--format text|json` (default: json)
     - `--output FILE`
     - `--verbose` or `-v`
     - `--version`
     - `--help` or `-h`

4. **Error Handling**:
   - Use appropriate exit codes:
     - `0`: Success
     - `1`: General error
     - `2`: Invalid arguments
     - `3`: Theme not found
     - `4`: I/O error
   - Provide clear error messages for all error conditions.

5. **Version Management**:
   - Use `importlib.metadata` to retrieve version information.
   - Avoid hardcoding version numbers in the source code.

## Service Layer Rules

### Theme Loader

1. **Theme Discovery**:
   - Implement theme discovery in standard KDE directories.
   - Follow XDG Base Directory Specification for path discovery.
   - Handle multiple theme sources (user, system, look-and-feel).

2. **Theme Parsing**:
   - Parse theme files correctly, including:
     - `.colors` files for color schemes
     - `metadata.desktop` files for theme metadata
   - Handle theme inheritance chains.
   - Validate theme structure and content.

3. **Performance Optimizations**:
   - Implement caching for theme paths and metadata.
   - Use lazy loading for theme resources.
   - Process large theme files in chunks when possible.

4. **Error Handling**:
   - Handle missing or corrupt theme files gracefully.
   - Provide meaningful error messages for parsing failures.
   - Implement fallback mechanisms for invalid themes.

### File System Service

1. **Abstraction**:
   - Abstract all file system operations behind the `FileSystem` interface.
   - Implement `StdFileSystem` for production use.
   - Implement a separate `FileSystemDouble` interface for testing purposes.

2. **Operations**:
   - Implement all required file system operations:
     - `read_file(path)`
     - `file_exists(path)`
     - `is_dir(path)`
     - `glob(pattern)`
     - `walk(path)`

3. **Safety Measures**:
   - Implement path sanitization for all file operations.
   - Check file permissions before access.
   - Use safe path joining to prevent directory traversal.
   - Restrict access to system directories.

4. **Performance**:
   - Optimize file existence checks.
   - Implement lazy loading of file contents.
   - Release resources promptly after use.

### Output Formatting

1. **JSON Formatting**:
   - Implement proper JSON serialization for theme data.
   - Format output for readability when requested.
   - Ensure valid JSON structure at all times.

2. **Output Handling**:
   - Support writing to file or stdout.
   - Handle large outputs efficiently.
   - Properly close file handles after use.

3. **Performance Optimizations**:
   - Use efficient string building techniques.
   - Implement memory-efficient serialization.
   - Support streaming for large outputs.

## Interface Design Rules

1. **Protocol Definitions**:
   - Define clear protocol interfaces using Python's `typing.Protocol`.
   - Document expected behavior, parameters, and return values.
   - Include error conditions and exceptions in documentation.

2. **Interface Stability**:
   - Keep interfaces stable once defined.
   - Use interface versioning if breaking changes are needed.
   - Maintain backward compatibility when possible.

3. **Protocol Extensions**:
   - Use protocol inheritance for extending interfaces.
   - Create specialized interfaces for testing (e.g., `FileSystemDouble`).
   - Document test-specific extensions separately from production interfaces.

## Data Structure Rules

1. **Theme Data Structure**:
   - Use consistent structure for theme data:
     ```python
     {
         "name": str,               # Theme name (e.g., "Breeze")
         "colors": {
             "windowBackground": str,  # Hex color code
             "windowForeground": str,  # Hex color code
             # ... additional color definitions
         },
         "metadata": {
             "version": str,          # Theme version
             "author": str,           # Theme author
             # ... additional metadata
         }
     }
     ```
   - Maintain consistent key naming conventions.
   - Validate data structure integrity.

## Error Handling Rules

1. **Error Hierarchy**:
   - Implement a clear error hierarchy with a base `KDEThemeError` class.
   - Create specific error types for different error conditions:
     - `ThemeNotFoundError`
     - `InvalidThemeError`
     - `IOError`
     - `PermissionError`

2. **Error Recovery**:
   - Implement graceful fallback for missing theme files.
   - Provide detailed error messages with context.
   - Suggest resolution steps when possible.

3. **Exception Propagation**:
   - Catch and handle exceptions at appropriate levels.
   - Convert low-level exceptions to domain-specific ones.
   - Log all exceptions with appropriate context.

## Performance Rules

1. **Caching Strategy**:
   - Cache theme file contents to avoid repeated disk I/O.
   - Cache theme paths and metadata after first access.
   - Implement cache invalidation on theme changes.
   - Set size limits to prevent excessive memory usage.

2. **Memory Management**:
   - Load large theme files in chunks when possible.
   - Only load required theme data into memory.
   - Release resources promptly after use.
   - Use generators for processing large data sets.

## Security Rules

1. **File System Security**:
   - Only perform read operations on theme files.
   - Detect and prevent path traversal attempts.
   - Check file permissions before access.
   - Never access sensitive system files.

2. **Input Validation**:
   - Validate all command-line arguments.
   - Sanitize theme names before use.
   - Normalize and validate file paths.
   - Restrict output file permissions.

## Design Pattern Usage

1. **Dependency Injection**:
   - Pass dependencies as parameters to components.
   - Use constructor injection for required dependencies.
   - Allow optional dependencies with sensible defaults.

2. **Factory Pattern**:
   - Use factory methods to create formatters based on output format.
   - Implement `OutputFormatterFactory` for creating formatter instances.

3. **Strategy Pattern**:
   - Use different theme loading strategies for different KDE versions.
   - Allow `ThemeLoader` to be extended with different loading strategies.

## Testing Considerations

1. **Testability**:
   - Design components with testability in mind.
   - Use dependency injection to facilitate testing.
   - Create interfaces that are easy to implement in test doubles.

2. **Test Doubles**:
   - Implement test-specific doubles that conform to interfaces.
   - Use `FakeFileSystem` for file system operations in tests.
   - Create specialized test doubles for complex components.

These rules serve as guidelines for implementation and can be used as a checklist during development to ensure compliance with the Software Design Document.
