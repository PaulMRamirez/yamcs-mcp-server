#!/bin/bash
# Wrapper script for Claude to run Yamcs MCP Server

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Add uv to PATH
export PATH="/Users/pramirez/.local/bin:$PATH"

# Change to the project directory
cd "$SCRIPT_DIR"

# Debug output
echo "Working directory: $(pwd)" >&2
echo "Running: uv run yamcs-mcp $@" >&2

# Run the server using uv
exec /Users/pramirez/.local/bin/uv run yamcs-mcp "$@"