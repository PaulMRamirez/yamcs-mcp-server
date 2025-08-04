# Yamcs MCP Server

A comprehensive Model Context Protocol (MCP) server for Yamcs (Yet Another Mission Control System) that exposes Yamcs capabilities as standardized MCP tools and resources.

## Overview

The Yamcs MCP Server enables AI assistants to interact with mission control systems through natural language by providing a bridge between MCP-compatible clients and Yamcs instances. It implements the MCP protocol using FastMCP 2.x with a modular component architecture.

## Features

- **Mission Database (MDB)**: Access to parameters, commands, algorithms, and space systems
- **TM/TC Processing**: Real-time telemetry monitoring and command execution
- **Link Management**: Monitor and control data links
- **Object Storage**: Manage buckets and objects in Yamcs storage
- **Instance Management**: Control Yamcs instances and services
- **Alarm Management**: Monitor and acknowledge alarms with summary statistics

## Installation

### Prerequisites

- Python 3.12 or higher
- Yamcs server instance (local or remote)
- uv package manager (recommended) or pip

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/PaulMRamirez/yamcs-mcp-server.git
cd yamcs-mcp-server

# Install dependencies
uv sync

# Run the server
uv run yamcs-mcp
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/PaulMRamirez/yamcs-mcp-server.git
cd yamcs-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Run the server
yamcs-mcp
```

### Running Yamcs

You'll need a running Yamcs instance. The easiest way is using Docker:

```bash
docker run -d --name yamcs -p 8090:8090 yamcs/example-simulation
```

This will start Yamcs with a `simulator` instance that includes example telemetry data.

## Configuration

The server can be configured using environment variables or a `.env` file:

```bash
# Yamcs connection settings
YAMCS_URL=http://localhost:8090
YAMCS_INSTANCE=simulator
YAMCS_USERNAME=admin
YAMCS_PASSWORD=password

# Server toggles
YAMCS_ENABLE_MDB=true
YAMCS_ENABLE_PROCESSOR=true
YAMCS_ENABLE_LINKS=true
YAMCS_ENABLE_STORAGE=true
YAMCS_ENABLE_INSTANCES=true
YAMCS_ENABLE_ALARMS=true
YAMCS_ENABLE_COMMANDS=true

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
      "command": "uv",
      "args": ["--directory", "/path/to/yamcs-mcp-server", "run", "yamcs-mcp"],
      "env": {
        "YAMCS_URL": "http://localhost:8090",
        "YAMCS_INSTANCE": "simulator"
      }
    }
  }
}
```

**Important**:
- Replace `/path/to/yamcs-mcp-server` with the actual path to your yamcs-mcp-server directory
- The `--directory` argument is required for uv to find the correct project
- If `uv` is not in your PATH, use the full path to uv (e.g., `/Users/PaulMRamirez/.local/bin/uv`)

### Available Tools

The server exposes numerous tools organized by server:

#### MDB Tools
- `mdb_list_parameters` - List available parameters
- `mdb_describe_parameter` - Get parameter details
- `mdb_list_commands` - List available commands
- `mdb_describe_command` - Get command details
- `mdb_list_space_systems` - List space systems
- `mdb_describe_space_system` - Get space system details

#### Processor Tools
- `processors_list_processors` - List available processors
- `processors_describe_processor` - Get processor details
- `processors_delete_processor` - Delete a processor
- `processors_issue_command` - Issue a command
- `processors_subscribe_parameters` - Subscribe to parameter updates

#### Link Tools
- `links_list_links` - List all data links
- `links_describe_link` - Get detailed link information
- `links_enable_link` - Enable a data link
- `links_disable_link` - Disable a data link

#### Instance Tools
- `instances_list_instances` - List Yamcs instances
- `instances_describe_instance` - Get instance details
- `instances_start_instance` - Start an instance
- `instances_stop_instance` - Stop an instance

#### Storage Tools
- `storage_list_buckets` - List storage buckets
- `storage_list_objects` - List objects in a bucket
- `storage_upload_object` - Upload an object
- `storage_download_object` - Download an object

#### Alarm Tools
- `alarms_list_alarms` - List active alarms with summary counts
- `alarms_describe_alarm` - Get detailed alarm information
- `alarms_acknowledge_alarm` - Acknowledge an alarm
- `alarms_shelve_alarm` - Temporarily shelve an alarm
- `alarms_unshelve_alarm` - Unshelve an alarm
- `alarms_clear_alarm` - Clear an alarm
- `alarms_read_log` - Read alarm history

#### Command Tools
- `commands_list_commands` - List available commands for execution
- `commands_describe_command` - Get detailed command information
- `commands_run_command` - Execute a command (supports dry-run)
- `commands_read_log` - Read command execution history

### Available Resources

The server also provides read-only resources:

- `mdb://parameters` - List all parameters
- `processors://list` - List all processors with details
- `links://status` - Show status of all links
- `instances://list` - List all instances with details
- `alarms://list` - Show active alarms summary

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

### Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=yamcs_mcp --cov-report=html

# Run specific test file
uv run pytest tests/test_server.py

# Run with verbose output
uv run pytest -v
```

#### Testing Without a Yamcs Server

The server can run in demo mode without connecting to a real Yamcs server:

```bash
# Run in demo mode (will show a warning about connection failure but continue)
uv run python -m yamcs_mcp.server

# Or use the demo script
uv run python run_demo.py
```

### Project Structure

```
yamcs-mcp-server/
├── src/
│   └── yamcs_mcp/
│       ├── server.py           # Main server entry point
│       ├── servers/            # MCP servers
│       │   ├── base_server.py # Base class for all servers
│       │   ├── mdb.py         # Mission Database
│       │   ├── processors.py  # TM/TC Processing
│       │   ├── links.py       # Link management
│       │   ├── storage.py     # Object storage
│       │   ├── instances.py   # Instance management
│       │   └── alarms.py      # Alarm management
│       ├── client.py          # Yamcs client management
│       ├── config.py          # Configuration
│       └── types.py           # Type definitions
├── tests/                     # Test suite
├── scripts/                   # Test scripts
└── CLAUDE.md                  # AI assistant guidance
```

## Troubleshooting

### Common Issues

#### "Input validation error" when executing commands

**Problem:** Getting errors like `'{"voltage_num": 1}' is not valid under any of the given schemas`

**Solution:** The `commands/run_command` tool now accepts both formats. The server will automatically parse JSON strings to objects. 

Both formats are now supported:

✅ **Args as object (preferred):**
```json
{
  "command": "/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF",
  "args": {"voltage_num": 1}
}
```

✅ **Args as JSON string (automatically parsed):**
```json
{
  "command": "/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF",
  "args": "{\"voltage_num\": 1}"
}
```

✅ **Command without arguments:**
```json
{
  "command": "/TSE/simulator/get_identification"
}
```

✅ **Multiple arguments:**
```json
{
  "command": "/YSS/SIMULATOR/SET_HEATER",
  "args": {
    "heater_id": 2,
    "temperature": 25.5,
    "duration": 300
  }
}
```

#### Connection to Yamcs fails

**Problem:** Server can't connect to Yamcs at startup

**Solution:** 
1. Ensure Yamcs is running: `docker ps | grep yamcs`
2. Check the URL is correct: `curl http://localhost:8090/api`
3. The server will continue in demo mode even if Yamcs is unavailable

#### Enum serialization errors

**Problem:** Errors about unable to serialize enum types

**Solution:** This has been fixed in the latest version. Update to the latest version of the server.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastMCP](https://gofastmcp.com/)
- Powered by [Yamcs](https://yamcs.org/)
