# Instance Tools

Instance tools manage Yamcs instances and their services.

## Available Tools

| Tool | Purpose |
|------|---------|
| `instances/list_instances` | List all Yamcs instances |
| `instances/describe_instance` | Get detailed instance information |
| `instances/start_instance` | Start a stopped instance |
| `instances/stop_instance` | Stop a running instance |

## Tools Reference

### instances/list_instances

List all available Yamcs instances.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| - | - | - | No parameters |

**Example prompts:**
- "List all Yamcs instances"
- "Show me what instances are available"
- "Which instances are currently running?"

**Sample response:**
```json
{
  "count": 2,
  "instances": [
    {
      "name": "simulator",
      "state": "RUNNING",
      "mission_time": "2024-01-15T12:34:56Z",
      "processors": 1,
      "clients": 3
    },
    {
      "name": "ops",
      "state": "STOPPED",
      "mission_time": null,
      "processors": 0,
      "clients": 0
    }
  ]
}
```

### instances/describe_instance

Get comprehensive information about a specific instance.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `instance` | string | No | Instance name (uses default if not specified) |

**Example prompts:**
- "Describe the simulator instance"
- "Show me details about the ops instance"
- "What services are running in the simulator?"

**Sample response:**
```json
{
  "name": "simulator",
  "state": "RUNNING",
  "mission_time": "2024-01-15T12:34:56Z",
  "labels": {
    "environment": "development",
    "mission": "demo"
  },
  "capabilities": [
    "mdb",
    "commanding",
    "cfdp",
    "timeline",
    "alarm"
  ],
  "processors": {
    "count": 1,
    "items": [
      {
        "name": "realtime",
        "state": "RUNNING",
        "type": "realtime"
      }
    ]
  },
  "services": {
    "count": 12,
    "items": [
      {
        "name": "tm-provider",
        "state": "RUNNING",
        "class": "org.yamcs.tctm.TcpTmDataLink"
      },
      {
        "name": "tc-provider",
        "state": "RUNNING",
        "class": "org.yamcs.tctm.TcpTcDataLink"
      },
      {
        "name": "parameter-archive",
        "state": "RUNNING",
        "class": "org.yamcs.parameterarchive.ParameterArchive"
      }
    ]
  },
  "databases": {
    "mdb": "/opt/yamcs/mdb/simulator",
    "config": "/opt/yamcs/etc/simulator.yaml"
  }
}
```

### instances/start_instance

Start a stopped Yamcs instance.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `instance` | string | No | Instance name (uses default if not specified) |

**Example prompts:**
- "Start the simulator instance"
- "Bring the ops instance online"
- "Activate the test instance"

**Sample response:**
```json
{
  "success": true,
  "instance": "simulator",
  "message": "Instance 'simulator' started",
  "new_state": "RUNNING"
}
```

### instances/stop_instance

Stop a running Yamcs instance.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `instance` | string | No | Instance name (uses default if not specified) |

**Example prompts:**
- "Stop the simulator instance"
- "Shut down the test instance"
- "Take the ops instance offline"

**Sample response:**
```json
{
  "success": true,
  "instance": "simulator",
  "message": "Instance 'simulator' stopped",
  "new_state": "STOPPED"
}
```

## Resources

### instances://list

Provides a formatted summary of all instances and their states.

**Example prompt:** "Show me the instances list resource"

## Instance States

| State | Description |
|-------|-------------|
| `RUNNING` | Instance is active and processing |
| `STOPPED` | Instance is stopped |
| `STARTING` | Instance is in the process of starting |
| `STOPPING` | Instance is in the process of stopping |
| `FAILED` | Instance failed to start or crashed |

## Instance Capabilities

Common capabilities you may see:

| Capability | Description |
|------------|-------------|
| `mdb` | Mission Database support |
| `commanding` | Command processing capability |
| `cfdp` | CCSDS File Delivery Protocol |
| `timeline` | Timeline/scheduling support |
| `alarm` | Alarm monitoring |
| `events` | Event recording |
| `parameter-archive` | Parameter archiving |

## Common Use Cases

### System Status Check

> "Show me all instances and their current state"

The AI will use `instances/list_instances` to provide an overview

### Instance Health Check

> "Check if the simulator instance is healthy and what services are running"

The AI will use `instances/describe_instance` to show detailed status

### Instance Management

> "Stop the test instance for maintenance"

The AI will use `instances/stop_instance` to stop the instance

### Service Verification

> "Verify that commanding is available on the simulator instance"

The AI will use `instances/describe_instance` and check capabilities

### Multi-Instance Operations

> "Start all stopped instances"

The AI will:
1. Use `instances/list_instances` to find stopped instances
2. Use `instances/start_instance` for each stopped instance

## Tips

1. **Check state first** - Verify instance state before operations
2. **Review capabilities** - Ensure required capabilities are available
3. **Monitor services** - Check that critical services are running
4. **Understand processors** - Each instance can have multiple processors
5. **Watch client count** - High client counts indicate active usage