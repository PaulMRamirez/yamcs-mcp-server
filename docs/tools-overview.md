# Tools & Resources Reference

This reference describes all tools and resources available through the Yamcs MCP Server. Tools are functions that AI assistants can call to interact with your Yamcs instance.

## Available Tool Categories

| Category | Description | Tool Count |
|----------|-------------|------------|
| [Server](#server-tools) | Health checks and connection testing | 2 |
| [MDB](tools/mdb.md) | Mission Database queries | 5 |
| [Processors](tools/processors.md) | Real-time processing control | 3 |
| [Links](tools/links.md) | Data link management | 4 |
| [Storage](tools/storage.md) | Object storage operations | 5 |
| [Instances](tools/instances.md) | Yamcs instance control | 4 |
| [Alarms](tools/alarms.md) | Alarm monitoring and management | 7 |

## Server Tools

These tools are always available regardless of which components are enabled.

### health_check

Check the overall health and configuration of the MCP server.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| - | - | - | No parameters |

**Example prompt:** "Check if the MCP server is healthy"

**Returns:** Server status, version, Yamcs URL, and enabled components

### test_connection

Test the connection to the Yamcs server.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| - | - | - | No parameters |

**Example prompt:** "Verify the connection to Yamcs is working"

**Returns:** Connection status and Yamcs server information

## Quick Reference

### Most Common Tools

| Tool | Purpose | Example Prompt |
|------|---------|----------------|
| `mdb/list_parameters` | Find telemetry parameters | "Show me all battery parameters" |
| `processors/describe_processor` | Check processor status | "Is the realtime processor running?" |
| `links/list_links` | View all data links | "Show me the status of all links" |
| `alarms/list_alarms` | View active alarms | "What alarms are currently active?" |
| `instances/list_instances` | List Yamcs instances | "What instances are available?" |

### Tool Naming Pattern

All tools follow a consistent naming convention:
- **List operations:** `category/list_items` (e.g., `mdb/list_parameters`)
- **Get details:** `category/describe_item` (e.g., `links/describe_link`)
- **Actions:** `category/verb_item` (e.g., `links/enable_link`)

## Resources

Resources provide pre-formatted information summaries:

| Resource URI | Description |
|--------------|-------------|
| `mdb://parameters` | Summary of parameters in the Mission Database |
| `mdb://commands` | Summary of commands in the Mission Database |
| `processors://list` | List of all processors with their states |
| `links://status` | Current status of all data links |
| `storage://overview` | Storage usage overview |
| `instances://list` | Summary of all Yamcs instances |
| `alarms://list` | Summary of active alarms |

## Using Tools Effectively

### 1. Start Broad, Then Narrow

First get an overview:
> "List all processors"

Then get details:
> "Describe the realtime processor"

### 2. Combine Related Operations

Instead of multiple requests:
> "Check if the simulator instance is running, list its processors, and show any active alarms"

### 3. Use Filters When Available

Many list tools support filtering:
> "List parameters in the /YSS/SIMULATOR system that contain 'voltage'"

### 4. Check Before Acting

Before making changes:
> "Show me the current status of the tm_realtime link before enabling it"

## Error Handling

All tools return consistent error structures:

```json
{
  "error": true,
  "message": "Human-readable error description",
  "operation": "The tool that failed",
  "details": "Additional context if available"
}
```

Common error types:
- **Connection errors:** Yamcs server unreachable
- **Not found:** Requested resource doesn't exist
- **Permission denied:** Insufficient privileges
- **Validation errors:** Invalid parameters provided

## Component Dependencies

Some tools require specific Yamcs components:

| Required Component | Tools Affected |
|-------------------|----------------|
| Mission Database | All MDB tools |
| Command capability | Command execution tools |
| Archive | Historical data queries |
| Storage | Bucket and object operations |

## Next Steps

- Explore specific tool categories:
  - [MDB Tools](tools/mdb.md) - Parameter and command queries
  - [Processor Tools](tools/processors.md) - Real-time processing
  - [Link Tools](tools/links.md) - Data link control
  - [Storage Tools](tools/storage.md) - File operations
  - [Instance Tools](tools/instances.md) - Instance management
  - [Alarm Tools](tools/alarms.md) - Alarm handling
- Review [Sample Prompts](sample-prompts.md) for practical examples
- Check [Configuration](configuration.md) to enable/disable components