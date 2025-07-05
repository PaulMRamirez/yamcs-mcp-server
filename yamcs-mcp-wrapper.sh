#!/bin/bash
# Wrapper script for Claude to run Yamcs MCP Server

# Add uv to PATH
export PATH="/Users/pramirez/.local/bin:$PATH"

# Change to the project directory
cd "$(dirname "$0")"

# Run the server using uv
exec uv run yamcs-mcp "$@"