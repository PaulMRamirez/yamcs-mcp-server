#!/bin/bash
# Script to run Yamcs MCP Server with proper environment setup

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Check if dependencies are installed
if [ ! -d ".venv" ]; then
    echo "Installing dependencies..."
    uv sync --all-extras
fi

# Run the server
echo "Starting Yamcs MCP Server..."
uv run yamcs-mcp