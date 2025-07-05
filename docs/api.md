# Yamcs MCP Server API Reference

This document provides a complete reference for all tools and resources exposed by the Yamcs MCP Server.

## Table of Contents

1. [Server Tools](#server-tools)
2. [MDB Component](#mdb-component)
3. [Processor Component](#processor-component)
4. [Archive Component](#archive-component)
5. [Link Management Component](#link-management-component)
6. [Object Storage Component](#object-storage-component)
7. [Instance Management Component](#instance-management-component)

## Server Tools

### health_check
Check overall server health status.

**Parameters:** None

**Returns:**
```json
{
  "status": "healthy",
  "server": "YamcsServer",
  "version": "0.1.0",
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

## MDB Component

### Tools

#### mdb_list_parameters
List parameters from the Mission Database.

**Parameters:**
- `instance` (str, optional): Yamcs instance name
- `system` (str, optional): Filter by space system
- `search` (str, optional): Search pattern for parameter names

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

#### mdb_get_parameter
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

#### mdb_list_commands
List commands from the Mission Database.

**Parameters:**
- `instance` (str, optional): Yamcs instance name
- `system` (str, optional): Filter by space system
- `search` (str, optional): Search pattern for command names

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

#### mdb_get_command
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
  ],
  "alias": []
}
```

#### mdb_list_space_systems
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

- `mdb://parameters` - List all parameters in the MDB
- `mdb://commands` - List all commands in the MDB

## Processor Component

### Tools

#### processor_list_processors
List available processors.

**Parameters:**
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "instance": "simulator",
  "count": 2,
  "processors": [
    {
      "name": "realtime",
      "state": "RUNNING",
      "persistent": true,
      "time": "2024-01-01T12:00:00Z",
      "replay": false
    }
  ]
}
```

#### processor_get_status
Get processor status information.

**Parameters:**
- `processor` (str, optional): Processor name (default: "realtime")
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "instance": "simulator",
  "processor": "realtime",
  "state": "RUNNING",
  "time": "2024-01-01T12:00:00Z",
  "mission_time": "2024-01-01T12:00:00Z",
  "statistics": {
    "tm_packets": 100,
    "parameters": 1000
  }
}
```

#### processor_issue_command
Issue a command through the processor.

**Parameters:**
- `command` (str, required): Command qualified name
- `args` (dict, optional): Command arguments
- `processor` (str, optional): Processor name (default: "realtime")
- `instance` (str, optional): Yamcs instance name
- `dry_run` (bool, optional): Validate without executing

**Returns:**
```json
{
  "success": true,
  "command_id": "cmd-123",
  "command": "/YSS/SIMULATOR/SWITCH_VOLTAGE",
  "generation_time": "2024-01-01T12:00:00Z",
  "origin": "MCP",
  "sequence_number": 42
}
```

#### processor_get_parameter_value
Get current value of a parameter.

**Parameters:**
- `parameter` (str, required): Parameter qualified name
- `processor` (str, optional): Processor name (default: "realtime")
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "parameter": "/YSS/SIMULATOR/BatteryVoltage",
  "value": {
    "eng_value": 12.5,
    "raw_value": 2048,
    "generation_time": "2024-01-01T12:00:00Z",
    "acquisition_time": "2024-01-01T12:00:00Z",
    "validity": "VALID",
    "monitoring_result": "IN_LIMITS"
  }
}
```

#### processor_set_parameter_value
Set parameter value (for writable parameters).

**Parameters:**
- `parameter` (str, required): Parameter qualified name
- `value` (float/int/str/bool, required): New value
- `processor` (str, optional): Processor name (default: "realtime")
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "success": true,
  "parameter": "/YSS/SIMULATOR/TestParameter",
  "value": 42.0,
  "processor": "realtime"
}
```

### Resources

- `processor://status/{processor}` - Real-time processor status

## Archive Component

### Tools

#### archive_query_parameters
Query historical parameter data.

**Parameters:**
- `parameters` (list[str], required): Parameter names to query
- `start` (str, required): Start time (ISO format)
- `stop` (str, required): Stop time (ISO format)
- `instance` (str, optional): Yamcs instance name
- `limit` (int, optional): Max samples per parameter (default: 1000)

**Returns:**
```json
{
  "instance": "simulator",
  "start": "2024-01-01T00:00:00Z",
  "stop": "2024-01-01T01:00:00Z",
  "parameters": {
    "/YSS/SIMULATOR/BatteryVoltage": {
      "count": 3600,
      "samples": [
        {
          "time": "2024-01-01T00:00:00Z",
          "value": 12.5,
          "raw_value": 2048,
          "status": "VALID"
        }
      ]
    }
  }
}
```

#### archive_get_parameter_samples
Get parameter samples with statistics.

**Parameters:**
- `parameter` (str, required): Parameter name
- `start` (str, required): Start time (ISO format)
- `stop` (str, required): Stop time (ISO format)
- `instance` (str, optional): Yamcs instance name
- `limit` (int, optional): Max samples (default: 1000)

**Returns:**
```json
{
  "parameter": "/YSS/SIMULATOR/BatteryVoltage",
  "start": "2024-01-01T00:00:00Z",
  "stop": "2024-01-01T01:00:00Z",
  "count": 3600,
  "statistics": {
    "min": 11.8,
    "max": 12.6,
    "average": 12.2
  },
  "samples": []
}
```

#### archive_query_events
Query historical events.

**Parameters:**
- `start` (str, required): Start time (ISO format)
- `stop` (str, required): Stop time (ISO format)
- `source` (str, optional): Filter by event source
- `severity` (str, optional): Filter by severity
- `search` (str, optional): Search in event message
- `instance` (str, optional): Yamcs instance name
- `limit` (int, optional): Max events (default: 1000)

**Returns:**
```json
{
  "instance": "simulator",
  "start": "2024-01-01T00:00:00Z",
  "stop": "2024-01-01T01:00:00Z",
  "count": 15,
  "events": [
    {
      "time": "2024-01-01T00:15:00Z",
      "source": "FlightSoftware",
      "type": "SYSTEM",
      "severity": "INFO",
      "message": "System initialized",
      "sequence_number": 1
    }
  ]
}
```

#### archive_get_completeness
Get data completeness information.

**Parameters:**
- `parameter` (str, required): Parameter name
- `start` (str, required): Start time (ISO format)
- `stop` (str, required): Stop time (ISO format)
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "parameter": "/YSS/SIMULATOR/BatteryVoltage",
  "start": "2024-01-01T00:00:00Z",
  "stop": "2024-01-01T01:00:00Z",
  "completeness": {
    "coverage_percent": 95.5,
    "gaps": [],
    "total_samples": 3420
  }
}
```

### Resources

- `archive://parameters/{timerange}` - Historical parameter data
- `archive://events/{timerange}` - Historical events

## Link Management Component

### Tools

#### link_list_links
List all data links.

**Parameters:**
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "instance": "simulator",
  "count": 3,
  "links": [
    {
      "name": "tm_realtime",
      "type": "TCP",
      "status": "OK",
      "disabled": false,
      "parent": null,
      "data_in_count": 1000000,
      "data_out_count": 0
    }
  ]
}
```

#### link_get_status
Get detailed link status.

**Parameters:**
- `link` (str, required): Link name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "name": "tm_realtime",
  "type": "TCP",
  "status": "OK",
  "disabled": false,
  "statistics": {
    "data_in_count": 1000000,
    "data_out_count": 0,
    "last_data_in": "2024-01-01T12:00:00Z",
    "last_data_out": null
  },
  "details": "Connected to localhost:10015"
}
```

#### link_enable_link
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

#### link_disable_link
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

#### link_reset_link
Reset link counters.

**Parameters:**
- `link` (str, required): Link name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "success": true,
  "link": "tm_realtime",
  "operation": "reset",
  "message": "Link 'tm_realtime' counters reset successfully"
}
```

#### link_get_statistics
Get statistics for all links.

**Parameters:**
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "instance": "simulator",
  "statistics": {
    "total_links": 3,
    "enabled_links": 2,
    "disabled_links": 1,
    "ok_links": 2,
    "failed_links": 0,
    "total_data_in": 5000000,
    "total_data_out": 100000,
    "links": []
  }
}
```

### Resources

- `link://status` - Current status of all links
- `link://statistics` - Link performance statistics

## Object Storage Component

### Tools

#### object_list_buckets
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
      "object_count": 100,
      "max_size": null
    }
  ]
}
```

#### object_list_objects
List objects in a bucket.

**Parameters:**
- `bucket` (str, required): Bucket name
- `prefix` (str, optional): Object name prefix
- `delimiter` (str, optional): Delimiter for pseudo-directories
- `instance` (str, optional): Yamcs instance name
- `limit` (int, optional): Max objects (default: 1000)

**Returns:**
```json
{
  "bucket": "telemetry",
  "prefix": "2024/01/",
  "count": 50,
  "objects": [
    {
      "name": "2024/01/01/tm_00001.dat",
      "size": 10240,
      "created": "2024-01-01T00:00:00Z",
      "metadata": {}
    }
  ],
  "prefixes": ["2024/01/01/", "2024/01/02/"]
}
```

#### object_get_object
Get object metadata and download URL.

**Parameters:**
- `bucket` (str, required): Bucket name
- `object_name` (str, required): Object name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "bucket": "telemetry",
  "name": "2024/01/01/tm_00001.dat",
  "size": 10240,
  "created": "2024-01-01T00:00:00Z",
  "metadata": {},
  "url": "http://localhost:8090/api/buckets/..."
}
```

