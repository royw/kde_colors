# Architecture

This document describes the high-level architecture of the `kde-colors` project.

## Package Structure

The `kde_colors` package is organized into the following structure:

```text
kde_colors/
├── __init__.py        # Main package initialization
├── __main__.py        # Entry point for direct execution, defined in pyproject.toml, calls cli_runner.run_cli()
├── cli/               # Command-line interface components
│   ├── __init__.py
│   ├── cli_arg_parser.py  # Argument parsing
│   └── cli_runner.py      # Command execution
├── interfaces/        # Protocol definitions
│   ├── __init__.py
│   ├── environment.py     # Environment interface
│   ├── file_system.py     # FileSystem interface
│   ├── output_formatter.py # OutputFormatter interface
│   ├── theme_loader.py    # ThemeLoader interface
│   └── xdg.py            # XDG interface
├── services/          # Service implementations
│   ├── __init__.py
│   ├── environment.py     # Environment service
│   ├── file_system.py     # FileSystem implementation
│   ├── output_formatter.py # OutputFormatter implementation
│   ├── theme_loader.py    # ThemeLoader implementation
│   └── xdg.py             # XDG implementation
└── tests/             # Test suite
    ├── __init__.py
    ├── unit/               # Unit tests
    │   └── __init__.py
    ├── integration/        # Integration tests
    │   └── __init__.py
    ├── e2e/                # End-to-end tests
    │   └── __init__.py
    ├── performance/        # Performance tests
    │   └── __init__.py
    └── support/           # Test doubles for interfaces
        ├── __init__.py
        ├── environment_double.py
        ├── file_system_double.py
        ├── output_formatter_double.py
        ├── theme_loader_double.py
        └── xdg_double.py
```

## Project Script

The `kde-colors` script is the entry point for the application. It is defined in the `kde_colors.__main__` module.

pyproject.toml defines the script entry point:
scripts = {'kde_colors' = "kde_colors.__main__:main"}

## System Overview

The following diagram shows the main components of the system and their relationships:

```mermaid
graph TD
    %% Core Components
    User[User] -->|interacts with| CLI["CLI (Command Line Interface)"]
    CLI -->|uses| CLIRunner["CLIRunner"]

    %% Command Handlers
    CLIRunner -->|dispatches to| CommandHandlers["Command Handlers"]
    CommandHandlers -->|list command| ListCmd["List Command"]
    CommandHandlers -->|paths command| PathsCmd["Paths Command"]
    CommandHandlers -->|theme command| ThemeCmd["Theme Command"]

    %% Services
    ListCmd -->|uses| ThemeLoader["ThemeLoader"]
    PathsCmd -->|uses| ThemeLoader
    ThemeCmd -->|uses| ThemeLoader

    %% Formatters
    ListCmd -->|formats output via| OutputFormatter["OutputFormatter"]
    PathsCmd -->|formats output via| OutputFormatter
    ThemeCmd -->|formats output via| OutputFormatter

    %% Output Formatter Types
    OutputFormatter -->|creates| TextOut["*TextOutputFormatter"]
    OutputFormatter -->|creates| JsonOut["*JsonOutputFormatter"]

    %% Note for formatter types
    JsonOut -.- Note("<p>* is one of <ul><li>List</li><li>Paths</li><li>Theme</li></ul></p>")
    TextOut -.- Note

    %% Dependencies
    ThemeLoader -->|depends on| FileSystem["FileSystem"]
    ThemeLoader -->|depends on| XDG["XDG"]
    FileSystem -->|depends on| Environment["Environment"]
    XDG -->|depends on| Environment

    %% Interface Implementation Relationships
    ThemeLoader -.->|implements| ThemeLoaderInterface["ThemeLoaderInterface"]
    FileSystem -.->|implements| FileSystemInterface["FileSystemInterface"]
    OutputFormatter -.->|implements| OutputFormatterInterface["OutputFormatterInterface"]
    Environment -.->|implements| EnvironmentInterface["EnvironmentInterface"]
    XDG -.->|implements| XDGInterface["XDGInterface"]

    class ThemeLoaderInterface,FileSystemInterface,OutputFormatterInterface,EnvironmentInterface,XDGInterface interface
    class ThemeLoader,FileSystem,OutputFormatter,Environment,XDG service
    class CLI,CLIRunner,CommandHandlers,ListCmd,PathsCmd,ThemeCmd cli
    class User user
```

