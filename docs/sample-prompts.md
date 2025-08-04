# Sample Prompts

This page provides example prompts you can use with the Yamcs MCP Server when connected to an AI assistant like Claude. These prompts demonstrate practical mission control scenarios.

## System Health & Status

### Overall System Check
> "Check the health of the Yamcs server and list all running instances with their current status"

This will use `health_check`, `test_connection`, and `instances/list_instances` tools to give you a comprehensive system overview.

### Link Status Monitoring
> "Show me all data links and highlight any that are disabled or have errors"

Uses `links/list_links` to check telemetry and command link status.

### Processor Status
> "What processors are running on the simulator instance? Are they all operational?"

Combines `processors/list_processors` with status checking.

## Telemetry & Parameters

### Finding Parameters
> "Find all battery-related parameters in the mission database"

Uses `mdb/list_parameters` with search patterns to locate specific telemetry.

### Parameter Details
> "Tell me about the BatteryVoltage parameter - what are its units, type, and data source?"

Uses `mdb/describe_parameter` to get detailed parameter information.

### System Overview
> "List all space systems and show me what parameters are available in the power subsystem"

Combines `mdb/list_space_systems` and `mdb/list_parameters` with filtering.

## Commanding

### Available Commands
> "What commands are available for voltage control? Show me their arguments"

Uses `mdb/list_commands` with search and `mdb/describe_command` for details.

### Command Structure
> "Describe the SWITCH_VOLTAGE command including all its arguments and their types"

Provides detailed command information for operators.

### Command Execution

**Note:** The server accepts both JSON objects and JSON strings for command arguments. Objects are preferred, but strings will be automatically parsed.

#### Commands WITH Arguments

> "Execute SWITCH_VOLTAGE_OFF with voltage_num=1"

The tool will correctly use:
```json
{
  "command": "/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF", 
  "args": {"voltage_num": 1}
}
```

> "Run ENABLE_HEATER with heater_id=2, temperature=25.5, and duration=300"

The tool will correctly use:
```json
{
  "command": "/YSS/SIMULATOR/ENABLE_HEATER", 
  "args": {
    "heater_id": 2, 
    "temperature": 25.5,
    "duration": 300
  }
}
```

#### Commands WITHOUT Arguments

> "Execute the get_identification command"

The tool will correctly use:
```json
{
  "command": "/TSE/simulator/get_identification"
}
```
Note: The `args` field is omitted entirely for commands with no arguments.

> "Send the reset_counters command"

The tool will correctly use:
```json
{
  "command": "/YSS/SIMULATOR/reset_counters"
}
```

#### Validation Before Execution

> "Validate (dry-run) the SET_MODE command with mode='SAFE' before executing"

Uses dry_run=true to validate without execution:
```json
{
  "command": "/YSS/SIMULATOR/SET_MODE",
  "args": {"mode": "SAFE"},
  "dry_run": true
}
```

### Command History
> "Show me the last 10 commands executed today"

Uses `commands/read_log` to review command history.

## Alarm Management

### Active Alarms
> "Show me all active alarms on the realtime processor, grouped by severity"

Uses `alarms/list_alarms` to monitor current alarm state.

### Alarm History
> "What alarms occurred in the last hour? Which ones were acknowledged?"

Uses `alarms/read_log` with time filtering.

### Alarm Response
> "There's a critical battery voltage alarm (sequence 1). Acknowledge it with comment 'Under investigation'"

Uses `alarms/acknowledge_alarm` for alarm management.

### Alarm Investigation
> "Show me the details of the BatteryVoltage alarm and its history for today"

Combines `alarms/describe_alarm` and `alarms/read_log` for investigation.

## Data Management

### Storage Overview
> "List all storage buckets and show me what's in the telemetry bucket"

Uses `storage/list_buckets` and `storage/list_objects`.

### Data Upload
> "Upload this configuration file to the configs bucket as 'mission-config-v2.json'"

Uses `storage/upload_object` for data management.

## Troubleshooting Scenarios

### Link Troubleshooting
> "The tm_realtime link seems to be down. Show me its status and try to enable it"

Combines `links/describe_link` and `links/enable_link`.

### Multi-System Check
> "Check if the simulator instance is running, list its processors, verify all links are enabled, and show any active alarms"

Comprehensive health check using multiple tools.

### Historical Analysis
> "Show me all alarms from yesterday, focusing on any battery or power-related issues"

Uses `alarms/read_log` with time range and name filtering.

## Complex Scenarios

### Pre-Pass Checklist
> "Prepare for the next satellite pass: verify all links are enabled, check for any active alarms, confirm the realtime processor is running, and list available commanding capabilities"

Combines multiple tools for operational readiness.

### Subsystem Analysis
> "Analyze the power subsystem: list all power-related parameters, show any power commands, and check for power-related alarms in the last 24 hours"

Deep dive into a specific subsystem using MDB and alarm tools.

### Shift Handover
> "Generate a shift handover report: list all instances and their status, show active alarms with acknowledgment status, display link statistics, and identify any disabled components"

Comprehensive status report using multiple servers.

## Tips for Effective Prompts

1. **Be Specific**: Instead of "show alarms", say "show critical alarms from the last hour on the realtime processor"

2. **Chain Operations**: "First check if the simulator instance is running, then list its processors, and finally show any alarms"

3. **Use Filters**: "Find all parameters with 'temperature' in the name from the thermal subsystem"

4. **Include Context**: "The telemetry link is showing high data rates. Show me its detailed status and statistics"

5. **Request Formatting**: "List all active alarms grouped by severity, with unacknowledged ones first"

## Integration Examples

### With Claude Desktop
When using with Claude Desktop, you can combine file operations with Yamcs operations:

> "Read the mission plan from mission-plan.md, then check if all the required links mentioned in the plan are currently enabled"

### With Development Tools
> "Check the MDB for parameters matching the interface defined in telemetry-spec.yaml, and verify they're all present"

### With Monitoring
> "Monitor the system for the next operation: show processor status, active alarms, and link statistics, then suggest any actions needed"

## Advanced Usage

### Conditional Operations
> "If there are any critical alarms, show their details and history. Otherwise, just give me a count of active alarms by severity"

### Bulk Operations
> "For each disabled link, show why it's disabled and attempt to re-enable it"

### Correlation Analysis
> "Show me all alarms that occurred around the same time as the last link failure"

### Performance Analysis
> "Compare the data rates across all telemetry links and identify any anomalies"

## Common Patterns

### Health Check Pattern
```
1. Check server health
2. Verify instance status
3. List processors and their states
4. Check all link status
5. Show active alarm summary
```

### Investigation Pattern
```
1. Identify the problem (alarm, link down, etc.)
2. Get detailed information about the component
3. Check historical data for patterns
4. Suggest corrective actions
```

### Operational Readiness Pattern
```
1. Verify all systems are running
2. Check for blocking alarms
3. Confirm all required links are enabled
4. Validate commanding capability
5. Review recent operations
```

These patterns help structure your interactions for common mission control tasks.