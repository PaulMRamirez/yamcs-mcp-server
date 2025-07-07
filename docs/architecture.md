# Yamcs MCP Server Architecture

## Overview

The Yamcs MCP Server follows a modular server-based architecture using FastMCP 2.x's server composition pattern. Each Yamcs subsystem is implemented as an independent FastMCP server that gets mounted to the main server with a prefix.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│               MCP Client (Claude, etc.)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │ MCP Protocol
┌───────────────────────────┴─────────────────────────────────┐
│                    Yamcs MCP Server                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  FastMCP Core                       │    │
│  └────────────────────────┬────────────────────────────┘    │
│  ┌────────────────────────┴────────────────────────────┐    │
│  │              Server Mount Points                    │    │
│  └─────┬───────┬───────┬───────┬───────┬───────┬───────┘    │
│        │       │       │       │       │       │            │
│     ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐         │
│     │ MDB │ │Proc │ │Link │ │Stor │ │Inst │ │Alarm│         │
│     └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘         │
└────────┼───────┼───────┼───────┼───────┼───────┼────────────┘
         │       │       │       │       │       │
┌────────┴───────┴───────┴───────┴───────┴───────┴────────────┐
│                  Yamcs Python Client                        │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/WebSocket
┌───────────────────────────┴─────────────────────────────────┐
│                     Yamcs Server                            │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Server Core (`server.py`)
- Main entry point and server orchestration
- Server mounting and prefix management
- Transport handling (stdio, HTTP, SSE)
- Global tools (health check, connection test)

### 2. Configuration (`config.py`)
- Pydantic-based configuration management
- Environment variable loading
- Validation and type safety
- Component toggle support

### 3. Client Manager (`client.py`)
- Yamcs client lifecycle management
- Connection pooling and reuse
- Authentication handling
- Error recovery and retry logic

### 4. Base Server (`servers/base_server.py`)
- Abstract base class for all servers
- Common functionality (error handling)
- Each server is a complete FastMCP instance
- Consistent error response format

## Server Modules

Each server follows the same pattern:
1. Inherits from `BaseYamcsServer` (which extends FastMCP)
2. Registers tools via `@self.tool()` decorator
3. Registers resources via `@self.resource()` decorator
4. Implements domain-specific logic

### MDB Server (`servers/mdb.py`)
- **Mount**: `/mdb`
- **Purpose**: Access to Mission Database
- **Tools**: Parameter/command listing and details
- **Resources**: `mdb://parameters`, `mdb://commands`

### Processors Server (`servers/processors.py`)
- **Mount**: `/processors`
- **Purpose**: Real-time TM/TC processing
- **Tools**: Command execution, parameter monitoring
- **Resources**: `processors://list`

### Links Server (`servers/links.py`)
- **Mount**: `/links`
- **Purpose**: Data link control
- **Tools**: Link enable/disable, status monitoring
- **Resources**: `links://status`

### Storage Server (`servers/storage.py`)
- **Mount**: `/storage`
- **Purpose**: Bucket and object management
- **Tools**: CRUD operations on objects
- **Resources**: Bucket listings

### Instances Server (`servers/instances.py`)
- **Mount**: `/instances`
- **Purpose**: Yamcs instance control
- **Tools**: Instance/service start/stop
- **Resources**: `instances://list`

### Alarms Server (`servers/alarms.py`)
- **Mount**: `/alarms`
- **Purpose**: Alarm monitoring and management
- **Tools**: List/acknowledge/shelve alarms
- **Resources**: `alarms://list`

## Design Patterns

### 1. Server Composition Pattern
Using FastMCP's mount feature to compose multiple servers:
```python
mcp = FastMCP("YamcsServer")
mdb_server = MDBServer(client_manager, config)
mcp.mount(mdb_server, prefix="mdb")
processors_server = ProcessorsServer(client_manager, config)
mcp.mount(processors_server, prefix="processors")
```

This results in tools being prefixed, e.g.:
- `mdb_list_parameters`
- `processors_describe_processor`

### 2. Async Context Manager
Client connections are managed using async context managers:
```python
async with self.client_manager.get_client() as client:
    # Use client
    pass  # Client automatically closed
```

### 3. Error Handling Pattern
Consistent error handling across all components:
```python
try:
    # Operation
    return {"success": True, ...}
except Exception as e:
    return self._handle_error("operation_name", e)
```

### 4. Resource URI Pattern
Resources follow a consistent URI scheme:
- `mdb://parameters` - List all parameters
- `processors://list` - List all processors
- `links://status` - Show link status
- `instances://list` - List all instances
- `alarms://list` - Show active alarms

## Configuration Management

The server uses a hierarchical configuration system:
1. Default values in Pydantic models
2. Environment variables (with prefix)
3. `.env` file support
4. Runtime configuration objects

## Error Handling

Custom exception hierarchy:
- `YamcsError` - Base exception
- `YamcsConnectionError` - Connection failures
- `YamcsAuthenticationError` - Auth failures
- `YamcsNotFoundError` - Resource not found
- `YamcsValidationError` - Input validation
- `YamcsOperationError` - Operation failures

## Logging

Structured logging using `structlog`:
- JSON-formatted logs for production
- Pretty console output for development
- Correlation IDs for request tracking
- Component-specific loggers

## Performance Considerations

1. **Connection Pooling**: Reuse Yamcs client connections
2. **Async Operations**: Non-blocking I/O throughout
3. **Pagination**: Limit results to prevent memory issues
4. **Caching**: Consider caching MDB data (future enhancement)

## Security

1. **Authentication**: Support for Yamcs username/password
2. **Input Validation**: Pydantic models for all inputs
3. **Error Sanitization**: Don't leak sensitive info in errors
4. **Transport Security**: HTTPS support for Yamcs connection

## Extensibility

Adding new servers:
1. Create new server class inheriting from `BaseYamcsServer`
2. Implement `_register_tools()` and optionally `_register_resources()`
3. Mount the server in `YamcsMCPServer._initialize_servers()`
4. Add configuration toggle (e.g., `YAMCS_ENABLE_NEWSERVER`)

Example:
```python
class NewServer(BaseYamcsServer):
    def __init__(self, client_manager, config):
        super().__init__("New", client_manager, config)
        self._register_tools()

# In server.py
if self.config.yamcs.enable_new:
    new_server = NewServer(self.client_manager, self.config.yamcs)
    self.mcp.mount(new_server, prefix="new")
```

## Testing Strategy

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Mock Strategy**: Mock Yamcs client for predictable testing
4. **Coverage Goal**: >80% code coverage
