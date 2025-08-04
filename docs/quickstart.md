# Quick Start

Get up and running with the Yamcs MCP Server in minutes.

## Prerequisites

- Python 3.11 or higher
- A running Yamcs instance (or use Docker)
- An AI assistant that supports MCP (like Claude Desktop)

## Step 1: Install the Server

### Using pip
```bash
pip install yamcs-mcp-server
```

### Using uv (recommended)
```bash
uv pip install yamcs-mcp-server
```

## Step 2: Start Yamcs (if needed)

If you don't have Yamcs running, use Docker for a quick setup:

```bash
docker run -d --name yamcs \
  -p 8090:8090 \
  yamcs/example-simulation
```

This starts Yamcs with a `simulator` instance that includes example telemetry.

## Step 3: Configure the MCP Server

Set environment variables to connect to Yamcs:

```bash
export YAMCS_URL="http://localhost:8090"
export YAMCS_INSTANCE="simulator"
```

## Step 4: Connect to an AI Assistant

### With Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "yamcs": {
      "command": "python",
      "args": ["-m", "yamcs_mcp.server"],
      "env": {
        "YAMCS_URL": "http://localhost:8090",
        "YAMCS_INSTANCE": "simulator"
      }
    }
  }
}
```

Restart Claude Desktop to load the configuration.

### Manual Testing

Run the server directly to see it working:

```bash
python -m yamcs_mcp.server
```

You should see:
```
Starting Yamcs MCP Server v0.2.3
Connected to Yamcs at http://localhost:8090
MCP server running on stdio transport
```

## Step 5: Try It Out!

Once connected to your AI assistant, try these prompts:

### Basic Health Check
> "Check if the MCP server is healthy and connected to Yamcs"

The AI will use the `health_check` tool to verify connectivity.

### View System Status
> "Show me all running instances and their processors"

The AI will use `instances/list_instances` and show you the system state.

### Monitor Telemetry
> "List all battery-related parameters"

The AI will use `mdb/list_parameters` to find relevant telemetry.

### Check Data Links
> "Show me the status of all data links"

The AI will use `links/list_links` to display link health.

### View Alarms
> "Are there any active alarms?"

The AI will use `alarms/list_alarms` to check for issues.

## Common Operations

### Pre-Pass Checklist
> "Run a pre-pass checklist: verify all links are enabled, check for alarms, and confirm the realtime processor is running"

### Parameter Investigation
> "Show me details about the BatteryVoltage parameter including its alarm limits"

### Link Management
> "If any telemetry links are disabled, enable them"

### Alarm Handling
> "List any unacknowledged alarms and their severity"

## Understanding the Output

When you interact with the MCP server through an AI assistant:

1. **You ask** in natural language
2. **The AI determines** which tools to use
3. **Tools execute** against Yamcs
4. **The AI formats** the response for clarity

For example:
```
You: "Is the simulator instance healthy?"

AI: The simulator instance is healthy and running. Here's the status:
- State: RUNNING
- Mission Time: 2024-01-15T12:34:56Z
- Active Processors: 1 (realtime)
- Connected Clients: 3
- Available capabilities: MDB, commanding, alarms, archiving
```

## Next Steps

### Learn More About MCP
Read [Understanding MCP](mcp-concepts.md) to learn how tools and resources work.

### Explore Available Tools
Browse the [Tools Reference](tools-overview.md) to see all available operations.

### Try Sample Prompts
Check out [Sample Prompts](sample-prompts.md) for mission control scenarios.

### Configure Advanced Features
See [Configuration](configuration.md) for authentication, components, and transport options.

## Troubleshooting

### Server Won't Start
- Verify Yamcs is running: `curl http://localhost:8090/api`
- Check environment variables are set
- Review logs for connection errors

### Tools Not Available
- Ensure the MCP server is in Claude Desktop's configuration
- Restart Claude Desktop after configuration changes
- Check that required components are enabled

### No Data Returned
- Verify the Yamcs instance name is correct
- Check that Yamcs has data (parameters, alarms, etc.)
- Ensure you have proper permissions

See the [Troubleshooting Guide](troubleshooting.md) for more help.