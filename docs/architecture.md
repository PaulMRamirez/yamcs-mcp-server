# Yamcs MCP Server Architecture

## Overview

The Yamcs MCP Server follows a modular component-based architecture using FastMCP 2.x's composition pattern. This design allows for clean separation of concerns and easy extensibility.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Client (Claude, etc.)              │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP Protocol
┌─────────────────────┴───────────────────────────────────────┐
│                    Yamcs MCP Server                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  FastMCP Core                        │   │
│  └─────────────────────┬───────────────────────────────┘   │
│  ┌─────────────────────┴───────────────────────────────┐   │
│  │              Component Manager                       │   │
│  └──┬────────┬────────┬────────┬────────┬────────┬────┘   │
│     │        │        │        │        │        │         │
│  ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐       │
│  │ MDB │ │Proc │ │Arch │ │Link │ │Stor │ │Inst │       │
│  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘       │
└─────┼───────┼───────┼───────┼───────┼───────┼───────────┘
      │       │       │       │       │       │
┌─────┴───────┴───────┴───────┴───────┴───────┴───────────┐
│                  Yamcs Python Client                      │
└─────────────────────┬─────────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────┴─────────────────────────────────────┐
│                     Yamcs Server                           │
└───────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Server Core (`server.py`)
- Main entry point and server orchestration
- Component registration and lifecycle management
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

### 4. Base Component (`components/base.py`)
- Abstract base class for all components
- Common functionality (error handling, logging)
- Tool and resource registration patterns
- Health check implementation

## Component Modules

Each component follows the same pattern:
1. Inherits from `BaseYamcsComponent`
2. Registers tools via `@self.tool()` decorator
3. Registers resources via `@self.resource()` decorator
4. Implements domain-specific logic

### MDB Component (`components/mdb.py`)
- **Purpose**: Access to Mission Database
- **Tools**: Parameter/command listing and details
- **Resources**: Parameter and command catalogs

### Processor Component (`components/processor.py`)
- **Purpose**: Real-time TM/TC processing
- **Tools**: Command execution, parameter monitoring
- **Resources**: Processor status, real-time data

### Archive Component (`components/archive.py`)
- **Purpose**: Historical data queries
- **Tools**: Parameter/event/packet history
- **Resources**: Time-based data views

### Link Management Component (`components/links.py`)
- **Purpose**: Data link control
- **Tools**: Link enable/disable, status monitoring
- **Resources**: Link status and statistics

### Object Storage Component (`components/storage.py`)
- **Purpose**: Bucket and object management
- **Tools**: CRUD operations on objects
- **Resources**: Bucket listings

### Instance Management Component (`components/instances.py`)
- **Purpose**: Yamcs instance control
- **Tools**: Instance/service start/stop
- **Resources**: Instance and service listings

## Design Patterns

### 1. Composition Pattern
Using FastMCP's composition feature to combine multiple components into a single server:
```python
server = FastMCP("YamcsServer")
server.add_component(MDBComponent(...))
server.add_component(ProcessorComponent(...))
```

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
- `mdb://parameters` - MDB parameters
- `processor://status/realtime` - Processor status
- `archive://events/2024-01-01/2024-01-31` - Archive data

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

Adding new components:
1. Create new component class inheriting from `BaseYamcsComponent`
2. Implement `_register_tools()` and `_register_resources()`
3. Add component to server initialization
4. Add configuration toggle

## Testing Strategy

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Mock Strategy**: Mock Yamcs client for predictable testing
4. **Coverage Goal**: >80% code coverage