# KDE Colors

A CLI tool that extracts color schemes from KDE themes

[![CI](https://github.com/royw/kde_colors/actions/workflows/ci.yml/badge.svg)](https://github.com/royw/kde_colors/actions/workflows/ci.yml)
[![Documentation](https://github.com/royw/kde_colors/actions/workflows/ci.yml/badge.svg)](https://royw.github.io/kde_colors/)
[![PyPI version](https://badge.fury.io/py/kde_colors.svg)](https://badge.fury.io/py/kde_colors)
[![codecov](https://codecov.io/gh/royw/kde_colors/branch/main/graph/badge.svg)](https://codecov.io/gh/royw/kde_colors)

## Installation

```bash
pip install kde_colors
```

## Development

This project uses [Task](https://taskfile.dev) for task automation and GitHub Actions for CI/CD.

### Python Version Management

This project supports multiple Python versions using [uv](https://github.com/astral-sh/uv) for dependency management. Python versions are configured in two files:

- `.python-versions` - List of supported Python versions
- `.python-version` - Default Python version for development

Each Python version has its own virtual environment (`.venv-X.Y`), and `.venv` symlinks to the default version's environment.

#### Managing Python Versions

```bash
# List installed Python versions (* marks default)
task python:list-installed

# Add a Python version
task python:add -- 3.11

# Set default Python version
task python:set-default -- 3.11

# Remove a Python version
task python:remove -- 3.11
```

### Setup

```bash
task setup
```

This will:
1. Install all Python versions listed in `.python-versions`
2. Create virtual environments for each Python version
3. Install the package in editable mode with all dependencies
4. Set up pre-commit hooks
5. Create `.venv` symlink to the default Python version

### Available Tasks

#### Environment Management
- `task setup` - Set up development environments
- `task update:env` - Update all virtual environments
- `task update:dev-env` - Update only default environment
- `task upgrade-env` - Upgrade all dependencies
- `task clean` - Clean build artifacts and caches
- `task clean:venvs` - Remove all virtual environments

#### Testing
- `task test` - Run tests using default Python version
- `task test:coverage` - Run tests with coverage report
- `task test:pythons` - Run tests across all supported Python versions

#### Code Quality
- `task lint` - Run code quality checks (ruff, mypy, pre-commit)
- `task format` - Format code with ruff
- `task metrics` - Run code quality metrics (radon)
- `task spell` - Run codespell checks

#### Documentation
- `task docs` - Serve documentation locally
- `task docs:build` - Build documentation

#### Build and Publish
- `task build` - Build package distribution (wheel and sdist)
- `task publish:pypi` - Publish to PyPI
- `task publish:test-pypi` - Publish to Test PyPI

#### CI/CD
- `task ci` - Run all CI checks (lint, test, coverage, docs, build)

Run `task --list-all` to see all available tasks with descriptions.

### Continuous Integration

#### Monitoring Workflow Status

To check the status of GitHub Actions:

1. Go to your repository on GitHub
2. Click the "Actions" tab
3. You'll see a list of all workflow runs, with their status:
   - ✅ Green check: All jobs passed
   - ❌ Red X: One or more jobs failed
   - 🟡 Yellow dot: Workflow is in progress

You can also:
- Click on any workflow run to see detailed job results
- Click the "Re-run jobs" button to retry failed jobs
- See the status badge in the README: [![CI](https://github.com/royw/myrgb/actions/workflows/ci.yml/badge.svg)](https://github.com/royw/myrgb/actions/workflows/ci.yml)

GitHub Actions will automatically:
- Run tests across all supported Python versions
- Upload coverage reports to Codecov
- Run code quality checks (ruff, mypy)
- Run security checks (bandit)
- Build and test documentation
- Deploy documentation to GitHub Pages (on main branch)
- Publish package to PyPI (on release)

#### Setting up Codecov

To enable coverage reporting to Codecov:

1. Go to https://app.codecov.io/ and sign in with your GitHub account
2. Add your repository:
   - Go to https://app.codecov.io/gh/royw
   - Click "Add new repository"
   - Select "myrgb"
3. Get your Codecov token:
   - Go to repository settings
   - Look for "Repository Upload Token"
   - Copy the token value
4. Add the token to GitHub:
   - Go to your repository settings on GitHub
   - Navigate to Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `CODECOV_TOKEN`
   - Value: Paste the token from Codecov
   - Click "Add secret"

### Publishing to PyPI

#### Setting up PyPI Publishing

To enable automatic publishing to PyPI and Test PyPI through GitHub Actions:

1. Create accounts:
   - Sign up for PyPI: https://pypi.org/account/register/
   - Sign up for Test PyPI: https://test.pypi.org/account/register/

2. Create API tokens:
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Set scope to "Project: myrgb"
   - Copy the token value
   - Repeat for Test PyPI at https://test.pypi.org/manage/account/token/

3. Add tokens to GitHub:
   - Go to your repository settings on GitHub
   - Navigate to Settings > Secrets and variables > Actions
   - Add two secrets:
     1. `PYPI_TOKEN` - Your PyPI token
     2. `TEST_PYPI_TOKEN` - Your Test PyPI token

#### Publishing a New Version

Once set up, you can publish new versions in two ways:

1. **Manual Publishing** (using task)

   ```bash
   # Update version
   task version:bump -- patch  # For patch version (0.0.x)
   task version:bump -- minor  # For minor version (0.x.0)
   task version:bump -- major  # For major version (x.0.0)

   # Create and push tag
   task version:tag

   # Manual publishing if needed
   task publish:test-pypi  # Publish to Test PyPI
   task publish:pypi       # Publish to PyPI
   ```

2. **Automatic Publishing** (using GitHub)

   Simply create a new release on GitHub:
   - Go to your repository's Releases page
   - Click "Create a new release"
   - Choose or create a tag (e.g., v0.1.0)
   - Fill in the release title and description
   - Click "Publish release"

   The CI/CD workflow will automatically:
   - Run all checks (lint, test, coverage)
   - Build and verify the package
   - Publish to Test PyPI first
   - Run test installation from Test PyPI
   - Publish to PyPI if tests pass
   - Build and deploy documentation
   - Create a GitHub release

## Documentation

The documentation is built using MkDocs with the Material theme and mkdocstrings for API documentation.

To view the documentation locally:

```bash
task docs
```

Then open http://127.0.0.1:8000 in your browser.

The documentation is automatically deployed to GitHub Pages when changes are pushed to the main branch: https://royw.github.io/kde_colors/

## License

MIT
