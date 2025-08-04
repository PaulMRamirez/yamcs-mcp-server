# Link Tools

Link tools manage data links for telemetry reception and command transmission.

## Available Tools

| Tool | Purpose |
|------|---------|
| `links/list_links` | List all data links and their status |
| `links/describe_link` | Get detailed link information |
| `links/enable_link` | Enable a data link |
| `links/disable_link` | Disable a data link |

## Tools Reference

### links/list_links

List all data links in an instance.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `instance` | string | No | Yamcs instance name (uses default if not specified) |

**Example prompts:**
- "Show me all data links"
- "Which links are currently disabled?"
- "Check the status of telemetry links"

**Sample response:**
```json
{
  "instance": "simulator",
  "count": 4,
  "links": [
    {
      "name": "tm_realtime",
      "type": "TcpTmDataLink",
      "status": "OK",
      "disabled": false,
      "parent": null,
      "data_in_count": 1500000,
      "data_out_count": 0
    },
    {
      "name": "tc_realtime",
      "type": "TcpTcDataLink",
      "status": "OK",
      "disabled": false,
      "parent": null,
      "data_in_count": 0,
      "data_out_count": 250
    }
  ]
}
```

### links/describe_link

Get comprehensive information about a specific link.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `link` | string | Yes | Link name (e.g., "tm_realtime") |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Show me details about the tm_realtime link"
- "What's the configuration of the command uplink?"
- "Check if the telemetry link is connected"

**Sample response:**
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
    "data_in_count": 1500000,
    "data_out_count": 0,
    "last_received": "2024-01-15T12:34:56Z",
    "data_rate": 1024.5
  },
  "config": {
    "host": "localhost",
    "port": 10015,
    "reconnection_interval": 10
  }
}
```

### links/enable_link

Enable a disabled data link.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `link` | string | Yes | Link name to enable |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Enable the tm_realtime link"
- "Turn on the telemetry downlink"
- "Activate the command uplink"

**Sample response:**
```json
{
  "success": true,
  "link": "tm_realtime",
  "operation": "enable",
  "message": "Link 'tm_realtime' enabled successfully",
  "new_status": "OK"
}
```

### links/disable_link

Disable an active data link.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `link` | string | Yes | Link name to disable |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Disable the tc_realtime link"
- "Turn off the command uplink"
- "Stop receiving telemetry"

**Sample response:**
```json
{
  "success": true,
  "link": "tc_realtime",
  "operation": "disable",
  "message": "Link 'tc_realtime' disabled successfully"
}
```

## Resources

### links://status

Provides a formatted summary of all links and their current status.

**Example prompt:** "Show me the links status resource"

## Link Status Values

| Status | Description |
|--------|-------------|
| `OK` | Link operational and connected |
| `UNAVAIL` | Link unavailable or disconnected |
| `DISABLED` | Link manually disabled |
| `FAILED` | Link failed due to error |
| `ESTABLISHING` | Connection being established |

## Link Types

Common link types you may encounter:

| Type | Direction | Purpose |
|------|-----------|---------|
| `TcpTmDataLink` | Inbound | Receives telemetry via TCP |
| `TcpTcDataLink` | Outbound | Sends commands via TCP |
| `UdpTmDataLink` | Inbound | Receives telemetry via UDP |
| `FilePollingTmDataLink` | Inbound | Reads telemetry from files |
| `CfdpDataLink` | Bidirectional | CFDP file transfer |

## Common Use Cases

### Pre-Pass Configuration

> "Enable all telemetry and command links for the upcoming pass"

The AI will:
1. Use `links/list_links` to find all links
2. Use `links/enable_link` for any disabled links

### Link Health Check

> "Show me any links that are not OK or are disabled"

The AI will use `links/list_links` and filter for problematic links

### Data Rate Monitoring

> "What's the current data rate on the telemetry link?"

The AI will use `links/describe_link` to show statistics including data rate

### Troubleshooting Connections

> "The telemetry link seems down. Check its status and try to enable it"

The AI will:
1. Use `links/describe_link` to check detailed status
2. Use `links/enable_link` if the link is disabled

## Tips

1. **Check parent links** - Some links depend on parent links being enabled
2. **Monitor data counts** - Verify data is flowing with in/out counts
3. **Review last received time** - Check when data was last received
4. **Understand link types** - Different types have different capabilities
5. **Check connection details** - Use describe_link for connection parameters