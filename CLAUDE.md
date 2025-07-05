# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server for Yamcs (Yet Another Mission Control System). It provides a bridge between AI assistants and mission control systems using FastMCP 2.x with a modular component architecture.

## Key Commands

### Development Setup
```bash
# Install all dependencies including dev tools
uv sync --all-extras

# Install pre-commit hooks
pre-commit install
```

### Running the Server
```bash
# Run the server (will connect to Yamcs at http://localhost:8090)
uv run yamcs-mcp

# Run directly as Python module
uv run python -m yamcs_mcp.server

# Run in demo mode without Yamcs (shows warning but continues)
uv run python -m yamcs_mcp.server  # Yamcs connection failure is non-fatal
```

### Testing
```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_server.py -v

# Run specific test
uv run pytest tests/test_server.py::test_server_initialization -v

# Run tests with coverage report
uv run pytest --cov=yamcs_mcp --cov-report=html
```

### Code Quality
```bash
# Run linting
uv run ruff check .

# Run linting with auto-fix
uv run ruff check . --fix

# Run type checking
uv run mypy src/

# Format code
uv run ruff format .
```

## Architecture Overview

### Component-Based Design
The server uses FastMCP's composition pattern with six main components, each handling a specific Yamcs subsystem:

1. **BaseYamcsComponent** (`src/yamcs_mcp/components/base.py`)
   - Abstract base class defining the component interface
   - Key method: `register_with_server(server)` - components register their tools/resources with the FastMCP server
   - Components don't inherit from FastMCP, they compose with it

2. **Component Registration Pattern**
   - Each component implements `register_with_server(server)`
   - Inside this method, tools are defined as nested functions decorated with `@server.tool()`
   - Resources are defined with `@server.resource()`
   - Tools are async functions that interact with Yamcs via the client manager

3. **Server Initialization Flow** (`src/yamcs_mcp/server.py`)
   - Creates FastMCP instance
   - Instantiates enabled components based on config
   - Calls `register_with_server()` on each component
   - Runs the server with `run_async()` (not `run()` to avoid asyncio conflicts)

### Key Architectural Decisions

1. **Async Event Loop Handling**
   - The server uses `run_async()` instead of `run()` to work properly in environments with existing event loops
   - The main() function handles both cases: existing event loop (e.g., Jupyter) and new event loop

2. **Demo Mode**
   - Server continues running even if Yamcs connection fails (logs warning)
   - Allows testing MCP protocol without a real Yamcs instance

3. **Configuration**
   - Uses Pydantic for type-safe configuration
   - Environment variables with YAMCS_ and MCP_ prefixes
   - Component toggles allow selective feature enabling

4. **Client Management**
   - YamcsClientManager provides connection pooling and lifecycle management
   - Uses async context managers for proper cleanup

### Component Structure

Each component follows this pattern:
```python
class ComponentName(BaseYamcsComponent):
    def register_with_server(self, server: Any) -> None:
        @server.tool()
        async def tool_name(param: str) -> dict[str, Any]:
            # Implementation using self.client_manager
            pass
```

### Critical Files

- `src/yamcs_mcp/server.py` - Main server orchestration and component composition
- `src/yamcs_mcp/components/base.py` - Component interface definition
- `src/yamcs_mcp/client.py` - Yamcs connection management
- `src/yamcs_mcp/config.py` - Configuration schema and validation

### Environment Variables

Default instance name is `simulator` when using the example-simulation Docker image. Key variables:
- `YAMCS_URL` - Yamcs server URL (default: http://localhost:8090)
- `YAMCS_INSTANCE` - Yamcs instance name (default: simulator)
- `YAMCS_ENABLE_*` - Component toggles (all true by default)
- `MCP_TRANSPORT` - Transport type: stdio, http, or sse (default: stdio)

### Claude Desktop Integration

Uses uv's `--directory` flag for proper project resolution:
```json
{
  "command": "uv",
  "args": ["--directory", "/path/to/yamcs-mcp-server", "run", "yamcs-mcp"]
}
```

### Common Issues and Solutions

1. **"Already running asyncio in this thread"**
   - The server properly handles existing event loops
   - Uses `run_async()` instead of `run()`

2. **Claude Desktop "spawn uv ENOENT"**
   - Use `--directory` flag in args, not `cwd` parameter
   - Ensure uv is in PATH or use full path

3. **Abstract method errors**
   - All components must implement `register_with_server(server)`
   - Tools use `@server.tool()` not `@self.tool()`

4. **"'str' object has no attribute 'eng_type'" in mdb_list_parameters**
   - The yamcs-python client returns `param.type` as a string (e.g., "float", "int")
   - Not as an object with `eng_type` attribute
   - Fixed by using `param.type` directly

5. **Resources failing with "No active context found" or scope errors**
   - Resources defined with `@server.resource()` need to call tool functions
   - Tool functions defined in same `register_with_server` method are in closure scope
   - Resources can directly call the tool functions by name (they're in the same closure)
   - Don't use `self.tool_name()` - tools aren't class methods

### Testing Yamcs with Docker

Quick Yamcs setup for testing:
```bash
docker run -d --name yamcs -p 8090:8090 yamcs/example-simulation
```

This starts Yamcs with a `simulator` instance on port 8090 that includes example telemetry data.

## Memories

- First iteration of the Yamcs MCP server focused on core architecture and component design
- Developed with emphasis on async event loop handling and flexible component registration
- Initial design supports demo mode and provides robust connection management for Yamcs interactions