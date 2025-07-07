# Development Guide

This guide covers setting up a development environment and working with the Yamcs MCP Server codebase.

## Prerequisites

- Python 3.12 or higher
- uv package manager
- Docker (optional, for running Yamcs locally)
- Git

## Setting Up Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/PaulMRamirez/yamcs-mcp-server.git
cd yamcs-mcp-server
```

### 2. Install uv

If you haven't installed uv yet:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Install Dependencies

```bash
# Install all dependencies including dev tools
uv sync --all-extras
```

### 4. Set Up Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install
```

### 5. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` to match your Yamcs setup:

```bash
YAMCS_URL=http://localhost:8090
YAMCS_INSTANCE=simulator
```

## Running Yamcs Locally

### Using Docker

The easiest way to run Yamcs for development:

```bash
# Run Yamcs with simulator instance
docker run -d --name yamcs \
  -p 8090:8090 \
  yamcs/example-simulation
```

### Using Local Installation

Follow the [Yamcs installation guide](https://docs.yamcs.org/getting-started/installation/).

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

Follow the project structure:
- Components go in `src/yamcs_mcp/components/`
- Shared utilities in `src/yamcs_mcp/utils/`
- Tests mirror the source structure

### 3. Run Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_server.py

# Run with coverage
uv run pytest --cov=yamcs_mcp --cov-report=html
```

### 4. Check Code Quality

```bash
# Run linting
uv run ruff check .

# Run formatting
uv run ruff format .

# Run type checking
uv run mypy src/
```

### 5. Test Locally

```bash
# Run the server
uv run yamcs-mcp

# Or with Python directly
uv run python -m yamcs_mcp.server
```

## Adding a New Component

### 1. Create Component File

Create `src/yamcs_mcp/components/your_component.py`:

```python
"""Your component description."""

from typing import Any

from ..client import YamcsClientManager
from ..config import YamcsConfig
from .base import BaseYamcsComponent


class YourComponent(BaseYamcsComponent):
    """Your component for specific functionality."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Your component."""
        super().__init__("YourComponent", client_manager, config)

    def _register_tools(self) -> None:
        """Register component-specific tools."""
        
        @self.tool()
        async def your_tool(
            param: str,
        ) -> dict[str, Any]:
            """Tool description."""
            try:
                async with self.client_manager.get_client() as client:
                    # Implementation
                    return {"result": "success"}
            except Exception as e:
                return self._handle_error("your_tool", e)

    def _register_resources(self) -> None:
        """Register component-specific resources."""
        
        @self.resource("your://resource")
        async def your_resource() -> str:
            """Resource description."""
            return "Resource content"
```

### 2. Add to Server

Update `src/yamcs_mcp/server.py`:

```python
from .components.your_component import YourComponent

# In _initialize_components():
if self.config.yamcs.enable_your_component:
    self.logger.info("Enabling Your component")
    your_comp = YourComponent(self.client_manager, self.config.yamcs)
    components.append(your_comp)
```

### 3. Add Configuration

Update `src/yamcs_mcp/config.py`:

```python
class YamcsConfig(BaseSettings):
    # ... existing fields ...
    enable_your_component: bool = True
```

### 4. Write Tests

Create `tests/components/test_your_component.py`:

```python
"""Tests for Your component."""

import pytest
from unittest.mock import Mock

from yamcs_mcp.components.your_component import YourComponent


class TestYourComponent:
    """Test Your component."""

    @pytest.fixture
    def your_component(self, mock_client_manager, mock_yamcs_config):
        """Create component instance."""
        return YourComponent(mock_client_manager, mock_yamcs_config)

    def test_component_initialization(self, your_component):
        """Test initialization."""
        assert your_component.name == "YamcsYourComponent"

    @pytest.mark.asyncio
    async def test_your_tool(self, your_component, mock_yamcs_client):
        """Test your tool."""
        # Test implementation
```

## Debugging

### Enable Debug Logging

Set the log level in your environment:

```bash
YAMCS_LOG_LEVEL=DEBUG uv run yamcs-mcp
```

### Using VS Code

The project includes VS Code settings for debugging:

1. Open the project in VS Code
2. Set breakpoints in your code
3. Press F5 to start debugging

### Common Issues

#### Connection Errors

```python
# Check Yamcs is running
curl http://localhost:8090/api

# Test with the client
uv run python -c "from yamcs.client import YamcsClient; print(YamcsClient('http://localhost:8090').get_server_info())"
```

#### Import Errors

```bash
# Ensure you're in the virtual environment
uv run python

# Check imports
>>> from yamcs_mcp import YamcsMCPServer
```

## Testing with Claude Desktop

### 1. Build and Install Locally

```bash
# Install in development mode
uv pip install -e .
```

### 2. Configure Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcp-servers": {
    "yamcs-dev": {
      "command": "uv",
      "args": ["run", "yamcs-mcp"],
      "cwd": "/path/to/yamcs-mcp-server",
      "env": {
        "YAMCS_URL": "http://localhost:8090",
        "YAMCS_INSTANCE": "simulator",
        "YAMCS_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### 3. Test Tools

In Claude, you can test tools:

```
Use the mdb_list_parameters tool to show me all parameters
```

## Performance Profiling

### Using cProfile

```python
import cProfile
import pstats

# In your test
profiler = cProfile.Profile()
profiler.enable()

# Run your code
await your_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Memory Profiling

```bash
# Install memory profiler
uv add --dev memory-profiler

# Run with memory profiling
uv run mprof run yamcs-mcp
uv run mprof plot
```

## Release Process

### 1. Update Version

Edit `pyproject.toml`:

```toml
[project]
version = "0.2.0"
```

### 2. Update Changelog

Add entry to `CHANGELOG.md`:

```markdown
## [0.2.0] - 2024-01-15

### Added
- New feature description

### Fixed
- Bug fix description
```

### 3. Create Release

```bash
# Commit changes
git add .
git commit -m "chore: release v0.2.0"

# Tag release
git tag -a v0.2.0 -m "Release version 0.2.0"

# Push to GitHub
git push origin main --tags
```

### 4. Build and Publish

```bash
# Build package
uv build

# Publish to PyPI (when ready)
uv publish
```

## Contributing

For detailed contribution guidelines, see the CONTRIBUTING.md file in the repository root.