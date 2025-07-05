# Claude Desktop Setup for Yamcs MCP Server

## Quick Setup

1. **Copy this configuration** to your Claude Desktop settings:

```json
{
  "mcp-servers": {
    "yamcs": {
      "command": "/Users/pramirez/.local/bin/uv",
      "args": ["run", "yamcs-mcp"],
      "cwd": "/Users/pramirez/Development/ClaudeCode/yamcs-mcp-server",
      "env": {
        "YAMCS_URL": "http://localhost:8090",
        "YAMCS_INSTANCE": "simulator",
        "PYTHONWARNINGS": "ignore",
        "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION": "python"
      }
    }
  }
}
```

2. **Important**: The `cwd` parameter MUST be set to the yamcs-mcp-server directory for the server to work correctly.

3. **Restart Claude Desktop** after updating the configuration.

## Alternative Configurations

### Option 1: Using Python Script Directly
```json
{
  "mcp-servers": {
    "yamcs": {
      "command": "/Users/pramirez/Development/ClaudeCode/yamcs-mcp-server/.venv/bin/python",
      "args": ["/Users/pramirez/Development/ClaudeCode/yamcs-mcp-server/run-yamcs-mcp.py"],
      "env": {
        "YAMCS_URL": "http://localhost:8090",
        "YAMCS_INSTANCE": "simulator"
      }
    }
  }
}
```

### Option 2: Using Wrapper Script
```json
{
  "mcp-servers": {
    "yamcs": {
      "command": "/Users/pramirez/Development/ClaudeCode/yamcs-mcp-server/yamcs-mcp-wrapper.sh",
      "env": {
        "YAMCS_URL": "http://localhost:8090",
        "YAMCS_INSTANCE": "simulator"
      }
    }
  }
}
```

## Troubleshooting

1. **Check the logs**: `~/Library/Logs/Claude/mcp-server-yamcs.log`
2. **Verify Yamcs is running**: `curl http://localhost:8090/api`
3. **Test the server manually**: 
   ```bash
   cd /Users/pramirez/Development/ClaudeCode/yamcs-mcp-server
   /Users/pramirez/.local/bin/uv run yamcs-mcp
   ```

## Environment Variables

- `YAMCS_URL`: URL of your Yamcs server (default: http://localhost:8090)
- `YAMCS_INSTANCE`: Yamcs instance name (default: simulator)
- `YAMCS_USERNAME`: Optional username for authentication
- `YAMCS_PASSWORD`: Optional password for authentication
- `PYTHONWARNINGS`: Set to "ignore" to suppress Python warnings
- `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION`: Set to "python" to reduce protobuf warnings