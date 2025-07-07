# Examples

This page provides practical examples of using Yamcs MCP Server for common space operations tasks.

## Parameter Monitoring

### Monitor Critical Parameters

```python
# Monitor battery voltage and temperature
parameters = [
    "/YSS/SIMULATOR/BatteryVoltage",
    "/YSS/SIMULATOR/Temperature"
]

# Get current values
for param in parameters:
    result = await client.call_tool("processors_get_parameter_value", {
        "parameter": param
    })
    print(f"{param}: {result['value']['eng_value']} at {result['value']['generation_time']}")
```

### Set Parameter Alarms

```python
# Get parameter with alarm info
param_info = await client.call_tool("mdb_get_parameter", {
    "parameter": "/YSS/SIMULATOR/BatteryVoltage"
})

# Check alarm ranges
if "alarm_info" in param_info:
    print(f"Critical low: {param_info['alarm_info']['critical_low']}")
    print(f"Critical high: {param_info['alarm_info']['critical_high']}")
```

## Command Operations

### Safe Command Execution

```python
# First, validate the command
validation = await client.call_tool("processors_issue_command", {
    "command": "/YSS/SIMULATOR/SWITCH_BATTERY_OFF",
    "args": {"battery_num": 1},
    "dry_run": True
})

if validation["valid"]:
    # Execute the command
    result = await client.call_tool("processors_issue_command", {
        "command": "/YSS/SIMULATOR/SWITCH_BATTERY_OFF",
        "args": {"battery_num": 1},
        "dry_run": False
    })
    print(f"Command sent: {result['id']}")
else:
    print(f"Command validation failed: {validation['error']}")
```

### Command Sequences

```python
# Execute a sequence of commands
commands = [
    ("/YSS/SIMULATOR/POWER_ON", {"subsystem": "ADCS"}),
    ("/YSS/SIMULATOR/SET_MODE", {"mode": "NOMINAL"}),
    ("/YSS/SIMULATOR/ENABLE_TELEMETRY", {"rate": "HIGH"}),
]

for cmd, args in commands:
    result = await client.call_tool("processors_issue_command", {
        "command": cmd,
        "args": args
    })
    print(f"Executed: {cmd} -> {result['id']}")
    
    # Wait a bit between commands
    await asyncio.sleep(1)
```

## Link Management

### Monitor Link Health

```python
# Get all link statuses
links = await client.call_tool("link_list_links")

for link in links["links"]:
    if not link["disabled"] and link["status"] != "OK":
        print(f"WARNING: Link {link['name']} is {link['status']}")
    
    # Get detailed statistics
    stats = await client.call_tool("link_get_statistics", {
        "link": link["name"]
    })
    
    print(f"{link['name']}: In={stats['data_in_count']}, Out={stats['data_out_count']}")
```

### Manage Links

```python
# Disable all links before maintenance
links = await client.call_tool("link_list_links")

disabled_links = []
for link in links["links"]:
    if not link["disabled"]:
        await client.call_tool("link_disable_link", {"link": link["name"]})
        disabled_links.append(link["name"])
        print(f"Disabled: {link['name']}")

# ... perform maintenance ...

# Re-enable links
for link_name in disabled_links:
    await client.call_tool("link_enable_link", {"link": link_name})
    print(f"Re-enabled: {link_name}")
```

## Storage Operations

### Browse Mission Data

```python
# List all storage buckets
buckets = await client.call_tool("object_list_buckets")

for bucket in buckets["buckets"]:
    print(f"\nBucket: {bucket['name']} ({bucket['object_count']} objects)")
    
    # List recent objects
    objects = await client.call_tool("object_list_objects", {
        "bucket": bucket["name"],
        "limit": 5
    })
    
    for obj in objects["objects"]:
        print(f"  - {obj['name']} ({obj['size']} bytes)")
```

### Upload Configuration

```python
import json

# Upload a configuration file
config_data = {
    "mission": "YSS",
    "phase": "operations",
    "settings": {
        "telemetry_rate": "normal",
        "command_verification": True
    }
}

result = await client.call_tool("object_put_object", {
    "bucket": "configs",
    "object_name": "mission_config_v2.json",
    "data": json.dumps(config_data, indent=2),
    "metadata": {
        "version": "2.0",
        "author": "ops_team",
        "date": datetime.utcnow().isoformat()
    }
})
```

## Complete Mission Scenario

### Pre-Pass Checklist

```python
async def pre_pass_checklist(pass_start_time):
    """Execute pre-pass checklist before ground contact."""
    
    print("=== Pre-Pass Checklist ===")
    
    # 1. Check system health
    health = await client.call_tool("health_check")
    print(f"✓ System health: {health['status']}")
    
    # 2. Verify all links are ready
    links = await client.call_tool("link_list_links")
    tm_link = next(l for l in links["links"] if l["name"] == "TM_DOWNLINK")
    tc_link = next(l for l in links["links"] if l["name"] == "TC_UPLINK")
    
    if tm_link["disabled"] or tm_link["status"] != "OK":
        await client.call_tool("link_enable_link", {"link": "TM_DOWNLINK"})
        print("✓ Enabled TM downlink")
    
    if tc_link["disabled"] or tc_link["status"] != "OK":
        await client.call_tool("link_enable_link", {"link": "TC_UPLINK"})
        print("✓ Enabled TC uplink")
    
    # 3. Check critical parameters
    critical_params = [
        "/YSS/SIMULATOR/BatteryVoltage",
        "/YSS/SIMULATOR/Temperature",
        "/YSS/SIMULATOR/PowerConsumption"
    ]
    
    for param in critical_params:
        value = await client.call_tool("processors_get_parameter_value", {
            "parameter": param
        })
        print(f"✓ {param}: {value['value']['eng_value']}")
    
    # 4. Clear event buffer
    events = await client.call_tool("get_events", {
        "start": (pass_start_time - timedelta(hours=1)).isoformat() + "Z",
        "stop": pass_start_time.isoformat() + "Z",
        "severity": "ERROR"
    })
    
    if events["count"] > 0:
        print(f"⚠️  {events['count']} ERROR events in last hour")
    else:
        print("✓ No error events")
    
    print("\n=== Ready for pass ===")

# Execute checklist
await pre_pass_checklist(datetime.utcnow() + timedelta(minutes=30))
```

## Error Handling

### Robust Operations

```python
async def safe_parameter_check(parameter):
    """Safely check a parameter with retry logic."""
    
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            result = await client.call_tool("processors_get_parameter_value", {
                "parameter": parameter
            })
            
            if result.get("error"):
                print(f"Error reading {parameter}: {result['message']}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    return None
            
            return result["value"]["eng_value"]
            
        except Exception as e:
            print(f"Exception reading {parameter}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                return None
    
    return None

# Use the safe function
voltage = await safe_parameter_check("/YSS/SIMULATOR/BatteryVoltage")
if voltage is not None:
    print(f"Battery voltage: {voltage}V")
else:
    print("Failed to read battery voltage")
```