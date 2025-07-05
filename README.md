# Yamcs MCP Server

A comprehensive Model Context Protocol (MCP) server for Yamcs (Yet Another Mission Control System) that exposes Yamcs capabilities as standardized MCP tools and resources.

## Overview

The Yamcs MCP Server enables AI assistants to interact with mission control systems through natural language by providing a bridge between MCP-compatible clients and Yamcs instances. It implements the MCP protocol using FastMCP 2.x with a modular component architecture.

## Features

- **Mission Database (MDB)**: Access to parameters, commands, algorithms, and space systems
- **TM/TC Processing**: Real-time telemetry monitoring and command execution
- **Archive**: Historical data queries for parameters, events, and packets
- **Link Management**: Monitor and control data links
- **Object Storage**: Manage buckets and objects in Yamcs storage
- **Instance Management**: Control Yamcs instances and services

## Installation

### Prerequisites

- Python 3.12 or higher
- Yamcs server instance (local or remote)
- uv package manager (recommended) or pip

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/USERNAME/yamcs-mcp-server.git
cd yamcs-mcp-server

# Install dependencies
uv sync

# Run the server
uv run yamcs-mcp
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/USERNAME/yamcs-mcp-server.git
cd yamcs-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Run the server
yamcs-mcp
```

## Configuration

The server can be configured using environment variables or a `.env` file:

```bash
# Yamcs connection settings
YAMCS_URL=http://localhost:8090
YAMCS_INSTANCE=simulator
YAMCS_USERNAME=admin
YAMCS_PASSWORD=password

# Component toggles
YAMCS_ENABLE_MDB=true
YAMCS_ENABLE_PROCESSOR=true
YAMCS_ENABLE_ARCHIVE=true
YAMCS_ENABLE_LINKS=true
YAMCS_ENABLE_STORAGE=true
YAMCS_ENABLE_INSTANCES=true

# Server settings
MCP_TRANSPORT=stdio
MCP_HOST=127.0.0.1
MCP_PORT=8000
```

## Usage

### With Claude Desktop

Add the server to your Claude Desktop configuration:

```json
{
  "mcp-servers": {
    "yamcs": {
      "command": "/Users/pramirez/Development/ClaudeCode/yamcs-mcp-server/run-yamcs-mcp.py",
      "env": {
        "YAMCS_URL": "http://localhost:8090",
        "YAMCS_INSTANCE": "simulator"
      }
    }
  }
}
```

Alternative configurations:

1. **Using the wrapper script** (recommended):
```json
{
  "mcp-servers": {
    "yamcs": {
      "command": "/path/to/yamcs-mcp-server/yamcs-mcp-wrapper.sh",
      "env": {
        "YAMCS_URL": "http://localhost:8090",
        "YAMCS_INSTANCE": "simulator"
      }
    }
  }
}
```

2. **Using Python directly**:
```json
{
  "mcp-servers": {
    "yamcs": {
      "command": "python3",
      "args": ["/path/to/yamcs-mcp-server/run_server.py"],
      "env": {
        "YAMCS_URL": "http://localhost:8090",
        "YAMCS_INSTANCE": "simulator"
      }
    }
  }
}
```

3. **Using uv with full path**:
```json
{
  "mcp-servers": {
    "yamcs": {
      "command": "/Users/pramirez/.local/bin/uv",
      "args": ["run", "yamcs-mcp"],
      "cwd": "/Users/pramirez/Development/ClaudeCode/yamcs-mcp-server",
      "env": {
        "YAMCS_URL": "http://localhost:8090",
        "YAMCS_INSTANCE": "simulator"
      }
    }
  }
}
```

### Available Tools

The server exposes numerous tools organized by component:

#### MDB Tools
- `mdb_list_parameters` - List available parameters
- `mdb_get_parameter` - Get parameter details
- `mdb_list_commands` - List available commands
- `mdb_get_command` - Get command details
- And more...

#### Processing Tools
- `processor_list_processors` - List available processors
- `processor_issue_command` - Issue a command
- `processor_subscribe_parameters` - Subscribe to parameter updates
- And more...

See the full documentation for a complete list of available tools.

## Development

### Setting up the development environment

```bash
# Install development dependencies
uv sync --all-extras

# Install pre-commit hooks
pre-commit install

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run mypy src/
```

### Project Structure

```
yamcs-mcp-server/
├── src/
│   └── yamcs_mcp/
│       ├── server.py           # Main server entry point
│       ├── components/         # MCP components
│       │   ├── mdb.py         # Mission Database
│       │   ├── processor.py   # TM/TC Processing
│       │   ├── archive.py     # Archive queries
│       │   ├── links.py       # Link management
│       │   ├── storage.py     # Object storage
│       │   └── instances.py   # Instance management
│       └── utils/             # Utilities
├── tests/                     # Test suite
├── docs/                      # Documentation
└── examples/                  # Usage examples
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastMCP](https://gofastmcp.com/)
- Powered by [Yamcs](https://yamcs.org/)