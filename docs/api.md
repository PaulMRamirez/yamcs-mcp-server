# Yamcs MCP Server API Reference

This document provides a complete reference for all tools and resources exposed by the Yamcs MCP Server.

## Table of Contents

1. [Server Tools](#server-tools)
2. [MDB Server](#mdb-server)
3. [Processors Server](#processors-server)
4. [Links Server](#links-server)
5. [Storage Server](#storage-server)
6. [Instances Server](#instances-server)
7. [Alarms Server](#alarms-server)

## Server Tools

### health_check
Check overall server health status.

**Parameters:** None

**Returns:**
```json
{
  "status": "healthy",
  "server": "YamcsServer",
  "version": "0.2.3-beta",
  "yamcs_url": "http://localhost:8090",
  "yamcs_instance": "simulator",
  "transport": "stdio"
}
```

### test_connection
Test connection to Yamcs server.

**Parameters:** None

**Returns:**
```json
{
  "connected": true,
  "yamcs_url": "http://localhost:8090",
  "message": "Connection successful"
}
```

## MDB Server

The Mission Database (MDB) server provides access to parameter and command definitions.

### Tools

#### mdb/list_parameters
List parameters from the Mission Database.

**Parameters:**
- `instance` (str, optional): Yamcs instance name
- `system` (str, optional): Filter by space system
- `search` (str, optional): Search pattern for parameter names
- `limit` (int, optional): Maximum results (default: 100)

**Returns:**
```json
{
  "instance": "simulator",
  "count": 150,
  "parameters": [
    {
      "name": "BatteryVoltage",
      "qualified_name": "/YSS/SIMULATOR/BatteryVoltage",
      "type": "float",
      "units": "V",
      "description": "Battery voltage reading"
    }
  ]
}
```

#### mdb/describe_parameter
Get detailed information about a specific parameter.

**Parameters:**
- `parameter` (str, required): Parameter qualified name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "name": "BatteryVoltage",
  "qualified_name": "/YSS/SIMULATOR/BatteryVoltage",
  "type": {
    "eng_type": "float",
    "encoding": "IEEE754_32"
  },
  "units": "V",
  "description": "Battery voltage reading",
  "data_source": "TELEMETERED",
  "alias": [
    {
      "name": "BATT_V",
      "namespace": "MIL-STD-1553"
    }
  ]
}
```

#### mdb/list_commands
List commands from the Mission Database.

**Parameters:**
- `instance` (str, optional): Yamcs instance name
- `system` (str, optional): Filter by space system
- `search` (str, optional): Search pattern for command names
- `limit` (int, optional): Maximum results (default: 100)

**Returns:**
```json
{
  "instance": "simulator",
  "count": 50,
  "commands": [
    {
      "name": "SWITCH_VOLTAGE",
      "qualified_name": "/YSS/SIMULATOR/SWITCH_VOLTAGE",
      "description": "Switch voltage on/off",
      "abstract": false
    }
  ]
}
```

#### mdb/describe_command
Get detailed information about a specific command.

**Parameters:**
- `command` (str, required): Command qualified name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "name": "SWITCH_VOLTAGE",
  "qualified_name": "/YSS/SIMULATOR/SWITCH_VOLTAGE",
  "description": "Switch voltage on/off",
  "abstract": false,
  "arguments": [
    {
      "name": "voltage_num",
      "description": "Voltage number to switch",
      "type": "integer",
      "initial_value": "1"
    }
  ]
}
```

#### mdb/list_space_systems
List space systems from the Mission Database.

**Parameters:**
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "instance": "simulator",
  "count": 5,
  "space_systems": [
    {
      "name": "YSS",
      "qualified_name": "/YSS",
      "description": "Yamcs Simulation Spacecraft"
    }
  ]
}
```

### Resources

- `mdb://parameters` - Summary of parameters in the MDB
- `mdb://commands` - Summary of commands in the MDB

## Processors Server

The Processors server manages real-time and replay processors.

### Tools

#### processors/list_processors
List available processors.

**Parameters:**
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "instance": "simulator",
  "count": 1,
  "processors": [
    {
      "name": "realtime",
      "state": "RUNNING",
      "mission_time": "2024-01-01T12:00:00Z",
      "type": "realtime",
      "replay": false,
      "persistent": true
    }
  ]
}
```

#### processors/describe_processor
Get comprehensive information about a processor.

**Parameters:**
- `processor` (str, required): Processor name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "name": "realtime",
  "instance": "simulator",
  "state": "RUNNING",
  "type": "realtime",
  "mission_time": "2024-01-01T12:00:00Z",
  "config": {
    "persistent": true,
    "protected": false,
    "synchronous": false,
    "checkCommandClearance": true
  },
  "replay": {
    "is_replay": false
  },
  "services": ["tm_realtime", "tc_realtime"],
  "statistics": {}
}
```

#### processors/delete_processor
Delete a processor.

**Parameters:**
- `processor` (str, required): Processor name to delete
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "success": true,
  "processor": "test-processor",
  "instance": "simulator",
  "message": "Processor 'test-processor' deleted successfully"
}
```

### Resources

- `processors://list` - Summary of all processors

## Links Server

The Links server manages data links for telemetry and telecommand.

### Tools

#### links/list_links
List all data links.

**Parameters:**
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "instance": "simulator",
  "count": 5,
  "links": [
    {
      "name": "tm_realtime",
      "type": "TcpTmDataLink",
      "status": "OK",
      "disabled": false,
      "parent": null,
      "data_in_count": 1000000,
      "data_out_count": 0
    }
  ]
}
```

#### links/describe_link
Get comprehensive information about a specific link.

**Parameters:**
- `link` (str, required): Link name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "name": "tm_realtime",
  "qualified_name": "tm_realtime",
  "type": "TcpTmDataLink",
  "parent": null,
  "instance": "simulator",
  "status": {
    "state": "OK",
    "enabled": true,
    "detail": "Connected to localhost:10015"
  },
  "statistics": {
    "data_in_count": 1000000,
    "data_out_count": 0
  }
}
```

#### links/enable_link
Enable a data link.

**Parameters:**
- `link` (str, required): Link name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "success": true,
  "link": "tm_realtime",
  "operation": "enable",
  "message": "Link 'tm_realtime' enabled successfully"
}
```

#### links/disable_link
Disable a data link.

**Parameters:**
- `link` (str, required): Link name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "success": true,
  "link": "tm_realtime",
  "operation": "disable",
  "message": "Link 'tm_realtime' disabled successfully"
}
```

### Resources

- `link://status` - Current status of all links

## Storage Server

The Storage server manages object storage buckets and objects.

### Tools

#### storage/list_buckets
List storage buckets.

**Parameters:**
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "instance": "simulator",
  "count": 2,
  "buckets": [
    {
      "name": "telemetry",
      "created": "2024-01-01T00:00:00Z",
      "size": 1048576,
      "object_count": 100
    }
  ]
}
```

#### storage/list_objects
List objects in a bucket.

**Parameters:**
- `bucket` (str, required): Bucket name
- `prefix` (str, optional): Object name prefix
- `instance` (str, optional): Yamcs instance name
- `limit` (int, optional): Max objects (default: 100)

**Returns:**
```json
{
  "bucket": "telemetry",
  "instance": "simulator",
  "count": 50,
  "objects": [
    {
      "name": "2024/01/01/tm_00001.dat",
      "size": 10240,
      "created": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### storage/upload_object
Upload an object to a bucket.

**Parameters:**
- `bucket` (str, required): Bucket name
- `object_name` (str, required): Object name
- `data` (str, required): Base64 encoded data
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "success": true,
  "bucket": "telemetry",
  "object": "test.txt",
  "size": 100
}
```

#### storage/delete_object
Delete an object from a bucket.

**Parameters:**
- `bucket` (str, required): Bucket name
- `object_name` (str, required): Object name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "success": true,
  "bucket": "telemetry",
  "object": "test.txt",
  "message": "Object 'test.txt' deleted from bucket 'telemetry'"
}
```

#### storage/create_bucket
Create a new storage bucket.

**Parameters:**
- `name` (str, required): Bucket name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "success": true,
  "bucket": {
    "name": "new-bucket",
    "created": "2024-01-01T00:00:00Z"
  },
  "message": "Bucket 'new-bucket' created successfully"
}
```

### Resources

- `storage://overview` - Storage usage overview

## Instances Server

The Instances server manages Yamcs instances and their services.

### Tools

#### instances/list_instances
List all Yamcs instances.

**Parameters:** None

**Returns:**
```json
{
  "count": 1,
  "instances": [
    {
      "name": "simulator",
      "state": "RUNNING",
      "mission_time": "2024-01-01T12:00:00Z",
      "processors": 1
    }
  ]
}
```

#### instances/describe_instance
Get comprehensive information about a Yamcs instance.

**Parameters:**
- `instance` (str, optional): Instance name (uses default if not specified)

**Returns:**
```json
{
  "name": "simulator",
  "state": "RUNNING",
  "mission_time": "2024-01-01T12:00:00Z",
  "labels": {},
  "capabilities": ["mdb", "commanding", "cfdp"],
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
    "count": 10,
    "items": [
      {
        "name": "tm-provider",
        "state": "RUNNING",
        "class": "org.yamcs.tctm.TcpTmDataLink"
      }
    ]
  }
}
```

#### instances/start_instance
Start a Yamcs instance.

**Parameters:**
- `instance` (str, optional): Instance name (uses default if not specified)

**Returns:**
```json
{
  "success": true,
  "instance": "simulator",
  "message": "Instance 'simulator' started"
}
```

#### instances/stop_instance
Stop a Yamcs instance.

**Parameters:**
- `instance` (str, optional): Instance name (uses default if not specified)

**Returns:**
```json
{
  "success": true,
  "instance": "simulator",
  "message": "Instance 'simulator' stopped"
}
```

### Resources

- `instances://list` - Summary of all instances

## Alarms Server

The Alarms server provides alarm monitoring and management capabilities.

### Tools

#### alarms/list_alarms
List active alarms on a processor.

**Parameters:**
- `processor` (str, optional): Processor name (default: realtime)
- `include_pending` (bool, optional): Include pending alarms
- `instance` (str, optional): Yamcs instance

**Returns:**
```json
{
  "instance": "simulator",
  "processor": "realtime",
  "summary": {
    "total": 3,
    "acknowledged": 1,
    "unacknowledged": 2,
    "shelved": 0,
    "ok": 1,
    "latched": 2
  },
  "alarms": [
    {
      "name": "/YSS/SIMULATOR/BatteryVoltage",
      "sequence_number": 1,
      "trigger_time": "2024-01-01T12:00:00Z",
      "severity": "CRITICAL",
      "violation_count": 5,
      "count": 1,
      "is_acknowledged": false,
      "is_ok": false,
      "is_shelved": false
    }
  ]
}
```

#### alarms/describe_alarm
Get detailed information about a specific alarm.

**Parameters:**
- `alarm` (str, required): Alarm name (parameter name)
- `processor` (str, optional): Processor name (default: realtime)
- `instance` (str, optional): Yamcs instance

**Returns:**
```json
{
  "instance": "simulator",
  "processor": "realtime",
  "alarm": {
    "name": "/YSS/SIMULATOR/BatteryVoltage",
    "sequence_number": 1,
    "trigger_time": "2024-01-01T12:00:00Z",
    "update_time": "2024-01-01T12:05:00Z",
    "severity": "CRITICAL",
    "violation_count": 5,
    "count": 1,
    "is_acknowledged": false,
    "is_ok": false,
    "is_process_ok": true,
    "is_latched": true,
    "is_latching": true,
    "is_shelved": false
  }
}
```

#### alarms/acknowledge_alarm
Acknowledge a specific alarm.

**Parameters:**
- `alarm` (str, required): Alarm name
- `sequence_number` (int, required): Alarm sequence number
- `comment` (str, optional): Acknowledgment comment
- `processor` (str, optional): Processor name (default: realtime)
- `instance` (str, optional): Yamcs instance

**Returns:**
```json
{
  "success": true,
  "alarm": "/YSS/SIMULATOR/BatteryVoltage",
  "sequence_number": 1,
  "processor": "realtime",
  "instance": "simulator",
  "message": "Alarm '/YSS/SIMULATOR/BatteryVoltage' (seq: 1) acknowledged"
}
```

#### alarms/shelve_alarm
Shelve (temporarily suspend) an alarm.

**Parameters:**
- `alarm` (str, required): Alarm name
- `sequence_number` (int, required): Alarm sequence number
- `comment` (str, optional): Shelve comment
- `processor` (str, optional): Processor name (default: realtime)
- `instance` (str, optional): Yamcs instance

**Returns:**
```json
{
  "success": true,
  "alarm": "/YSS/SIMULATOR/BatteryVoltage",
  "sequence_number": 1,
  "processor": "realtime",
  "instance": "simulator",
  "message": "Alarm '/YSS/SIMULATOR/BatteryVoltage' (seq: 1) shelved"
}
```

#### alarms/unshelve_alarm
Unshelve (reactivate) a previously shelved alarm.

**Parameters:**
- `alarm` (str, required): Alarm name
- `sequence_number` (int, required): Alarm sequence number
- `comment` (str, optional): Unshelve comment
- `processor` (str, optional): Processor name (default: realtime)
- `instance` (str, optional): Yamcs instance

**Returns:**
```json
{
  "success": true,
  "alarm": "/YSS/SIMULATOR/BatteryVoltage",
  "sequence_number": 1,
  "processor": "realtime",
  "instance": "simulator",
  "message": "Alarm '/YSS/SIMULATOR/BatteryVoltage' (seq: 1) unshelved"
}
```

#### alarms/clear_alarm
Clear a specific alarm.

**Parameters:**
- `alarm` (str, required): Alarm name
- `sequence_number` (int, required): Alarm sequence number
- `comment` (str, optional): Clear comment
- `processor` (str, optional): Processor name (default: realtime)
- `instance` (str, optional): Yamcs instance

**Returns:**
```json
{
  "success": true,
  "alarm": "/YSS/SIMULATOR/BatteryVoltage",
  "sequence_number": 1,
  "processor": "realtime",
  "instance": "simulator",
  "message": "Alarm '/YSS/SIMULATOR/BatteryVoltage' (seq: 1) cleared"
}
```

#### alarms/read_log
Read alarm history from the archive.

**Parameters:**
- `name` (str, optional): Optional alarm name filter
- `start` (str, optional): Start time (ISO 8601 or 'now', 'today', 'yesterday')
- `stop` (str, optional): Stop time (ISO 8601 or 'now', 'today', 'yesterday')
- `lines` (int, optional): Maximum alarms to return (default: 10)
- `descending` (bool, optional): Sort order (default: True)
- `instance` (str, optional): Yamcs instance

**Returns:**
```json
{
  "instance": "simulator",
  "filter": {
    "name": null,
    "start": "today",
    "stop": "now",
    "descending": true
  },
  "count": 5,
  "requested_lines": 10,
  "alarms": [
    {
      "name": "/YSS/SIMULATOR/BatteryVoltage",
      "sequence_number": 1,
      "trigger_time": "2024-01-01T12:00:00Z",
      "severity": "CRITICAL",
      "is_acknowledged": true,
      "acknowledge_time": "2024-01-01T12:10:00Z",
      "acknowledged_by": "operator"
    }
  ]
}
```

### Resources

- `alarms://list` - Summary of active alarms across all processors