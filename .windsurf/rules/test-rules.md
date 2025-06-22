# Test Rules

This document outlines specific rules derived from the Test Design Document (TDD) to guide the implementation of tests for the KDE Theme Colors tool. Following these rules will ensure a robust testing strategy that meets project requirements.

## General Testing Rules

1. **No-Mocking Policy**:
   - Do not use mock objects or monkey patching.
   - Avoid using `unittest.mock`, `patch`, or any form of runtime patching.
   - Prefer real implementations or test doubles that implement the same interfaces.

2. **Test Coverage Requirements**:
   - Maintain a minimum test coverage of 60% across all modules.
   - Aim for higher coverage (80%+) in core functionality modules.
   - Generate and review coverage reports regularly using `task test:cov`.

3. **Test Organization**:
   - Unit tests in `/tests/unit/`
   - Integration tests in `/tests/integration/`
   - End-to-end tests in `/tests/e2e/`
   - Test data in `/tests/test_data/`

4. **Test Environment**:
   - Support Python 3.11, 3.12, and 3.13.
   - Design tests to work on any Linux environment with KDE Plasma 5 or 6.

## Testing Approaches

### 1. Dependency Injection

- Design all components to accept dependencies via constructor parameters.
- Pass real implementations in production code.
- Pass test-specific implementations in test code.
- Example:
  ```python
  # Production code
  class CLIRunner:
      def __init__(self, theme_loader: ThemeLoader, file_system: FileSystem):
          self.theme_loader = theme_loader
          self.file_system = file_system

  # Test code
  def test_cli_runner():
      theme_loader = FakeThemeLoader()
      file_system = FakeFileSystem()
      runner = CLIRunner(theme_loader, file_system)
      # Test with controlled dependencies
  ```

### 2. Test Doubles

- Create lightweight implementations of interfaces for testing.
- Test doubles should implement the same interfaces as production code.
- Name test doubles with a descriptive prefix (e.g., `Fake`, `Stub`).
- Do not use `Test` as a prefix for test doubles to avoid pytest collection issues.
- Example:
  ```python
  class FakeFileSystem(FileSystem):
      def __init__(self, files: dict[str, str] = None):
          self.files = files or {}

      def read_file(self, path: str) -> str:
          if path not in self.files:
              raise FileNotFoundError(f"File not found: {path}")
          return self.files[path]
  ```

### 3. Test-Specific Interfaces

- Create extended interfaces for testing that include additional test methods.
- Ensure these interfaces extend the production interfaces for type safety.
- Example:
  ```python
  class FileSystemDouble(FileSystem, Protocol):
      def add_file(self, path: str, content: str) -> None: ...
      def delete_file(self, path: str) -> None: ...
  ```

### 4. Protocol Conformance Testing

- Test that implementations conform to their protocols using `isinstance()`.
- Verify that all required methods are properly implemented.
- Ensure type hints match between protocols and implementations.
- Example:
  ```python
  def test_file_system_conformance():
      fs = StdFileSystem()
      assert isinstance(fs, FileSystem), "StdFileSystem should implement FileSystem protocol"

      test_fs = FakeFileSystem()
      assert isinstance(test_fs, FileSystem), "FakeFileSystem should implement FileSystem protocol"
      assert isinstance(test_fs, FileSystemDouble), "FakeFileSystem should implement FileSystemDouble protocol"
  ```

## Unit Testing Rules

1. **Component Isolation**:
   - Test individual components in isolation.
   - Provide test doubles for dependencies.
   - Focus on the component's public interface.

2. **Test Structure**:
   - Group tests by component/class.
   - Create test classes with clear method names.
   - Avoid using test class constructors (`__init__`) as pytest may collect them.
   - Use `setup_method` and `teardown_method` for test fixtures.

3. **Error Handling**:
   - Test both success and error paths.
   - Verify that appropriate exceptions are raised.
   - Test edge cases and boundary conditions.

4. **State Validation**:
   - Verify that component state is correctly modified.
   - Test state transitions and side effects.
   - Reset any global state in teardown methods.

## Integration Testing Rules

1. **Component Interaction**:
   - Test how components interact with each other.
   - Test workflows that span multiple components.
   - Verify data flow between components.

2. **Real Implementations**:
   - Use real implementations of components.
   - Use test doubles only for external dependencies.
   - Test with realistic data and scenarios.

3. **Contract Testing**:
   - Verify that components honor their contracts.
   - Test that interfaces are used correctly.
   - Ensure component substitutability.

## End-to-End Testing Rules

1. **Complete Workflows**:
   - Test complete user workflows.
   - Use subprocess to run the CLI as a real user would.
   - Test all CLI commands and options.

2. **Output Validation**:
   - Verify that output matches expected format.
   - Test both stdout and file output.
   - Validate exit codes for success and error scenarios.

3. **Environment Setup**:
   - Set up a controlled test environment.
   - Provide test themes and files.
   - Clean up after tests to maintain isolation.

## Test Data Management

1. **Test Themes**:
   - Create a variety of test themes:
     - Minimal theme (for fast testing)
     - Full theme (for comprehensive testing)
     - Corrupt theme (for error handling)
     - Theme with inheritance (for testing parent-child relationships)

2. **Expected Outputs**:
   - Provide expected output files for comparison.
   - Include both JSON and text format examples.
   - Cover various edge cases and error scenarios.

3. **File System Structure**:
   - Simulate XDG directory structure.
   - Include user and system theme directories.
   - Test with various file permissions.

## CI/CD Integration

1. **Automated Test Execution**:
   - Run tests on every push to main branch.
   - Run tests on all pull requests.
   - Run scheduled nightly test suites.

2. **Test Reporting**:
   - Generate HTML coverage reports.
   - Produce JUnit XML for CI integration.
   - Track coverage trends over time.

3. **Performance Benchmarking**:
   - Measure test execution time.
   - Track performance trends.
   - Alert on significant performance degradation.

## Exit Criteria

1. **Test Completion**:
   - All high-priority tests pass.
   - No critical defects remain open.
   - Test coverage meets or exceeds the minimum requirement.
   - Performance tests show acceptable results.

2. **Documentation**:
   - Test plans are up-to-date.
   - Known issues are documented.
   - Test results are summarized.

These rules should be applied throughout the development process to ensure the KDE Theme Colors tool is thoroughly tested and meets all requirements specified in the Software Requirements Specification.
