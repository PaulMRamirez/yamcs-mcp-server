#!/bin/bash
# Clean wrapper that suppresses all warnings

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Set environment to suppress warnings
export PYTHONWARNINGS="ignore"
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION="python"

# Run the server, redirecting stderr warnings to /dev/null but keeping error messages
exec /Users/pramirez/.local/bin/uv run yamcs-mcp "$@" 2>&1 | grep -v "Warning" | grep -v "Deprecated"