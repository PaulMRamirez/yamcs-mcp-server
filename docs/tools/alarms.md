# Alarm Tools

Alarm tools provide monitoring and management of parameter alarms in Yamcs.

## Available Tools

| Tool | Purpose |
|------|---------|
| `alarms/list_alarms` | List active alarms |
| `alarms/describe_alarm` | Get detailed alarm information |
| `alarms/acknowledge_alarm` | Acknowledge an alarm |
| `alarms/shelve_alarm` | Temporarily suspend an alarm |
| `alarms/unshelve_alarm` | Reactivate a shelved alarm |
| `alarms/clear_alarm` | Clear an alarm |
| `alarms/read_log` | Read alarm history |

## Tools Reference

### alarms/list_alarms

List active alarms on a processor.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `processor` | string | No | Processor name (default: "realtime") |
| `include_pending` | boolean | No | Include pending alarms (default: false) |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Show me all active alarms"
- "List critical alarms on the realtime processor"
- "Are there any unacknowledged alarms?"

**Sample response:**
```json
{
  "instance": "simulator",
  "processor": "realtime",
  "summary": {
    "total": 3,
    "acknowledged": 1,
    "unacknowledged": 2,
    "shelved": 0,
    "ok": 0,
    "latched": 3
  },
  "alarms": [
    {
      "name": "/YSS/SIMULATOR/BatteryVoltage",
      "sequence_number": 1,
      "trigger_time": "2024-01-15T12:00:00Z",
      "severity": "CRITICAL",
      "violation_count": 5,
      "count": 1,
      "is_acknowledged": false,
      "is_ok": false,
      "is_shelved": false
    },
    {
      "name": "/YSS/SIMULATOR/Temperature",
      "sequence_number": 2,
      "trigger_time": "2024-01-15T12:05:00Z",
      "severity": "WARNING",
      "violation_count": 2,
      "count": 1,
      "is_acknowledged": true,
      "is_ok": false,
      "is_shelved": false
    }
  ]
}
```

### alarms/describe_alarm

Get detailed information about a specific alarm.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `alarm` | string | Yes | Alarm name (parameter name) |
| `processor` | string | No | Processor name (default: "realtime") |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Show me details about the BatteryVoltage alarm"
- "What's the status of the temperature alarm?"
- "Get full information on the power system alarm"

**Sample response:**
```json
{
  "instance": "simulator",
  "processor": "realtime",
  "alarm": {
    "name": "/YSS/SIMULATOR/BatteryVoltage",
    "sequence_number": 1,
    "trigger_time": "2024-01-15T12:00:00Z",
    "update_time": "2024-01-15T12:30:00Z",
    "severity": "CRITICAL",
    "violation_count": 10,
    "count": 1,
    "is_acknowledged": false,
    "is_ok": false,
    "is_process_ok": true,
    "is_latched": true,
    "is_latching": true,
    "is_shelved": false,
    "trigger_value": 22.5,
    "most_severe_value": 21.8,
    "current_value": 23.2,
    "violations": [
      {
        "level": "CRITICAL",
        "type": "LOW",
        "limit": 24.0
      }
    ]
  }
}
```

### alarms/acknowledge_alarm

Acknowledge a specific alarm.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `alarm` | string | Yes | Alarm name |
| `sequence_number` | integer | Yes | Alarm sequence number |
| `comment` | string | No | Acknowledgment comment |
| `processor` | string | No | Processor name (default: "realtime") |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Acknowledge the BatteryVoltage alarm with sequence 1"
- "Mark the temperature alarm as acknowledged with comment 'Under investigation'"
- "Acknowledge alarm sequence 5"

**Sample response:**
```json
{
  "success": true,
  "alarm": "/YSS/SIMULATOR/BatteryVoltage",
  "sequence_number": 1,
  "processor": "realtime",
  "instance": "simulator",
  "message": "Alarm '/YSS/SIMULATOR/BatteryVoltage' (seq: 1) acknowledged",
  "acknowledged_by": "operator",
  "acknowledge_time": "2024-01-15T12:35:00Z"
}
```

### alarms/shelve_alarm

