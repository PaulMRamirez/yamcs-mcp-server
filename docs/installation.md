# Installation

## Requirements

- Python 3.11 or higher
- Access to a Yamcs instance (5.8.0 or higher)
- pip or uv package manager

## Install from PyPI

The simplest way to install yamcs-mcp-server is from PyPI:

```bash
pip install yamcs-mcp-server
```

Or using uv:

```bash
uv pip install yamcs-mcp-server
```

## Install from Source

To install the latest development version:

```bash
git clone https://github.com/yourusername/yamcs-mcp-server.git
cd yamcs-mcp-server
pip install -e .
```

Or using uv:

```bash
git clone https://github.com/yourusername/yamcs-mcp-server.git
cd yamcs-mcp-server
uv pip install -e .
```

## Docker Installation

A Docker image is available for easy deployment:

```bash
docker pull yourusername/yamcs-mcp-server:latest

docker run -it \
  -e YAMCS_URL=http://localhost:8090 \
  -e YAMCS_INSTANCE=simulator \
  yourusername/yamcs-mcp-server
```

## Verify Installation

After installation, verify everything is working:

```bash
# Check version
python -m yamcs_mcp --version

# Test connection to Yamcs
python -m yamcs_mcp test-connection
```

## Development Installation

For development, install with all extras:

```bash
git clone https://github.com/yourusername/yamcs-mcp-server.git
cd yamcs-mcp-server

# Install with development dependencies
pip install -e ".[dev]"

# Or using uv
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Next Steps

- [Configure](configuration.md) your Yamcs connection
- Follow the [Quick Start](quickstart.md) guide
- Explore [Examples](examples.md)