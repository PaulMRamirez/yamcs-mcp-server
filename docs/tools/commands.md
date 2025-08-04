# Command Tools

Command tools provide execution and management of spacecraft commands through Yamcs.

## Available Tools

| Tool | Purpose |
|------|---------|
| `commands/list_commands` | List available commands for execution |
| `commands/describe_command` | Get detailed command information |
| `commands/run_command` | Execute a command |
| `commands/read_log` | Read command execution history |

## Tools Reference

### commands/list_commands

List available commands that can be executed.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `instance` | string | No | Yamcs instance (uses default if not specified) |
| `system` | string | No | Filter by space system (e.g., "/YSS/SIMULATOR") |
| `search` | string | No | Search pattern for command names |
| `limit` | integer | No | Maximum commands to return (default: 100) |

**Example prompts:**
- "List all available commands"
- "Show me power system commands"
- "Find commands with 'voltage' in the name"

**Sample response:**
```json
{
  "instance": "simulator",
  "count": 25,
  "commands": [
    {
      "name": "SWITCH_VOLTAGE_ON",
      "qualified_name": "/YSS/SIMULATOR/SWITCH_VOLTAGE_ON",
      "description": "Switch voltage bus on",
      "abstract": false,
      "significance": "NORMAL"
    }
  ]
}
```

### commands/describe_command

Get comprehensive information about a command including its arguments.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `command` | string | Yes | Command qualified name |
| `instance` | string | No | Yamcs instance |

**Example prompts:**
- "Describe the SWITCH_VOLTAGE_ON command"
- "What arguments does the SET_MODE command need?"
- "Show me details about the ENABLE_HEATER command"

**Sample response:**
```json
{
  "name": "SWITCH_VOLTAGE_ON",
  "qualified_name": "/YSS/SIMULATOR/SWITCH_VOLTAGE_ON",
  "description": "Switch voltage bus on",
  "abstract": false,
  "arguments": [
    {
      "name": "voltage_num",
      "description": "Voltage bus number (1-4)",
      "type": "integer",
      "required": true,
      "initial_value": "1",
      "valid_range": {
        "min": 1,
        "max": 4
      }
    }
  ],
  "significance": {
    "consequence_level": "NORMAL",
    "reason": "Routine power management"
  }
}
```

### commands/run_command

Execute a command on the spacecraft.

**Note:** The `args` parameter accepts both JSON objects and JSON strings. If a string is provided, it will be automatically parsed.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `command` | string | Yes | Command qualified name to execute |
| `args` | object/string | No | Command arguments as a dictionary or JSON string |
| `processor` | string | No | Target processor (default: "realtime") |
| `dry_run` | boolean | No | Validate without execution (default: false) |
| `comment` | string | No | Optional comment to attach to the command |
| `sequence_number` | integer | No | Optional command sequence number |
| `instance` | string | No | Yamcs instance |

**Format Examples:**

✅ **Example 1: Command WITH arguments** - args as object (preferred):
```json
{
  "command": "/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF",
  "args": {"voltage_num": 1},
  "comment": "Turning off voltage channel 1"
}
```

✅ **Example 2: Command WITH arguments** - args as JSON string (also works):
```json
{
  "command": "/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF",
  "args": "{\"voltage_num\": 1}",
  "comment": "Turning off voltage channel 1"
}
```

✅ **Example 3: Multiple arguments**:
```json
{
  "command": "/YSS/SIMULATOR/SET_HEATER",
  "args": {
    "heater_id": 2,
    "temperature": 25.5,
    "duration": 300
  },
  "comment": "Setting heater 2 to 25.5°C for 5 minutes"
}
```

✅ **Example 4: Command WITHOUT arguments**:
```json
{
  "command": "/TSE/simulator/get_identification",
  "comment": "Requesting system identification"
}
```

**Important Notes:**
- The tool now accepts both JSON objects and JSON strings for the `args` parameter
- JSON strings will be automatically parsed to objects
- Use `describe_command` first to see what arguments are required
- Omit the `args` field entirely for commands that take no arguments

**Example prompts:**
- "Execute SWITCH_VOLTAGE_ON with voltage_num=2"
- "Run the ENABLE_HEATER command in dry-run mode"
- "Send SET_MODE command with mode='SAFE' to the realtime processor with comment 'Entering safe mode for maintenance'"

