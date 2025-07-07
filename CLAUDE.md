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

### Server Composition Pattern
The server uses FastMCP's server composition pattern where each Yamcs subsystem is implemented as an independent FastMCP server that gets mounted to the main server:

1. **BaseYamcsServer** (`src/yamcs_mcp/servers/base_server.py`)
   - Base class extending FastMCP for all servers
   - Provides common functionality like error handling
   - Each server is a full FastMCP instance

2. **Servers** (in `src/yamcs_mcp/servers/`)
   - **MDBServer** - Mission Database operations
   - **LinksServer** - Data link management
   - **ProcessorsServer** - Processor control
   - **InstancesServer** - Instance management
   - **StorageServer** - Object storage operations
   - **AlarmsServer** - Alarm management and monitoring

3. **Server Initialization Flow** (`src/yamcs_mcp/server.py`)
   - Creates main FastMCP instance
   - Instantiates enabled component servers based on config
   - Mounts each server with a prefix using `server.mount(component_server, prefix="prefix")`
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

### Server Structure

Each server follows this pattern:
```python
class ServerName(BaseYamcsServer):
    def __init__(self, client_manager, config):
        super().__init__("ServerType", client_manager, config)
        self._register_tools()
        self._register_resources()
        
    def _register_tools(self):
        @self.tool()
        async def tool_name(param: str) -> dict[str, Any]:
            # Implementation using self.client_manager
            pass
            
    def _register_resources(self):
        @self.resource("prefix://resource_name")
        async def resource_name() -> str:
            # Return formatted text information
            pass
```

Tools are prefixed when mounted, e.g., `mdb_list_parameters`, `links_describe_link`

### Critical Files

- `src/yamcs_mcp/server.py` - Main server orchestration and server mounting
- `src/yamcs_mcp/servers/base_server.py` - Base class for all servers
- `src/yamcs_mcp/servers/` - Individual server implementations
- `src/yamcs_mcp/client.py` - Yamcs connection management
- `src/yamcs_mcp/config.py` - Configuration schema and validation

### Environment Variables

Default instance name is `simulator` when using the example-simulation Docker image. Key variables:
- `YAMCS_URL` - Yamcs server URL (default: http://localhost:8090)
- `YAMCS_INSTANCE` - Yamcs instance name (default: simulator)
- `YAMCS_ENABLE_MDB` - Enable Mission Database server (default: true)
- `YAMCS_ENABLE_PROCESSOR` - Enable Processors server (default: true)
- `YAMCS_ENABLE_LINKS` - Enable Links server (default: true)
- `YAMCS_ENABLE_STORAGE` - Enable Storage server (default: true)
- `YAMCS_ENABLE_INSTANCES` - Enable Instances server (default: true)
- `YAMCS_ENABLE_ALARMS` - Enable Alarms server (default: true)
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

3. **Server composition errors**
   - Component servers extend BaseYamcsServer which extends FastMCP
   - Tools use `@self.tool()` since each component is a FastMCP server
   - Main server mounts components with prefixes

4. **"'str' object has no attribute 'eng_type'" in mdb_list_parameters**
   - The yamcs-python client returns `param.type` as a string (e.g., "float", "int")
   - Not as an object with `eng_type` attribute
   - Fixed by using `param.type` directly

5. **Link statistics reporting incorrectly**
   - Use `in_count`/`out_count` not `data_in_count`/`data_out_count`
   - Link type is in `class_name` attribute, not `type`
   - Use `enabled` attribute and convert to `disabled` as needed
   - `get_link()` returns LinkClient, call `get_info()` for Link object

6. **Instance API issues**
   - No `get_instance()` method - use `list_instances()` and find by name
   - Instance objects don't have `processor_count` - count with `list_processors()`
   - Use client methods like `start_instance()`, not instance methods

7. **Alarm API field names**
   - Use `violation_count` not `violations`
   - Use `is_ok` not `is_process_ok` for current state
   - Use `is_latched` not `is_triggered`
   - Acknowledge info may be in separate attributes (acknowledge_time, acknowledged_by, acknowledge_message)

### Testing Yamcs with Docker

Quick Yamcs setup for testing:
```bash
docker run -d --name yamcs -p 8090:8090 yamcs/example-simulation
```

This starts Yamcs with a `simulator` instance on port 8090 that includes example telemetry data.

## Key Architectural Decisions

1. **Server Composition over Component Pattern**
   - Each Yamcs subsystem is a complete FastMCP server
   - Servers are mounted with prefixes (e.g., `mdb`, `links`, `processors`)
   - Better modularity and follows FastMCP best practices

2. **Consistent Naming Convention**
   - Plural server names (LinksServer, ProcessorsServer, InstancesServer)
   - Tool names follow pattern: `prefix_action_resource`
   - Resources use URI scheme: `prefix://resource_name`

3. **Error Handling**
   - All errors handled through BaseYamcsServer._handle_error()
   - Returns consistent error structure with operation context
   - Non-fatal Yamcs connection failures (demo mode)

4. **Tool Design**
   - Tools that get single items use `describe_` prefix
   - Tools that list items use `list_` prefix
   - Control operations use verb names (enable_link, start_instance)
   - All tools return dictionaries for consistency

## Testing Commands

```bash
# Test specific servers
uv run python scripts/test-alarms-server.py
uv run python scripts/test-links-server.py

# Run integration tests
uv run pytest tests/test_integration.py -v

# Test with real Yamcs
docker run -d --name yamcs -p 8090:8090 yamcs/example-simulation
uv run yamcs-mcp
```