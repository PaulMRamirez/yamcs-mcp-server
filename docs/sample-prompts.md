# Sample Prompts

This page provides example prompts you can use with the Yamcs MCP Server when connected to an AI assistant like Claude. These prompts demonstrate practical mission control scenarios.

## System Health & Status

### Overall System Check
> "Check the health of the Yamcs server and list all running instances with their current status"

Get a comprehensive overview of your Yamcs system health and operational status.

### Link Status Monitoring
> "Show me all data links and highlight any that are disabled or have errors"

Monitor the status of telemetry and command links in your system.

### Processor Status
> "What processors are running on the simulator instance? Are they all operational?"

Check the operational status of data processors in a specific instance.

## Telemetry & Parameters

### Finding Parameters
> "Find all battery-related parameters in the mission database"

Search for specific telemetry parameters by name or subsystem.

### Parameter Details
> "Tell me about the BatteryVoltage parameter - what are its units, type, and data source?"

Get detailed information about specific telemetry parameters.

### System Overview
> "List all space systems and show me what parameters are available in the power subsystem"

Explore the organization of parameters within different subsystems.

## Commanding

### Available Commands
> "What commands are available for voltage control? Show me their arguments"

Discover available commands and their required arguments.

### Command Structure
> "Describe the SWITCH_VOLTAGE command including all its arguments and their types"

Get detailed command information including argument specifications.

### Command Execution

**Note:** The server accepts both JSON objects and JSON strings for command arguments. Objects are preferred, but strings will be automatically parsed.

#### Commands WITH Arguments

> "Execute SWITCH_VOLTAGE_OFF with voltage_num=1"

Execute a command that requires a single argument.

> "Run ENABLE_HEATER with heater_id=2, temperature=25.5, and duration=300"

Execute a command with multiple arguments.

#### Commands WITHOUT Arguments

> "Execute the get_identification command"

Execute a command that doesn't require any arguments.

> "Send the reset_counters command"

Another example of executing a command without arguments.

#### Validation Before Execution

> "Validate (dry-run) the SET_MODE command with mode='SAFE' before executing"

Test command validity without actually executing it.

### Command History
> "Show me the last 10 commands executed today"

Review recently executed commands and their status.

## Alarm Management

### Active Alarms
> "Show me all active alarms on the realtime processor, grouped by severity"

Monitor current alarm states across your system.

### Alarm History
> "What alarms occurred in the last hour? Which ones were acknowledged?"

Review historical alarm data with acknowledgment status.

### Alarm Response
> "There's a critical battery voltage alarm (sequence 1). Acknowledge it with comment 'Under investigation'"

Acknowledge and manage active alarms with comments.

### Alarm Investigation
> "Show me the details of the BatteryVoltage alarm and its history for today"

Investigate specific alarms and their historical patterns.

## Data Management

### Storage Overview
> "List all storage buckets and show me what's in the telemetry bucket"

Explore available storage buckets and their contents.

### Data Upload
> "Upload this configuration file to the configs bucket as 'mission-config-v2.json'"

Manage data uploads to Yamcs storage buckets.

## Troubleshooting Scenarios

### Link Troubleshooting
> "The tm_realtime link seems to be down. Show me its status and try to enable it"

Diagnose and resolve data link issues.

### Multi-System Check
> "Check if the simulator instance is running, list its processors, verify all links are enabled, and show any active alarms"

Perform comprehensive system health checks.

### Historical Analysis
> "Show me all alarms from yesterday, focusing on any battery or power-related issues"

Analyze historical data for specific subsystems or time periods.

## Complex Scenarios

### Pre-Pass Checklist
> "Prepare for the next satellite pass: verify all links are enabled, check for any active alarms, confirm the realtime processor is running, and list available commanding capabilities"

Prepare for operational activities with comprehensive system checks.

### Subsystem Analysis
> "Analyze the power subsystem: list all power-related parameters, show any power commands, and check for power-related alarms in the last 24 hours"

Perform deep analysis of specific spacecraft subsystems.

### Shift Handover
> "Generate a shift handover report: list all instances and their status, show active alarms with acknowledgment status, display link statistics, and identify any disabled components"

Create comprehensive status reports for operational handovers.

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