#### object_put_object
Upload an object to a bucket.

**Parameters:**
- `bucket` (str, required): Bucket name
- `object_name` (str, required): Object name
- `content` (str, required): Object content
- `metadata` (dict, optional): Metadata key-value pairs
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "success": true,
  "bucket": "telemetry",
  "object_name": "test.txt",
  "size": 100,
  "metadata": {"type": "test"}
}
```

#### object_delete_object
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
  "object_name": "test.txt",
  "message": "Object 'test.txt' deleted from bucket 'telemetry'"
}
```

#### object_get_metadata
Get object metadata.

**Parameters:**
- `bucket` (str, required): Bucket name
- `object_name` (str, required): Object name
- `instance` (str, optional): Yamcs instance name

**Returns:**
```json
{
  "bucket": "telemetry",
  "object_name": "test.txt",
  "metadata": {"type": "test"},
  "system_metadata": {
    "size": 100,
    "created": "2024-01-01T00:00:00Z",
    "content_type": "text/plain"
  }
}
```

### Resources

- `object://buckets` - Available storage buckets
- `object://objects/{bucket}` - Objects in specific bucket

## Instance Management Component

### Tools

#### instance_list_instances
List Yamcs instances.

**Parameters:** None

**Returns:**
```json
{
  "count": 2,
  "instances": [
    {
      "name": "simulator",
      "state": "RUNNING",
      "mission_time": "2024-01-01T12:00:00Z",
      "labels": {},
      "template": "simulation",
      "capabilities": ["mdb", "commanding", "archive"]
    }
  ]
}
```