Temporarily suspend (shelve) an alarm.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `alarm` | string | Yes | Alarm name |
| `sequence_number` | integer | Yes | Alarm sequence number |
| `comment` | string | No | Shelve reason |
| `processor` | string | No | Processor name |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Shelve the temperature alarm during maintenance"
- "Temporarily disable the low voltage alarm"
- "Suspend alarm sequence 2 with comment 'Known issue'"

**Sample response:**
```json
{
  "success": true,
  "alarm": "/YSS/SIMULATOR/Temperature",
  "sequence_number": 2,
  "processor": "realtime",
  "instance": "simulator",
  "message": "Alarm '/YSS/SIMULATOR/Temperature' (seq: 2) shelved"
}
```

### alarms/unshelve_alarm

Reactivate a previously shelved alarm.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `alarm` | string | Yes | Alarm name |
| `sequence_number` | integer | Yes | Alarm sequence number |
| `comment` | string | No | Unshelve reason |
| `processor` | string | No | Processor name |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Unshelve the temperature alarm"
- "Reactivate the shelved voltage alarm"
- "Resume monitoring for alarm sequence 2"

### alarms/clear_alarm

Clear a specific alarm.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `alarm` | string | Yes | Alarm name |
| `sequence_number` | integer | Yes | Alarm sequence number |
| `comment` | string | No | Clear reason |
| `processor` | string | No | Processor name |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Clear the resolved battery alarm"
- "Remove alarm sequence 1"
- "Clear the temperature alarm with comment 'Issue resolved'"

### alarms/read_log

Read historical alarm data from the archive.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | No | Filter by alarm name |
| `start` | string | No | Start time (ISO 8601 or 'today', 'yesterday') |
| `stop` | string | No | Stop time (ISO 8601 or 'now') |
| `lines` | integer | No | Maximum entries (default: 10) |
| `descending` | boolean | No | Sort order (default: true) |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Show me alarms from the last hour"
- "What battery alarms occurred yesterday?"
- "List the 5 most recent critical alarms"

**Sample response:**
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
  "alarms": [
    {
      "name": "/YSS/SIMULATOR/BatteryVoltage",
      "sequence_number": 1,
      "trigger_time": "2024-01-15T12:00:00Z",
      "clear_time": "2024-01-15T13:00:00Z",
      "severity": "CRITICAL",
      "is_acknowledged": true,
      "acknowledge_time": "2024-01-15T12:10:00Z",
      "acknowledged_by": "operator",
      "acknowledge_message": "Investigating"
    }
  ]
}
```

## Resources

### alarms://list

Provides a formatted summary of active alarms across all processors.

**Example prompt:** "Show me the alarms list resource"

## Alarm Severities

| Severity | Description | Typical Response |
|----------|-------------|------------------|
| `CRITICAL` | Immediate action required | Acknowledge and investigate |
| `MAJOR` | Significant issue | Investigate promptly |
| `WARNING` | Potential problem | Monitor closely |
| `MINOR` | Low priority issue | Schedule review |
| `INFO` | Informational only | No action required |

## Alarm States

| State | Description |
|-------|-------------|
| `is_ok` | Parameter value is within limits |
| `is_acknowledged` | Operator has acknowledged |
| `is_shelved` | Temporarily suspended |
| `is_latched` | Alarm persists even if value returns to normal |

## Common Use Cases

### Alarm Triage

> "Show me all unacknowledged critical alarms"

The AI will use `alarms/list_alarms` and filter results

### Alarm Investigation

> "What caused the battery voltage alarm and what's its current value?"

The AI will use `alarms/describe_alarm` for detailed information

### Shift Handover

> "Show me all alarms that occurred during the last 8 hours with their acknowledgment status"

The AI will use `alarms/read_log` with appropriate time range

### Maintenance Mode

> "Shelve all temperature alarms during thermal testing"

The AI will:
1. Use `alarms/list_alarms` to find temperature alarms
2. Use `alarms/shelve_alarm` for each one

## Tips

1. **Always include sequence number** - Required for acknowledge/shelve/clear operations
2. **Add comments** - Document why alarms were acknowledged or shelved
3. **Check violation count** - High counts indicate persistent issues
4. **Review alarm history** - Use read_log to understand patterns
5. **Monitor latched alarms** - These require explicit clearing even after recovery