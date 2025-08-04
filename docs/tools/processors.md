# Processor Tools

Processor tools manage real-time and replay processors for telemetry and command processing.

## Available Tools

| Tool | Purpose |
|------|---------|
| `processors/list_processors` | List all processors and their states |
| `processors/describe_processor` | Get detailed processor information |
| `processors/delete_processor` | Delete a processor |

## Tools Reference

### processors/list_processors

List all available processors in an instance.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `instance` | string | No | Yamcs instance name (uses default if not specified) |

**Example prompts:**
- "List all processors"
- "Show me what processors are running"
- "Check processor status"

**Sample response:**
```json
{
  "instance": "simulator",
  "count": 2,
  "processors": [
    {
      "name": "realtime",
      "state": "RUNNING",
      "mission_time": "2024-01-15T12:34:56Z",
      "type": "realtime",
      "replay": false,
      "persistent": true
    },
    {
      "name": "replay-20240115",
      "state": "PAUSED",
      "mission_time": "2024-01-15T08:00:00Z",
      "type": "Archive",
      "replay": true,
      "persistent": false
    }
  ]
}
```

### processors/describe_processor

Get comprehensive information about a specific processor.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `processor` | string | Yes | Processor name (e.g., "realtime") |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Describe the realtime processor"
- "Show me details about the replay processor"
- "Is the realtime processor configured for commanding?"

**Sample response:**
```json
{
  "name": "realtime",
  "instance": "simulator",
  "state": "RUNNING",
  "type": "realtime",
  "mission_time": "2024-01-15T12:34:56Z",
  "config": {
    "persistent": true,
    "protected": false,
    "synchronous": false,
    "checkCommandClearance": true,
    "recordLocalValues": true
  },
  "replay": {
    "is_replay": false
  },
  "services": [
    "tm_realtime",
    "tc_realtime",
    "parameter_cache",
    "command_history"
  ],
  "statistics": {
    "tm_count": 1000000,
    "tc_count": 150,
    "parameter_count": 500,
    "client_count": 3
  }
}
```

### processors/delete_processor

Delete a non-persistent processor.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `processor` | string | Yes | Processor name to delete |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Delete the test-processor"
- "Remove the replay processor from yesterday"
- "Clean up the temporary processor"

**Sample response:**
```json
{
  "success": true,
  "processor": "replay-20240114",
  "instance": "simulator",
  "message": "Processor 'replay-20240114' deleted successfully"
}
```

## Resources

### processors://list

Provides a formatted summary of all processors and their current states.

**Example prompt:** "Show me the processors resource"

## Common Use Cases

### Checking System Status

> "Is the realtime processor running?"

The AI will use `processors/describe_processor` to check the state

### Understanding Processing Configuration

> "How is the realtime processor configured for commanding?"

The AI will use `processors/describe_processor` to show configuration details

### Managing Replay Sessions

> "List all replay processors and their time ranges"

The AI will use `processors/list_processors` to show replay processors

### Cleanup Operations

> "Delete all stopped replay processors"

The AI will:
1. Use `processors/list_processors` to find stopped processors
2. Use `processors/delete_processor` for each non-persistent stopped processor

## Processor States

Processors can be in the following states:

| State | Description |
|-------|-------------|
| `RUNNING` | Actively processing data |
| `PAUSED` | Temporarily suspended |
| `STOPPED` | Halted, can be restarted |
| `ERROR` | Failed due to error |
| `STARTING` | In the process of starting |
| `STOPPING` | In the process of stopping |

## Processor Types

| Type | Description | Persistent | Replay |
|------|-------------|------------|--------|
| `realtime` | Processes live telemetry/commands | Yes | No |
| `Archive` | Replays historical data | No | Yes |
| `synthetic` | Generates simulated data | Varies | No |

## Tips

1. **Check before deleting** - Only non-persistent processors can be deleted
2. **Monitor mission time** - Compare processor time with real time for delays
3. **Verify services** - Check that required services are listed
4. **Watch client count** - High client counts may indicate heavy usage
5. **Protected processors** - Some processors cannot be modified