#### instance_get_info
Get detailed instance information.

**Parameters:**
- `instance` (str, optional): Instance name

**Returns:**
```json
{
  "name": "simulator",
  "state": "RUNNING",
  "mission_time": "2024-01-01T12:00:00Z",
  "labels": {},
  "template": "simulation",
  "capabilities": ["mdb", "commanding", "archive"],
  "processors": ["realtime", "replay"]
}
```

#### instance_start_instance
Start a Yamcs instance.

**Parameters:**
- `instance` (str, required): Instance name

**Returns:**
```json
{
  "success": true,
  "instance": "simulator",
  "operation": "start",
  "message": "Instance 'simulator' started successfully"
}
```

#### instance_stop_instance
Stop a Yamcs instance.

**Parameters:**
- `instance` (str, required): Instance name

**Returns:**
```json
{
  "success": true,
  "instance": "simulator",
  "operation": "stop",
  "message": "Instance 'simulator' stopped successfully"
}
```

#### instance_list_services
List services for an instance.

**Parameters:**
- `instance` (str, optional): Instance name

**Returns:**
```json
{
  "instance": "simulator",
  "count": 10,
  "services": [
    {
      "name": "tm-provider",
      "class": "org.yamcs.tctm.TcpTmDataLink",
      "state": "RUNNING",
      "processor": "realtime"
    }
  ]
}
```

#### instance_start_service
Start a service.

**Parameters:**
- `service` (str, required): Service name
- `instance` (str, optional): Instance name

**Returns:**
```json
{
  "success": true,
  "service": "tm-provider",
  "instance": "simulator",
  "operation": "start",
  "message": "Service 'tm-provider' started successfully"
}
```

#### instance_stop_service
Stop a service.

**Parameters:**
- `service` (str, required): Service name
- `instance` (str, optional): Instance name

**Returns:**
```json
{
  "success": true,
  "service": "tm-provider",
  "instance": "simulator",
  "operation": "stop",
  "message": "Service 'tm-provider' stopped successfully"
}
```

### Resources

- `instance://list` - Available instances
- `instance://services/{instance}` - Services for instance