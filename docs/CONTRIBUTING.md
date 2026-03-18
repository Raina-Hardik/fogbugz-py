# Contributing Guide

Thank you for your interest in contributing to fogbugz-py! This guide will help you understand our development workflow and coding standards.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Python Development Standards](#python-development-standards)
- [Scripting Guidelines](#scripting-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Branch Naming Conventions](#branch-naming-conventions)
- [Pull Request Process](#pull-request-process)

## Getting Started

Before contributing, please:

1. Fork the repository
2. Clone your fork locally
3. Set up your development environment (see below)
4. Create a feature branch for your changes
5. Make your changes and commit them following our guidelines
6. Push to your fork and submit a pull request

## Development Environment

We use [uv](https://github.com/astral-sh/uv) for all Python package management and environment handling. **Never use pip or raw python commands directly.**

### Initial Setup

```bash
# Create a virtual environment
uv venv

# Install project dependencies
uv sync
```

### Installing Additional Dependencies

```bash
# Add new dependencies to the project
uv add requests typer pydantic

# Add development dependencies
uv add --dev pytest ruff mypy
```

### Running Python Scripts

```bash
# Run scripts within the environment
uv run python your_script.py

# Run CLI commands
uv run your_cli_command

# Run tools or modules
uv run -m pytest
```

## Python Development Standards

### Package Management

- **Always use `uv`** for dependency management
- Never use `pip install` or raw `python` commands
- Use `uv add` to add dependencies
- Use `uv remove` to remove dependencies
- Use `uv sync` to sync the environment with pyproject.toml

### Environment Management

```bash
# Create a new environment
uv venv

# Activate the environment (handled automatically by uv run)
# But if you need to activate manually:
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Unix/MacOS:
source .venv/bin/activate
```

## Scripting Guidelines

### Prefer Python Scripts Over Shell Scripts

Instead of writing raw PowerShell or bash scripts, write simple Python scripts that can be executed with `uv`. This ensures cross-platform compatibility and proper dependency management.

### Running Scripts with uv

```bash
# A script with no dependencies
uv run example.py

# A script with CLI arguments
uv run example.py --arg value

# A script with external dependencies
uv run --with requests example.py
```

### Creating Standalone Scripts

You can create Python scripts with inline dependency declarations:

```bash
# Initialize a script with dependencies
uv init --script example.py --python 3.12

# Add dependencies to an existing script
uv add --script example.py 'requests<3' 'rich'
```

### Avoiding Project Configuration

Use the `--no-project` flag when running scripts from within a project directory to avoid loading project-specific configuration:

```bash
uv run --no-project example.py
```

## Commit Message Guidelines

We follow a specific commit message style to maintain consistency across the project.

### Writing Commit Messages

- **Use imperative mood and present tense** (e.g., "add feature" not "added feature")
- **Do not use conventional commit prefixes** like `fix:`, `feat:`, `chore:`, etc.
- Write clear, descriptive commit messages that explain what the change does

### Examples

✅ **Good:**
```
correct typo in README file
add user authentication module
improve error handling in API client
```

❌ **Bad:**
```
fix: corrected typo in README file
feat: added user authentication
Fixed bugs
```

### What to Avoid

Do **not** use these conventional commit types:
- `fix:`
- `feat:`
- `build:`
- `chore:`
- `ci:`
- `docs:`
- `style:`
- `refactor:`
- `perf:`
- `test:`

## Branch Naming Conventions

Use descriptive branch names that clearly indicate the purpose of the branch.

### Format

- `feature/` - for new features
- `bugfix/` - for bug fixes
- `hotfix/` - for urgent production fixes
- `refactor/` - for code refactoring
- `docs/` - for documentation changes

### Examples

```bash
feature/user-authentication
bugfix/login-error-handling
hotfix/critical-security-patch
refactor/api-client-structure
docs/contribution-guide
```

### Creating a Branch

```bash
# Create and switch to a new feature branch
git checkout -b feature/your-feature-name

# Create and switch to a new bugfix branch
git checkout -b bugfix/fix-description
```

## Pull Request Process

1. **Ensure your code follows the project standards**
   - Use `uv` for all Python operations
   - Follow commit message guidelines
   - Use appropriate branch naming

2. **Update documentation**
   - Update README.md if needed
   - Add or update docstrings
   - Update relevant documentation in the `docs/` directory

3. **Test your changes**
   ```bash
   uv run -m pytest
   ```

4. **Format and lint your code**
   ```bash
   uv run ruff check .
   uv run ruff format .
   ```

5. **Submit your pull request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure all CI checks pass

6. **Respond to feedback**
   - Address review comments promptly
   - Make requested changes
   - Keep the PR updated with the main branch

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write clear docstrings for functions and classes
- Keep functions focused and concise
- Add comments for complex logic

## Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for high test coverage
- Use pytest for testing

```bash
# Run all tests
uv run -m pytest

# Run specific test file
uv run -m pytest tests/test_specific.py

# Run with coverage
uv run -m pytest --cov=src
```

## Questions or Issues?

If you have questions or run into issues:

1. Check existing documentation in the `docs/` directory
2. Search for existing issues on GitHub
3. Create a new issue with a detailed description
4. Reach out to maintainers for guidance

Thank you for contributing to fogbugz-py! 🎉
