# Yamcs MCP Server

Enable AI assistants to interact with your Yamcs mission control system through the Model Context Protocol.

## What is This?

The Yamcs MCP Server is a **Model Context Protocol server** that bridges AI assistants (like Claude) with [Yamcs](https://yamcs.org/) mission control systems. It's not a library or API you call directly - it's a server that AI assistants use to help you operate spacecraft.

### How It Works

```mermaid
graph LR
    A[You] -->|Natural Language| B[AI Assistant]
    B -->|MCP Protocol| C[Yamcs MCP Server]
    C -->|HTTP/WebSocket| D[Yamcs]
    D -->|Telemetry/Commands| E[Spacecraft]
```

You ask questions in plain English, and the AI uses MCP tools to interact with Yamcs on your behalf.

## Key Features

✨ **Natural Language Operations** - No need to memorize commands or write code  
🛠️ **Comprehensive Tool Set** - Access all major Yamcs subsystems  
🚀 **Mission-Ready** - Monitor telemetry, manage alarms, control data links  
🔒 **Safe Operations** - Built-in validation and error handling  
📊 **Smart Interpretation** - AI understands context and presents data clearly

## Quick Example

Instead of writing code or using complex commands:

**You say:**
> "Check if we're ready for the next satellite pass"

**The AI responds:**
> All systems are ready for the pass:
> - ✅ Simulator instance: RUNNING
> - ✅ Realtime processor: Active
> - ✅ TM downlink: Enabled and connected
> - ✅ TC uplink: Enabled and connected
> - ⚠️ 2 active alarms (1 critical - BatteryVoltage low)
> 
> Recommendation: Acknowledge the battery alarm before pass starts.

## What Can It Do?

The MCP server provides tools organized into functional areas:

| Category | Capabilities |
|----------|--------------|
| **Mission Database** | Browse parameters, commands, and space systems |
| **Processors** | Monitor real-time and replay processors |
| **Data Links** | Control telemetry and command links |
| **Alarms** | View, acknowledge, and manage alarms |
| **Storage** | Access archived telemetry and files |
| **Instances** | Manage Yamcs instances and services |

## Getting Started

### 1. Install
```bash
pip install yamcs-mcp-server
```

### 2. Configure
```bash
export YAMCS_URL="http://localhost:8090"
export YAMCS_INSTANCE="simulator"
```

### 3. Connect to AI
Add to Claude Desktop or another MCP-compatible AI assistant

### 4. Start Operating
Ask questions like:
- "Show me all active alarms"
- "Is the telemetry link working?"
- "List battery-related parameters"

See the [Quick Start](quickstart.md) guide for detailed setup instructions.

## Who Is This For?

- **Mission Operators** - Simplify daily operations with natural language
- **Engineers** - Quick system checks without memorizing commands
- **Training** - Learn mission operations with AI assistance
- **Automation** - Build intelligent automation workflows

## How Is This Different?

| Traditional Approach | With MCP Server |
|---------------------|-----------------|
| Write Python scripts | Ask in plain English |
| Memorize command syntax | Describe what you want |
| Parse JSON responses | Get formatted answers |
| Handle errors manually | AI manages complexity |

## Architecture

The server uses a modular architecture with each Yamcs subsystem as an independent MCP server:

- **FastMCP Foundation** - Built on FastMCP 2.x for reliability
- **Server Composition** - Each subsystem is a complete MCP server
- **Type Safety** - Full type hints and Pydantic validation
- **Async Operations** - Non-blocking I/O throughout

Learn more in the [Architecture](architecture.md) documentation.

## Documentation

### For Users
- [Understanding MCP](mcp-concepts.md) - Learn how MCP works
- [Quick Start](quickstart.md) - Get running in minutes
- [Sample Prompts](sample-prompts.md) - Example interactions
- [Tools Reference](tools-overview.md) - Available tools

### For Developers
- [Architecture](architecture.md) - System design
- [Development](development.md) - Contributing guide
- [Configuration](configuration.md) - Advanced setup

### Help
- [Troubleshooting](troubleshooting.md) - Common issues

## Requirements

- Python 3.11+
- Yamcs 5.8.0+
- An MCP-compatible AI assistant (like Claude Desktop)

## License

MIT License - See LICENSE file for details

## Links

- [GitHub Repository](https://github.com/PaulMRamirez/yamcs-mcp-server)
- [Yamcs Documentation](https://docs.yamcs.org)
- [MCP Specification](https://modelcontextprotocol.io)