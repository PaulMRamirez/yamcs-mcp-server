# Yamcs MCP Server

Welcome to the Yamcs MCP Server documentation!

## Overview

Yamcs MCP Server is a Model Context Protocol (MCP) server that provides programmatic access to [Yamcs](https://yamcs.org/) (Yet Another Mission Control System) through a standardized interface. It enables AI assistants and other tools to interact with Yamcs instances for space mission operations.

## Features

- **Full Yamcs Integration**: Access all major Yamcs subsystems through MCP
- **Modular Server Architecture**: 
    - Mission Database (MDB) - Parameter and command definitions
    - Processors - Real-time telemetry and command execution
    - Links - Data link monitoring and control
    - Storage - Object storage operations
    - Instances - Yamcs instance management
    - Alarms - Alarm monitoring and acknowledgment
- **Server Composition**: Each subsystem is an independent FastMCP server
- **Async/Await Support**: Built on modern Python async patterns
- **Type Safety**: Full type hints and validation with Pydantic
- **Extensible**: Easy to add new servers and capabilities

## Quick Example

```python
from yamcs_mcp import YamcsMCPServer
from yamcs_mcp.config import Config

# Create configuration
config = Config.from_env()

# Create and run server
server = YamcsMCPServer(config)
await server.run()
```

## Use Cases

- **AI-Assisted Operations**: Enable AI assistants to help with mission operations
- **Automation**: Build automated workflows that interact with Yamcs
- **Integration**: Connect Yamcs to other tools through the MCP protocol
- **Analysis**: Query historical data and analyze mission performance

## Getting Started

1. [Install](installation.md) the yamcs-mcp-server package
2. [Configure](configuration.md) your Yamcs connection
3. Follow the [Quick Start](quickstart.md) guide
4. Explore the [Examples](examples.md)

## Requirements

- Python 3.11 or higher
- Yamcs 5.8.0 or higher
- Access to a Yamcs instance

## Documentation Structure

- **Getting Started**: Installation, configuration, and quick start guides
- **User Guide**: Detailed information about architecture and components
- **API Reference**: Complete API documentation
- **Development**: Contributing guidelines and development setup
- **Troubleshooting**: Common issues and solutions

## License

This project is licensed under the MIT License. See the LICENSE file for details.