This architecture follows a clean, dependency-injected design with clear separation of interfaces and implementations. The CLI layer handles user interaction, the service layer provides core functionality, and interfaces establish contracts between components.

## Interface Design

The system uses protocol-based interfaces to define clear contracts between components. The main interfaces are defined in the `kde_colors.interfaces` package:

### FileSystemInterface

- __Purpose__: Abstract file system operations for both reading and writing.
- __Location__: `kde_colors.interfaces.file_system`
- __Key Methods__: `read_text()`, `exists()`, `is_file()`, `is_dir()`, `glob()`, `walk()`, `resolve_path()`, `expand_path()`, `list_files()`, `list_dir()`, `write_text()`

#### tests/support/file_system_double.py

- __Implements__: Implements the `FileSystemInterface` protocol
- __Purpose__: Test double implementation of the FileSystem interface for testing.
- __Location__: `tests.support.file_system_double`
- __Key Methods__: All methods from `FileSystemInterface` plus additional testing functionality like `mkdir()`, `remove()`, `rmdir()`

### XDGInterface

- __Purpose__: Abstract XDG Base Directory Specification that encapsulates XDG directory paths. Allows tests to inject custom XDG directories.
- __Location__: `kde_colors.interfaces.xdg`
- __Key Methods__: `xdg_cache_home()`, `xdg_config_dirs()`, `xdg_config_home()`, `xdg_data_dirs()`, `xdg_data_home()`, `xdg_runtime_dir()`, `xdg_state_home()`

#### tests/support/xdg_double.py

- __Implements__: Implements the `XDGInterface` protocol
- __Purpose__: Test double implementation for XDG interface
- __Location__: `tests.support.xdg_double`
- __Key Methods__: All methods from `XDGInterface` with customizable directory configurations

### ThemeLoaderInterface

- __Purpose__: Load and query KDE themes using XDG and FileSystem interfaces.
- __Location__: `kde_colors.interfaces.theme_loader`
- __Key Methods__: `get_themes()`, `get_theme_paths()`, `get_current_theme()`, `get_theme_details()`

#### tests/support/theme_loader_double.py

- __Implements__: Implements the `ThemeLoaderInterface` protocol
- __Purpose__: Test double implementation for the ThemeLoader interface
- __Location__: `tests.support.theme_loader_double`
- __Key Methods__: All methods from `ThemeLoaderInterface` with predefined test data

### OutputFormatterInterface

- __Purpose__: Format theme data into different output formats
- __Location__: `kde_colors.interfaces.output_formatter`
- __Key Method__: `format()`

#### tests/support/output_formatter_double.py

- __Implements__: Implements the `OutputFormatterInterface` protocol
- __Purpose__: Test double implementation for the OutputFormatter interface
- __Location__: `tests.support.output_formatter_double`
- __Key Method__: `format()` with configurable output

### EnvironmentInterface

- __Purpose__: Abstract interface that encapsulates environment variables. Allows tests to inject custom environment variables.
- __Location__: `kde_colors.interfaces.environment`
- __Key Methods__: `getenv()`

#### tests/support/environment_double.py

- __Implements__: Implements the `EnvironmentInterface` protocol
- __Purpose__: Test double implementation for the Environment interface
- __Location__: `tests.support.environment_double`
- __Key Methods__: `getenv()`, `setenv()`, `clearenv()`

### Services

- __Purpose__: Implement protocol interfaces.
- __Location__: `kde_colors.services`
- __Key Classes__: `ThemeLoader`, `FileSystem`, `OutputFormatter`, `EnvironmentService`

### ThemeLoader Service

- __Purpose__: Load and query KDE themes using XDG and FileSystem Interfaces.
- __Location__: `kde_colors.services.theme_loader`
- __Key Methods__: `load_themes()`

### FileSystem Service

