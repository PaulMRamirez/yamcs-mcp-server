# Troubleshooting Guide

## Common Issues

### 1. "spawn uv ENOENT" Error in Claude Desktop

**Problem**: Claude Desktop cannot find the `uv` command in its PATH.

**Solutions**:

1. **Use the wrapper script** (recommended):
   ```json
   {
     "mcp-servers": {
       "yamcs": {
         "command": "/path/to/yamcs-mcp-server/yamcs-mcp-wrapper.sh"
       }
     }
   }
   ```

2. **Use full path to uv**:
   ```json
   {
     "mcp-servers": {
       "yamcs": {
         "command": "/Users/pramirez/.local/bin/uv",
         "args": ["run", "yamcs-mcp"],
         "cwd": "/path/to/yamcs-mcp-server"
       }
     }
   }
   ```

3. **Use Python directly**:
   ```json
   {
     "mcp-servers": {
       "yamcs": {
         "command": "python3",
         "args": ["/path/to/yamcs-mcp-server/run_server.py"]
       }
     }
   }
   ```

### 2. Connection to Yamcs Failed

**Problem**: Server cannot connect to Yamcs instance.

**Solutions**:

1. **Verify Yamcs is running**:
   ```bash
   curl http://localhost:8090/api
   ```

2. **Check Docker container** (if using Docker):
   ```bash
   docker ps
   docker logs yamcs
   ```

3. **Verify environment variables**:
   ```bash
   echo $YAMCS_URL
   echo $YAMCS_INSTANCE
   ```

4. **Test with yamcs-client directly**:
   ```bash
   uv run python -c "from yamcs.client import YamcsClient; print(YamcsClient('http://localhost:8090').get_server_info())"
   ```

### 3. Module Import Errors

**Problem**: Python cannot find yamcs_mcp modules.

**Solutions**:

1. **Install in development mode**:
   ```bash
   uv pip install -e .
   ```

2. **Verify installation**:
   ```bash
   uv run python -c "import yamcs_mcp; print(yamcs_mcp.__version__)"
   ```

3. **Check Python path**:
   ```bash
   uv run python -c "import sys; print('\n'.join(sys.path))"
   ```

### 4. Authentication Errors

**Problem**: Yamcs requires authentication but credentials are not set.

**Solutions**:

1. **Set credentials in environment**:
   ```bash
   export YAMCS_USERNAME=admin
   export YAMCS_PASSWORD=password
   ```

2. **Or in .env file**:
   ```
   YAMCS_USERNAME=admin
   YAMCS_PASSWORD=password
   ```

3. **Or in Claude Desktop config**:
   ```json
   {
     "env": {
       "YAMCS_USERNAME": "admin",
       "YAMCS_PASSWORD": "password"
     }
   }
   ```

### 5. Missing Dependencies

**Problem**: Required packages are not installed.

**Solutions**:

1. **Install all dependencies**:
   ```bash
   uv sync --all-extras
   ```

2. **Verify installations**:
   ```bash
   uv pip list | grep -E "(fastmcp|yamcs-client|pydantic)"
   ```

3. **Reinstall if needed**:
   ```bash
   uv pip install -r requirements.txt
   ```

## Debugging Steps

### 1. Enable Debug Logging

Set log level to DEBUG:
```bash
YAMCS_LOG_LEVEL=DEBUG uv run yamcs-mcp
```

Or in Claude Desktop config:
```json
{
  "env": {
    "YAMCS_LOG_LEVEL": "DEBUG"
  }
}
```

### 2. Check Server Logs

Claude Desktop logs are located at:
- macOS: `~/Library/Logs/Claude/mcp-server-*.log`
- Windows: `%APPDATA%\Claude\logs\mcp-server-*.log`
- Linux: `~/.config/Claude/logs/mcp-server-*.log`

### 3. Test Individual Components

Test MDB component:
```python
from yamcs_mcp.components.mdb import MDBComponent
from yamcs_mcp.client import YamcsClientManager
from yamcs_mcp.config import YamcsConfig

config = YamcsConfig()
client_manager = YamcsClientManager(config)
mdb = MDBComponent(client_manager, config)

# Test a tool
result = await mdb.mdb_list_parameters()
print(result)
```

### 4. Verify Yamcs API Access

Test raw API access:
```bash
# List instances
curl http://localhost:8090/api/instances

# Get MDB info
curl http://localhost:8090/api/mdb/myproject/parameters

# Check processor status
curl http://localhost:8090/api/processors/myproject/realtime
```

## Performance Issues

### 1. Slow Response Times

**Causes**:
- Large parameter/command lists
- Network latency to Yamcs
- Unoptimized queries

**Solutions**:
- Use pagination/limits in queries
- Run Yamcs locally if possible
- Cache MDB data (future enhancement)

### 2. High Memory Usage

**Causes**:
- Loading too much historical data
- Not limiting query results
- Memory leaks in long-running processes

**Solutions**:
- Always use `limit` parameter in queries
- Implement streaming for large datasets
- Monitor memory with: `uv run mprof run yamcs-mcp`

## Getting Help

1. **Check the documentation**:
   - [Architecture Guide](architecture.md)
   - [API Reference](api.md)
   - [Development Guide](development.md)

2. **Enable verbose logging**:
   ```bash
   YAMCS_LOG_LEVEL=DEBUG uv run yamcs-mcp 2>&1 | tee debug.log
   ```

3. **Report issues**:
   - Include Python version: `python --version`
   - Include package versions: `uv pip list`
   - Include relevant log snippets
   - Include minimal reproduction steps