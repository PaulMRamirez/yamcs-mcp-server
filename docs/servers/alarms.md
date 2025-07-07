# Alarms Server

The Alarms server provides comprehensive alarm monitoring and management capabilities for Yamcs.

## Overview

The Alarms server allows you to:
- Monitor active alarms across all processors
- View detailed alarm information including acknowledge status
- Acknowledge, shelve, and clear alarms
- Query historical alarm data
- Get summary statistics of alarm states

## Available Tools

### alarms_list_alarms

List active alarms on a processor with summary statistics.

**Parameters:**
- `processor` (optional): Processor name (default: realtime)
- `include_pending` (optional): Include pending alarms (default: false)
- `instance` (optional): Yamcs instance (uses default if not specified)

**Returns:**
- Summary counts (total, acknowledged, unacknowledged, shelved, ok, latched)
- List of active alarms with current state

**Example:**
```python
result = await client.call_tool("alarms_list_alarms", {
    "processor": "realtime"
})

# Result includes:
# {
#   "summary": {
#     "total": 5,
#     "acknowledged": 2,
#     "unacknowledged": 3,
#     "shelved": 1,
#     "ok": 0,
#     "latched": 1
#   },
#   "alarms": [...]
# }
```

### alarms_describe_alarm

Get detailed information about a specific alarm.

**Parameters:**
- `alarm`: Alarm name (parameter name)
- `processor` (optional): Processor name (default: realtime)
- `instance` (optional): Yamcs instance

**Returns:**
All documented fields from the Yamcs Alarm model including:
- Basic info (name, sequence_number, trigger_time, severity)
- Counts (violation_count, count)
- State flags (is_acknowledged, is_ok, is_latched, is_shelved)
- Acknowledge info if acknowledged

**Example:**
```python
result = await client.call_tool("alarms_describe_alarm", {
    "alarm": "/YSS/SIMULATOR/BatteryVoltage"
})
```

### alarms_acknowledge_alarm

Acknowledge a specific alarm.

**Parameters:**
- `alarm`: Alarm name
- `sequence_number`: Alarm sequence number
- `comment` (optional): Acknowledgment comment
- `processor` (optional): Processor name (default: realtime)
- `instance` (optional): Yamcs instance

**Example:**
```python
result = await client.call_tool("alarms_acknowledge_alarm", {
    "alarm": "/YSS/SIMULATOR/BatteryVoltage",
    "sequence_number": 123,
    "comment": "Investigating battery issue"
})
```

### alarms_shelve_alarm

Temporarily shelve an alarm.

**Parameters:**
- `alarm`: Alarm name
- `comment` (optional): Shelve reason
- `duration` (optional): Shelve duration in seconds
- `processor` (optional): Processor name
- `instance` (optional): Yamcs instance

**Example:**
```python
result = await client.call_tool("alarms_shelve_alarm", {
    "alarm": "/YSS/SIMULATOR/BatteryVoltage",
    "comment": "Known issue, fix scheduled",
    "duration": 3600  # 1 hour
})
```

### alarms_unshelve_alarm

Unshelve a previously shelved alarm.

**Parameters:**
- `alarm`: Alarm name
- `processor` (optional): Processor name
- `instance` (optional): Yamcs instance

### alarms_clear_alarm

Clear an alarm.

**Parameters:**
- `alarm`: Alarm name
- `sequence_number`: Alarm sequence number
- `comment` (optional): Clear reason
- `processor` (optional): Processor name
- `instance` (optional): Yamcs instance

### alarms_read_log

Read alarm history from the archive.

**Parameters:**
- `name` (optional): Filter by alarm name
- `start` (optional): Start time (ISO 8601 or 'now', 'today', 'yesterday')
- `stop` (optional): Stop time
- `lines` (optional): Maximum entries to return (default: 10)
- `descending` (optional): Sort order (default: true, most recent first)
- `instance` (optional): Yamcs instance

**Example:**
```python
# Get recent alarm history
result = await client.call_tool("alarms_read_log", {
    "lines": 50,
    "start": "today"
})

# Get history for specific alarm
result = await client.call_tool("alarms_read_log", {
    "name": "/YSS/SIMULATOR/BatteryVoltage",
    "lines": 20
})
```

## Resources

The Alarms server provides one MCP resource:

- `alarms://list` - Summary of active alarms across all processors with counts

## Use Cases

### Alarm Monitoring Dashboard

```python
async def get_alarm_dashboard():
    """Get comprehensive alarm status."""
    
    # Get active alarms with summary
    active = await client.call_tool("alarms_list_alarms", {})
    
    print(f"Total Active Alarms: {active['summary']['total']}")
    print(f"  Unacknowledged: {active['summary']['unacknowledged']}")
    print(f"  Acknowledged: {active['summary']['acknowledged']}")
    print(f"  Shelved: {active['summary']['shelved']}")
    
    # Show critical unacknowledged alarms
    critical_unack = [
        a for a in active['alarms'] 
        if a['severity'] in ['CRITICAL', 'SEVERE'] 
        and not a['is_acknowledged']
    ]
    
    if critical_unack:
        print(f"\nCritical Unacknowledged Alarms ({len(critical_unack)}):")
        for alarm in critical_unack:
            print(f"  - {alarm['name']} [{alarm['severity']}]")
```

### Alarm Acknowledgment Workflow

```python
async def acknowledge_critical_alarms():
    """Acknowledge all critical alarms with logging."""
    
    # Get active alarms
    result = await client.call_tool("alarms_list_alarms", {})
    
    for alarm in result['alarms']:
        if alarm['severity'] == 'CRITICAL' and not alarm['is_acknowledged']:
            # Acknowledge the alarm
            ack_result = await client.call_tool("alarms_acknowledge_alarm", {
                "alarm": alarm['name'],
                "sequence_number": alarm['sequence_number'],
                "comment": "Auto-acknowledged critical alarm"
            })
            
            if ack_result.get('success'):
                print(f"Acknowledged: {alarm['name']}")
```

### Alarm History Analysis

```python
async def analyze_alarm_patterns():
    """Analyze alarm patterns over time."""
    
    # Get alarm history for the past week
    history = await client.call_tool("alarms_read_log", {
        "lines": 1000,
        "start": "2024-01-01T00:00:00Z"
    })
    
    # Count by alarm name
    alarm_counts = {}
    for entry in history['alarms']:
        name = entry['name']
        alarm_counts[name] = alarm_counts.get(name, 0) + 1
    
    # Show most frequent alarms
    sorted_alarms = sorted(
        alarm_counts.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    print("Most Frequent Alarms:")
    for name, count in sorted_alarms[:10]:
        print(f"  {name}: {count} occurrences")
```

## Best Practices

1. **Always include sequence_number**: When acknowledging or clearing alarms, always provide the sequence_number to ensure you're acting on the correct alarm instance

2. **Add meaningful comments**: When acknowledging or shelving alarms, provide clear comments explaining the action taken

3. **Monitor unacknowledged count**: Set up monitoring for the unacknowledged alarm count to ensure timely response

4. **Use shelving judiciously**: Only shelve alarms for known issues with a clear resolution timeline

5. **Regular history review**: Periodically review alarm history to identify recurring issues

## Alarm States

Alarms can be in various states (not mutually exclusive):
- **Acknowledged**: Operator has acknowledged the alarm
- **Shelved**: Temporarily suppressed
- **OK**: Condition that triggered the alarm is resolved
- **Latched**: Alarm remains active even if condition is resolved
- **Unacknowledged**: Not yet acknowledged by an operator