- __Purpose__: Abstract Read-only file system operations injector.
- __Location__: `kde_colors.services.file_system`
- __Key Methods__: `read_file()`, `file_exists()`, `exists()`, `is_file()`, `is_dir()`, `glob()`, `walk()`, `resolve_path()`, `expand_path()`, `list_files()`, `list_dir()`

### OutputFormatter Service

- __Purpose__: Format theme data into different output formats
- __Location__: `kde_colors.services.output_formatter`
- __Key Method__: `format()`

### Environment Service

- __Purpose__: Abstract environment detection injector that encapsulates environment variables.  Allows tests to inject custom environment variables.
- __Location__: `kde_colors.services.environment`
- __Key Methods__: `getenv()`

## Theme Data Structure

Theme data is represented as dictionaries in the application:

- Theme metadata: `dict[str, str]` - Contains name, package, etc.
- Theme colors: `dict[str, dict[str, list[int]]]` - Color definitions organized by color group
- Theme paths: `list[str]` - Lists of paths to theme files

## CLI Package Architecture

The `kde_colors.cli` package handles all command-line interaction and serves as the entry point for the application.

### cli_arg_parser.py

- __Purpose__: Defines and handles command-line argument parsing
- __Key Components__:
  - `create_parser()`: Creates and configures the command-line argument parser
  - `parse_args()`: Parses command-line arguments and applies defaults
  - `get_version()`: Retrieves the application version

### cli_runner.py

- __Purpose__: Executes CLI commands based on parsed arguments
- __Key Components__:
  - `CLIRunner` class: Orchestrates the execution of commands
  - Command handlers: `_cmd_list()`, `_cmd_paths()`, `_cmd_theme()`
  - `run_cli()`: Entry point function for the application

### Command-line Argument Parsing

The CLI argument parsing architecture uses the sub-parser pattern from Python's `argparse` module:

```mermaid
graph TD
    %% CLI Argument Parsing Architecture
    main_parser[Main Parser]-->parent_parser[Parent Parser with Global Options]
    main_parser-->subparsers[Subparsers]

    subparsers-->list_cmd[List Command]
    subparsers-->paths_cmd[Paths Command]
    subparsers-->theme_cmd[Theme Command]

    parent_parser-.->|inherits|list_cmd
    parent_parser-.->|inherits|paths_cmd
    parent_parser-.->|inherits|theme_cmd

    %% Options flow
    list_cmd-->parsed_args[Parsed Arguments]
    paths_cmd-->parsed_args
    theme_cmd-->parsed_args
    parsed_args-->command_handler[Command Handler]
```

This architecture has several benefits:

1. __Consistent Option Handling__: Global options like `--verbose` are defined once but work universally
2. __Modular Design__: Each command is encapsulated in its own parser
3. __Extensible__: Adding new commands requires minimal changes to existing code
4. __Uniform Help Text__: Help documentation is standardized across all commands

### Version Management

Version information is managed through Python's standard library:

```mermaid
graph LR
    %% Version Management Architecture
    pyproject[pyproject.toml]-->|defines|package_version[Package Version]
    package_version-->|read by|importlib[importlib.metadata]
    importlib-->|provides|version_var[__version__ Variable]
    version_var-->|used by|cli[CLI --version Flag]
    version_var-->|used by|error_reporting[Error Reporting]
```

This approach follows Python's best practices:

1. The version is defined exactly once in the project metadata
2. Runtime version detection uses the standard library's `importlib.metadata`
3. No hardcoded version strings throughout the codebase

## Components

### CLI

The Command Line Interface (CLI) is the main entry point for users. It handles:

- Command-line argument parsing
- User input validation
- Coordinating between different components

### Core Services

#### ThemeLoader

The ThemeLoader component is responsible for:

- Loading theme data from KDE configuration files
- Validating theme data
- Providing a clean interface for accessing theme properties

#### FileSystem

The FileSystem component handles all file system operations:

- Enables test doubling by routing file system operations to a protocol interface
- Provides a clean interface for accessing file system properties
- Handles file system errors

### Output Formatters

Output formatters convert theme data into different formats:

- JSON
- Human-readable text
- Potentially other formats in the future
