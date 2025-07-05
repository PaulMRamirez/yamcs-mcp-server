# Contributing to Yamcs MCP Server

We welcome contributions to the Yamcs MCP Server! This document provides guidelines for contributing to the project.

## Development Workflow

### Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/yamcs-mcp-server.git
   cd yamcs-mcp-server
   ```

3. Set up the development environment:
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   uv sync --all-extras

   # Install pre-commit hooks
   pre-commit install
   ```

### Making Changes

1. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards
3. Add or update tests as needed
4. Run the test suite:
   ```bash
   uv run pytest
   ```

5. Run code quality checks:
   ```bash
   uv run ruff check .
   uv run ruff format .
   uv run mypy src/
   ```

### Commit Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages:

- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```bash
git commit -m "feat: add parameter subscription support"
git commit -m "fix: handle connection timeouts gracefully"
git commit -m "docs: update installation instructions"
```

### Pull Request Process

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a Pull Request on GitHub
3. Ensure all CI checks pass
4. Request review from maintainers
5. Address any feedback

## Code Standards

### Python Code Style

We use `ruff` for linting and formatting. The configuration is in `ruff.toml`.

Key style points:
- Line length: 88 characters (Black standard)
- Use double quotes for strings
- Type hints for all function parameters and return values
- Docstrings for all public functions and classes (Google style)

### Type Checking

We use `mypy` in strict mode. All code must pass type checking:

```bash
uv run mypy src/
```

### Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use `pytest` for all tests
- Mock external dependencies appropriately

Test structure:
```python
import pytest
from yamcs_mcp.components.mdb import MDBComponent

class TestMDBComponent:
    """Tests for MDB component."""

    @pytest.mark.asyncio
    async def test_list_parameters(self):
        """Test listing parameters."""
        # Test implementation
```

## Documentation

- Update README.md if adding new features
- Add docstrings to all public APIs
- Update examples if changing behavior
- Keep CHANGELOG.md up to date

## Issue Reporting

When reporting issues, please include:
1. Python version
2. Yamcs version
3. Full error messages and stack traces
4. Steps to reproduce
5. Expected vs actual behavior

## Feature Requests

We welcome feature requests! Please:
1. Check existing issues first
2. Describe the use case
3. Provide examples if possible
4. Be open to discussion about implementation

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion on GitHub
- Contact maintainers

Thank you for contributing to Yamcs MCP Server!