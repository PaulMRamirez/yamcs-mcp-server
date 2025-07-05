# Configuration

Yamcs MCP Server can be configured through environment variables, configuration files, or programmatically.

## Environment Variables

The following environment variables can be used to configure the server:

### Yamcs Connection

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `YAMCS_URL` | Yamcs server URL | - | Yes |
| `YAMCS_INSTANCE` | Default Yamcs instance | - | Yes |
| `YAMCS_USERNAME` | Username for authentication | - | No |
| `YAMCS_PASSWORD` | Password for authentication | - | No |

### Component Selection

| Variable | Description | Default |
|----------|-------------|---------|
| `YAMCS_MCP_ENABLE_MDB` | Enable Mission Database component | `true` |
| `YAMCS_MCP_ENABLE_PROCESSOR` | Enable Processor component | `true` |
| `YAMCS_MCP_ENABLE_ARCHIVE` | Enable Archive component | `true` |
| `YAMCS_MCP_ENABLE_LINKS` | Enable Link Management component | `true` |
| `YAMCS_MCP_ENABLE_STORAGE` | Enable Object Storage component | `true` |
| `YAMCS_MCP_ENABLE_INSTANCES` | Enable Instance Management component | `true` |

### MCP Server Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_TRANSPORT` | Transport type (`stdio` or `http`) | `stdio` |
| `MCP_HOST` | Host for HTTP transport | `127.0.0.1` |
| `MCP_PORT` | Port for HTTP transport | `8000` |

### Logging

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |

## Configuration File

You can also use a YAML configuration file:

```yaml
# config.yml
yamcs:
  url: http://localhost:8090
  instance: simulator
  username: operator
  password: secret
  
  # Component selection
  enable_mdb: true
  enable_processor: true
  enable_archive: true
  enable_links: true
  enable_storage: true
  enable_instances: true

mcp:
  transport: stdio
  # For HTTP transport:
  # transport: http
  # host: 0.0.0.0
  # port: 8000

logging:
  level: INFO
```

Load the configuration file:

```python
from yamcs_mcp.config import Config

config = Config.from_file("config.yml")
```

## Programmatic Configuration

```python
from yamcs_mcp.config import Config, YamcsConfig, MCPConfig

config = Config(
    yamcs=YamcsConfig(
        url="http://localhost:8090",
        instance="simulator",
        username="operator",
        password="secret",
        enable_mdb=True,
        enable_processor=True,
        enable_archive=True,
        enable_links=True,
        enable_storage=True,
        enable_instances=True,
    ),
    mcp=MCPConfig(
        transport="stdio",
    )
)
```

## Authentication

### Basic Authentication

Set username and password via environment variables:

```bash
export YAMCS_USERNAME=operator
export YAMCS_PASSWORD=mysecret
```

### API Key Authentication

For API key authentication, use a custom header:

```python
# Not yet implemented - planned feature
config = Config(
    yamcs=YamcsConfig(
        url="http://localhost:8090",
        api_key="your-api-key",
    )
)
```

## Transport Options

### stdio Transport (Default)

The stdio transport is used for direct process communication:

```bash
export MCP_TRANSPORT=stdio
python -m yamcs_mcp
```

This is the recommended mode for use with AI assistants.

### HTTP Transport

For network-based communication:

```bash
export MCP_TRANSPORT=http
export MCP_HOST=0.0.0.0
export MCP_PORT=8000
python -m yamcs_mcp
```

## Component Configuration

You can selectively enable/disable components based on your needs:

```bash
# Only enable MDB and Processor components
export YAMCS_MCP_ENABLE_MDB=true
export YAMCS_MCP_ENABLE_PROCESSOR=true
export YAMCS_MCP_ENABLE_ARCHIVE=false
export YAMCS_MCP_ENABLE_LINKS=false
export YAMCS_MCP_ENABLE_STORAGE=false
export YAMCS_MCP_ENABLE_INSTANCES=false
```

This is useful for:
- Reducing memory footprint
- Limiting access to certain Yamcs features
- Creating specialized MCP servers

## Advanced Configuration

### Connection Pooling

```python
# Not yet implemented - planned feature
config = Config(
    yamcs=YamcsConfig(
        url="http://localhost:8090",
        connection_pool_size=10,
        connection_timeout=30,
    )
)
```

### Retry Configuration

```python
# Not yet implemented - planned feature
config = Config(
    yamcs=YamcsConfig(
        url="http://localhost:8090",
        retry_attempts=3,
        retry_delay=1.0,
        retry_backoff=2.0,
    )
)
```

## Security Considerations

1. **Credentials**: Never commit credentials to version control
2. **HTTPS**: Use HTTPS for Yamcs connections in production
3. **Firewall**: Restrict network access to MCP server ports
4. **Minimal Components**: Only enable needed components

## Example Configurations

### Development Setup

```bash
export YAMCS_URL=http://localhost:8090
export YAMCS_INSTANCE=simulator
export LOG_LEVEL=DEBUG
python -m yamcs_mcp
```

### Production Setup

```bash
export YAMCS_URL=https://yamcs.example.com
export YAMCS_INSTANCE=ops
export YAMCS_USERNAME=mcp_service
export YAMCS_PASSWORD="${YAMCS_SERVICE_PASSWORD}"
export LOG_LEVEL=WARNING
export YAMCS_MCP_ENABLE_INSTANCES=false  # Restrict instance management
python -m yamcs_mcp
```

### Docker Setup

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install .

ENV YAMCS_URL=http://yamcs:8090
ENV YAMCS_INSTANCE=ops
ENV MCP_TRANSPORT=stdio

CMD ["python", "-m", "yamcs_mcp"]
```