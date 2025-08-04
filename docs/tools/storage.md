# Storage Tools

Storage tools manage object storage buckets and their contents in Yamcs.

## Available Tools

| Tool | Purpose |
|------|---------|
| `storage/list_buckets` | List all storage buckets |
| `storage/list_objects` | List objects in a bucket |
| `storage/upload_object` | Upload data to a bucket |
| `storage/delete_object` | Delete an object from a bucket |
| `storage/create_bucket` | Create a new storage bucket |

## Tools Reference

### storage/list_buckets

List all storage buckets in an instance.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `instance` | string | No | Yamcs instance name (uses default if not specified) |

**Example prompts:**
- "Show me all storage buckets"
- "List available data storage"
- "What buckets exist for telemetry?"

**Sample response:**
```json
{
  "instance": "simulator",
  "count": 3,
  "buckets": [
    {
      "name": "telemetry",
      "created": "2024-01-01T00:00:00Z",
      "size": 52428800,
      "object_count": 1250
    },
    {
      "name": "commands",
      "created": "2024-01-01T00:00:00Z",
      "size": 1048576,
      "object_count": 45
    },
    {
      "name": "configs",
      "created": "2024-01-10T00:00:00Z",
      "size": 524288,
      "object_count": 12
    }
  ]
}
```

### storage/list_objects

List objects in a specific bucket.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `bucket` | string | Yes | Bucket name |
| `prefix` | string | No | Filter objects by name prefix |
| `instance` | string | No | Yamcs instance name |
| `limit` | integer | No | Maximum objects to return (default: 100) |

**Example prompts:**
- "List files in the telemetry bucket"
- "Show me today's data in the telemetry bucket"
- "What configuration files are stored?"

**Sample response:**
```json
{
  "bucket": "telemetry",
  "instance": "simulator",
  "count": 50,
  "objects": [
    {
      "name": "2024/01/15/tm_120000.dat",
      "size": 102400,
      "created": "2024-01-15T12:00:00Z",
      "metadata": {
        "content-type": "application/octet-stream",
        "source": "tm_realtime"
      }
    },
    {
      "name": "2024/01/15/tm_130000.dat",
      "size": 98304,
      "created": "2024-01-15T13:00:00Z",
      "metadata": {}
    }
  ]
}
```

### storage/upload_object

Upload data to a storage bucket.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `bucket` | string | Yes | Target bucket name |
| `object_name` | string | Yes | Name for the object |
| `data` | string | Yes | Base64 encoded data or text content |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Upload this configuration to the configs bucket"
- "Save this data file to storage"
- "Store this command sequence"

**Sample response:**
```json
{
  "success": true,
  "bucket": "configs",
  "object": "mission-config-v2.json",
  "size": 2048,
  "url": "/storage/configs/mission-config-v2.json"
}
```

### storage/delete_object

Delete an object from a bucket.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `bucket` | string | Yes | Bucket name |
| `object_name` | string | Yes | Object name to delete |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Delete the old configuration file"
- "Remove yesterday's telemetry data"
- "Clean up test files from storage"

**Sample response:**
```json
{
  "success": true,
  "bucket": "configs",
  "object": "test-config.json",
  "message": "Object 'test-config.json' deleted from bucket 'configs'"
}
```

### storage/create_bucket

Create a new storage bucket.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | Yes | Bucket name (must be unique) |
| `instance` | string | No | Yamcs instance name |

**Example prompts:**
- "Create a bucket for mission reports"
- "Make a new storage area for analysis results"
- "Set up a bucket for temporary data"

**Sample response:**
```json
{
  "success": true,
  "bucket": {
    "name": "mission-reports",
    "created": "2024-01-15T14:30:00Z"
  },
  "message": "Bucket 'mission-reports' created successfully"
}
```

## Resources

### storage://overview

Provides a formatted summary of storage usage across all buckets.

**Example prompt:** "Show me the storage overview resource"

## Common Use Cases

### Data Organization

> "Show me how much storage each bucket is using"

The AI will use `storage/list_buckets` to show sizes and object counts

### Finding Recent Data

> "List the most recent telemetry files from today"

The AI will use `storage/list_objects` with a date prefix filter

### Configuration Management

> "Upload this new mission configuration file"

The AI will use `storage/upload_object` to store the configuration

### Cleanup Operations

> "Delete all test files from the configs bucket"

The AI will:
1. Use `storage/list_objects` with prefix="test"
2. Use `storage/delete_object` for each test file

### Storage Setup

> "Create a new bucket for this week's mission data"

The AI will use `storage/create_bucket` with an appropriate name

## Object Naming Conventions

Common patterns for object names:

| Pattern | Example | Use Case |
|---------|---------|----------|
| Date-based | `2024/01/15/data.dat` | Time-series data |
| Version-based | `config-v2.3.json` | Configuration files |
| Type-based | `tm/realtime/chunk001.dat` | Categorized data |
| Session-based | `pass-123/telemetry.dat` | Pass-specific data |

## Tips

1. **Use prefixes** - Organize objects with path-like prefixes
2. **Set limits** - Use the limit parameter to avoid large responses
3. **Check sizes** - Monitor bucket sizes to manage storage
4. **Use metadata** - Objects can have metadata for additional context
5. **Plan naming** - Use consistent naming conventions for easy retrieval