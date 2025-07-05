# Quick Start

This guide will help you get started with Yamcs MCP Server in minutes.

## Prerequisites

- Yamcs MCP Server installed ([Installation Guide](installation.md))
- A running Yamcs instance
- Basic familiarity with Yamcs concepts

## Basic Setup

### 1. Configure Environment

Set up your environment variables:

```bash
export YAMCS_URL="http://localhost:8090"
export YAMCS_INSTANCE="simulator"
```

### 2. Start the Server

Run the MCP server:

```bash
python -m yamcs_mcp
```

You should see output like:

```
2024-01-15 10:00:00 [INFO] Starting Yamcs MCP Server v0.1.0
2024-01-15 10:00:01 [INFO] Connected to Yamcs at http://localhost:8090
2024-01-15 10:00:01 [INFO] MCP server running on stdio transport
```

### 3. Test Basic Operations

In another terminal, you can interact with the server using an MCP client:

```python
# List available tools
client.list_tools()

# Get server health
result = await client.call_tool("health_check")
print(result)
# Output: {"status": "healthy", "yamcs_url": "http://localhost:8090", ...}

# List parameters from MDB
result = await client.call_tool("mdb_list_parameters", {
    "namespace": "/YSS/SIMULATOR"
})
```

## Common Use Cases

### Querying Parameters

```python
# Get parameter details
param_info = await client.call_tool("mdb_get_parameter", {
    "parameter": "/YSS/SIMULATOR/BatteryVoltage"
})

# Get current value
current_value = await client.call_tool("processor_get_parameter_value", {
    "parameter": "/YSS/SIMULATOR/BatteryVoltage"
})
```

### Historical Data

```python
# Query historical parameter data
history = await client.call_tool("archive_query_parameters", {
    "parameters": ["/YSS/SIMULATOR/BatteryVoltage"],
    "start": "2024-01-01T00:00:00Z",
    "stop": "2024-01-01T01:00:00Z"
})
```

### Command Execution

```python
# Issue a command
result = await client.call_tool("processor_issue_command", {
    "command": "/YSS/SIMULATOR/SWITCH_BATTERY_ON",
    "dry_run": True  # Validate without executing
})
```

### Link Management

```python
# List all links
links = await client.call_tool("link_list_links")

# Enable a link
await client.call_tool("link_enable_link", {
    "link": "TM_REALTIME"
})
```

## Using with AI Assistants

The MCP server is designed to work with AI assistants that support the Model Context Protocol:

1. Configure your AI assistant to connect to the MCP server
2. The assistant will have access to all Yamcs tools
3. You can ask natural language questions like:
   - "What's the current battery voltage?"
   - "Show me temperature data from yesterday"
   - "Enable the telemetry downlink"

## Configuration Options

See the [Configuration Guide](configuration.md) for detailed options:

- Authentication setup
- Component selection
- Transport options (stdio, HTTP)
- Logging configuration

## Troubleshooting

If you encounter issues:

1. Check Yamcs connectivity:
   ```bash
   python -m yamcs_mcp test-connection
   ```

2. Enable debug logging:
   ```bash
   export LOG_LEVEL=DEBUG
   python -m yamcs_mcp
   ```

3. See the [Troubleshooting Guide](troubleshooting.md) for common issues

## Next Steps

- Explore [Architecture](architecture.md) to understand how components work
- Read about specific [Components](components/mdb.md)
- Check out more [Examples](examples.md)
- Learn about [Development](development.md) if you want to contribute