**Sample response (dry run):**
```json
{
  "success": true,
  "dry_run": true,
  "command": "/YSS/SIMULATOR/SWITCH_VOLTAGE_ON",
  "processor": "realtime",
  "instance": "simulator",
  "valid": true,
  "message": "Command '/YSS/SIMULATOR/SWITCH_VOLTAGE_ON' validated successfully",
  "comment": null
}
```

**Sample response (execution):**
```json
{
  "success": true,
  "dry_run": false,
  "command": "/YSS/SIMULATOR/SWITCH_VOLTAGE_ON",
  "processor": "realtime",
  "instance": "simulator",
  "command_id": "cmd-12345",
  "generation_time": "2024-01-15T12:34:56Z",
  "origin": "MCP",
  "sequence_number": 42,
  "comment": "Routine voltage switch",
  "message": "Command '/YSS/SIMULATOR/SWITCH_VOLTAGE_ON' issued successfully"
}
```


### commands/read_log

Read command execution history from the archive.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `lines` | integer | No | Maximum commands to return (default: 10) |
| `since` | string | No | Start time (ISO 8601 or 'today', 'yesterday') |
| `until` | string | No | End time (ISO 8601 or 'now') |
| `command` | string | No | Filter by command name |
| `instance` | string | No | Yamcs instance |

**Example prompts:**
- "Show me the last 5 commands executed"
- "What commands were sent today?"
- "List all SWITCH_VOLTAGE commands from yesterday"
- "Show command history for the last hour"

**Sample response:**
```json
{
  "instance": "simulator",
  "filter": {
    "lines": 5,
    "since": "today",
    "until": "now",
    "command": null
  },
  "count": 5,
  "commands": [
    {
      "name": "/YSS/SIMULATOR/SWITCH_VOLTAGE_ON",
      "generation_time": "2024-01-15T12:34:56Z",
      "origin": "MCP",
      "sequence_number": 42,
      "username": "operator",
      "queue": "default",
      "acknowledge": {
        "Acknowledge_Queued": {
          "status": "OK",
          "time": "2024-01-15T12:34:56.100Z",
          "message": "Command queued"
        },
        "Acknowledge_Sent": {
          "status": "OK",
          "time": "2024-01-15T12:34:56.200Z",
          "message": "Command sent"
        }
      }
    }
  ]
}
```

## Command Safety

### Dry Run Mode

Always validate commands before execution:

> "Validate the SWITCH_VOLTAGE_ON command with voltage_num=5 without executing it"

This will check:
- Command syntax
- Argument validity
- Range constraints
- Permission requirements

### Command Significance Levels

| Level | Description | Typical Use |
|-------|-------------|-------------|
| `NONE` | No consequence | Test commands |
| `NORMAL` | Routine operation | Daily operations |
| `CRITICAL` | Significant impact | Mode changes |
| `SEVERE` | Irreversible action | Deployment, separation |

## Common Use Cases

### Command Discovery

> "What commands are available for the power system?"

The AI will use `commands/list_commands` with system filter

### Pre-Command Validation

> "Before executing, validate SWITCH_VOLTAGE_ON with voltage_num=3"

The AI will use `commands/run_command` with dry_run=true

### Command Execution

> "Execute the ENABLE_HEATER command with heater_id=1"

The AI will:
1. Optionally validate with dry_run
2. Execute with `commands/run_command`

### Command History Review

> "Show me all commands executed in the last hour"

The AI will use `commands/read_log` with time filtering

### Troubleshooting Failed Commands

> "Check the status of the last 5 commands sent"

The AI will use `commands/read_log` to review acknowledgments

## Best Practices

1. **Always validate first** - Use dry_run for critical commands
2. **Check arguments** - Use describe_command to understand requirements
3. **Review history** - Check recent commands before sending new ones
4. **Monitor acknowledgments** - Verify command was received and executed
5. **Use appropriate processor** - Route commands to the correct processor

## Time Formats

The `read_log` tool accepts various time formats:

| Format | Example | Description |
|--------|---------|-------------|
| ISO 8601 | `2024-01-15T12:00:00Z` | Standard timestamp |
| Special | `now` | Current time |
| Special | `today` | Start of today |
| Special | `yesterday` | Start of yesterday |
| UTC suffix | `today UTC` | Explicit UTC timezone |

## Tips

1. **Start with dry run** - Validate critical commands before execution
2. **Check command arguments** - Use describe_command first
3. **Monitor execution** - Review command log after sending
4. **Filter by system** - Focus on specific subsystems
5. **Track sequence numbers** - Useful for command correlation