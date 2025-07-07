# Mission Database (MDB) Component

The MDB component provides access to Yamcs Mission Database, which contains definitions of all telemetry parameters, commands, algorithms, and containers.

## Overview

The Mission Database is the heart of Yamcs, defining:
- **Parameters**: Telemetry and derived parameters
- **Commands**: Telecommands that can be sent to the spacecraft  
- **Containers**: Packet definitions
- **Algorithms**: Derived parameter calculations
- **Space Systems**: Hierarchical organization of the above

## Available Tools

### mdb_list_parameters

List parameters in the Mission Database.

**Parameters:**
- `namespace` (optional): Filter by namespace/subsystem
- `parameter_type` (optional): Filter by type (float, integer, string, etc.)
- `limit` (optional): Maximum number of results (default: 100)

**Example:**
```python
result = await client.call_tool("mdb_list_parameters", {
    "namespace": "/YSS/SIMULATOR",
    "parameter_type": "float",
    "limit": 50
})
```

### mdb_get_parameter

Get detailed information about a specific parameter.

**Parameters:**
- `parameter`: Qualified parameter name

**Example:**
```python
result = await client.call_tool("mdb_get_parameter", {
    "parameter": "/YSS/SIMULATOR/BatteryVoltage"
})

# Result includes:
# - name, qualified_name
# - type, units
# - description
# - alarm_ranges
# - calibrations
```

### mdb_list_commands

List commands in the Mission Database.

**Parameters:**
- `namespace` (optional): Filter by namespace/subsystem
- `abstract` (optional): Include abstract commands (default: false)
- `limit` (optional): Maximum number of results (default: 100)

**Example:**
```python
result = await client.call_tool("mdb_list_commands", {
    "namespace": "/YSS/SIMULATOR/POWER",
    "limit": 20
})
```

### mdb_get_command

Get detailed information about a specific command.

**Parameters:**
- `command`: Qualified command name

**Example:**
```python
result = await client.call_tool("mdb_get_command", {
    "command": "/YSS/SIMULATOR/SWITCH_BATTERY_ON"
})

# Result includes:
# - name, qualified_name
# - description
# - arguments (with types and constraints)
# - significance level
# - constraints
```

### mdb_list_space_systems

List space systems (subsystems) in the database.

**Parameters:**
- `limit` (optional): Maximum number of results (default: 100)

**Example:**
```python
result = await client.call_tool("mdb_list_space_systems", {})

# Returns hierarchical structure of space systems
```

## Resources

The MDB component also provides MCP resources for static access:

- `mdb://parameters` - List of all parameters
- `mdb://commands` - List of all commands
- `mdb://space_systems` - Space system hierarchy

## Use Cases

### Parameter Discovery

Find all temperature-related parameters:

```python
# Search by name pattern
all_params = await client.call_tool("mdb_list_parameters", {
    "limit": 1000
})

temp_params = [
    p for p in all_params["parameters"] 
    if "temp" in p["name"].lower() or "temperature" in p["name"].lower()
]

print(f"Found {len(temp_params)} temperature parameters")
```

### Command Validation

Before sending a command, validate its arguments:

```python
# Get command definition
cmd_info = await client.call_tool("mdb_describe_command", {
    "command": "/YSS/SIMULATOR/SET_PARAMETER"
})

# Check required arguments
for arg in cmd_info["arguments"]:
    print(f"Argument: {arg['name']}")
    print(f"  Type: {arg['type']}")
    print(f"  Required: {arg.get('required', False)}")
    if "range_min" in arg:
        print(f"  Range: [{arg['range_min']}, {arg['range_max']}]")
```

### Alarm Configuration

Review alarm settings for critical parameters:

```python
# Get all parameters with alarms
params = await client.call_tool("mdb_list_parameters", {
    "namespace": "/YSS/SIMULATOR"
})

alarmed_params = []
for param in params["parameters"]:
    # Get detailed info
    details = await client.call_tool("mdb_get_parameter", {
        "parameter": param["qualified_name"]
    })
    
    if "alarm_info" in details:
        alarmed_params.append({
            "name": param["qualified_name"],
            "alarms": details["alarm_info"]
        })

print(f"Parameters with alarms: {len(alarmed_params)}")
```

## Best Practices

1. **Use Qualified Names**: Always use fully qualified parameter/command names to avoid ambiguity
2. **Cache MDB Info**: The MDB rarely changes during operations, so cache results when appropriate
3. **Check Types**: Verify parameter types before processing values
4. **Validate Commands**: Always validate command arguments before execution
5. **Handle Missing Data**: Not all parameters have all fields (units, alarms, etc.)

## Common Patterns

### Building a Parameter Catalog

```python
async def build_parameter_catalog():
    """Build a complete parameter catalog with categories."""
    
    catalog = {
        "power": [],
        "thermal": [],
        "attitude": [],
        "communication": [],
        "other": []
    }
    
    # Get all parameters
    result = await client.call_tool("mdb_list_parameters", {
        "limit": 10000
    })
    
    for param in result["parameters"]:
        name = param["qualified_name"].lower()
        
        if "battery" in name or "power" in name or "voltage" in name:
            catalog["power"].append(param)
        elif "temp" in name or "thermal" in name:
            catalog["thermal"].append(param)
        elif "attitude" in name or "angle" in name or "rate" in name:
            catalog["attitude"].append(param)
        elif "link" in name or "comm" in name or "tlm" in name:
            catalog["communication"].append(param)
        else:
            catalog["other"].append(param)
    
    return catalog
```

### Command Argument Builder

```python
async def build_command_args(command_name, user_args):
    """Build validated command arguments."""
    
    # Get command definition
    cmd_info = await client.call_tool("mdb_describe_command", {
        "command": command_name
    })
    
    validated_args = {}
    
    for arg_def in cmd_info["arguments"]:
        arg_name = arg_def["name"]
        
        # Check if required
        if arg_def.get("required", False) and arg_name not in user_args:
            raise ValueError(f"Missing required argument: {arg_name}")
        
        if arg_name in user_args:
            value = user_args[arg_name]
            
            # Type validation
            if arg_def["type"] == "integer":
                value = int(value)
            elif arg_def["type"] == "float":
                value = float(value)
            elif arg_def["type"] == "boolean":
                value = bool(value)
            
            # Range validation
            if "range_min" in arg_def:
                if value < arg_def["range_min"] or value > arg_def["range_max"]:
                    raise ValueError(
                        f"{arg_name} out of range: [{arg_def['range_min']}, {arg_def['range_max']}]"
                    )
            
            validated_args[arg_name] = value
        elif "default_value" in arg_def:
            validated_args[arg_name] = arg_def["default_value"]
    
    return validated_args
```