# MDB Tools

The Mission Database (MDB) tools provide access to parameter and command definitions in your Yamcs instance.

## Available Tools

| Tool | Purpose |
|------|---------|
| `mdb/list_parameters` | List parameters with optional filtering |
| `mdb/describe_parameter` | Get detailed parameter information |
| `mdb/list_commands` | List commands with optional filtering |
| `mdb/describe_command` | Get detailed command information |
| `mdb/list_space_systems` | List space system hierarchy |

## Tools Reference

### mdb/list_parameters

List parameters from the Mission Database with optional filtering.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `instance` | string | No | Yamcs instance name (uses default if not specified) |
| `system` | string | No | Filter by space system (e.g., "/YSS/SIMULATOR") |
| `search` | string | No | Search pattern for parameter names |
| `limit` | integer | No | Maximum results to return (default: 100) |

**Example prompts:**
- "List all parameters"
- "Show me battery-related parameters"
- "Find parameters in the power subsystem"

**Sample response:**
```json
{
  "instance": "simulator",
  "count": 25,
  "parameters": [
    {
      "name": "BatteryVoltage",
      "qualified_name": "/YSS/SIMULATOR/BatteryVoltage",
      "type": "float",
      "units": "V",
      "description": "Main battery voltage"
    }
  ]
}
```

### mdb/describe_parameter

Get comprehensive information about a specific parameter.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `parameter` | string | Yes | Parameter qualified name (e.g., "/YSS/SIMULATOR/BatteryVoltage") |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Tell me about the BatteryVoltage parameter"
- "What are the alarm limits for temperature?"
- "Show me the data type and units for PowerConsumption"

**Sample response:**
```json
{
  "name": "BatteryVoltage",
  "qualified_name": "/YSS/SIMULATOR/BatteryVoltage",
  "type": {
    "eng_type": "float",
    "encoding": "IEEE754_32"
  },
  "units": "V",
  "description": "Main battery voltage reading",
  "data_source": "TELEMETERED",
  "alias": [
    {
      "name": "BATT_V",
      "namespace": "MIL-STD-1553"
    }
  ],
  "alarm_info": {
    "min_violations": 1,
    "static_alarm_ranges": [
      {
        "level": "WATCH",
        "min_inclusive": 24.0,
        "max_inclusive": 30.0
      },
      {
        "level": "CRITICAL",
        "min_inclusive": 22.0,
        "max_inclusive": 32.0
      }
    ]
  }
}
```

### mdb/list_commands

List commands from the Mission Database with optional filtering.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `instance` | string | No | Yamcs instance name |
| `system` | string | No | Filter by space system |
| `search` | string | No | Search pattern for command names |
| `limit` | integer | No | Maximum results (default: 100) |

**Example prompts:**
- "List all available commands"
- "Show me power-related commands"
- "What commands are in the ADCS system?"

**Sample response:**
```json
{
  "instance": "simulator",
  "count": 15,
  "commands": [
    {
      "name": "SWITCH_VOLTAGE_ON",
      "qualified_name": "/YSS/SIMULATOR/SWITCH_VOLTAGE_ON",
      "description": "Switch voltage bus on",
      "abstract": false
    }
  ]
}
```

### mdb/describe_command

Get detailed information about a specific command including arguments.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `command` | string | Yes | Command qualified name |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Describe the SWITCH_VOLTAGE_ON command"
- "What arguments does the SET_MODE command take?"
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

### mdb/list_space_systems

List the space system hierarchy in the Mission Database.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Show me the space system hierarchy"
- "List all subsystems"
- "What space systems are defined?"

**Sample response:**
```json
{
  "instance": "simulator",
  "count": 5,
  "space_systems": [
    {
      "name": "YSS",
      "qualified_name": "/YSS",
      "description": "Yamcs Simulation Spacecraft"
    },
    {
      "name": "SIMULATOR",
      "qualified_name": "/YSS/SIMULATOR",
      "description": "Simulation subsystem"
    }
  ]
}
```

## Resources

### mdb://parameters

Provides a formatted summary of all parameters in the Mission Database.

**Example prompt:** "Show me the parameters resource"

### mdb://commands

Provides a formatted summary of all commands in the Mission Database.

**Example prompt:** "Show me the commands resource"

## Common Use Cases

### Finding Parameters

> "Find all temperature sensors"

The AI will use `mdb/list_parameters` with search="temperature"

### Understanding Parameter Details

> "What are the normal operating ranges for battery voltage?"

The AI will use `mdb/describe_parameter` to get alarm ranges

### Command Discovery

> "What commands can I use to control the power system?"

The AI will use `mdb/list_commands` with search="power" or system filter

### Pre-Command Validation

> "Before I send the SWITCH_VOLTAGE_ON command, show me what arguments it needs"

The AI will use `mdb/describe_command` to show required arguments

## Tips

1. **Use search patterns** - The search parameter supports partial matching
2. **Filter by system** - Use the system parameter to focus on specific subsystems
3. **Check alarm ranges** - Use describe_parameter to understand nominal values
4. **Verify command arguments** - Always check command details before execution
5. **Explore the hierarchy** - Use list_space_systems to understand organization