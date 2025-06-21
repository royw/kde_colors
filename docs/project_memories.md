# Project Memories

This page contains important learnings and best practices that were captured during the development of this project template.

## Documentation Memories

### Comprehensive Module Documentation
!!! note "Memory ID: 58379707-d0cd-4c25-ae1e-f9628992dc2a"
    Added comprehensive documentation for all modules in the project:
    1. Document each class and its methods
    2. Document exceptions in a separate file
    3. Document model classes
    4. Verify documentation coverage with verify_docs.py
    5. Ensure all functions are documented and verified

### Class Method Documentation Fix
!!! tip "Memory ID: 426938d6-3fe7-46df-b2b7-84b66a692667"
    When documenting class methods:
    1. Track class methods separately from module-level functions
    2. Use a two-pass approach:
        - First collect class methods
        - Then collect module-level functions that aren't class methods
    3. This prevents duplicate documentation of methods

## Best Practices

### Documentation Structure
- Use Google-style docstrings for consistency
- Document all public methods and classes
- Include examples in docstrings when helpful
- Organize API documentation hierarchically by package/module
- Use type hints consistently throughout the codebase

### Project Organization
- Use src-layout for Python packages
- Keep documentation in docs/ directory
- Store utility scripts in scripts/ directory
- Use pyproject.toml for modern Python packaging
- Implement task automation with Taskfile.yml

### Code Quality
- Use Black for consistent code formatting
- Implement linting with Ruff
- Enforce type checking with MyPy
- Write comprehensive tests with Pytest
- Verify documentation coverage
