#!/Users/pramirez/Development/ClaudeCode/yamcs-mcp-server/.venv/bin/python
"""Clean runner for Yamcs MCP Server that suppresses warnings."""

import sys
import os
import warnings

# Suppress all deprecation warnings from yamcs-client
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Set environment to suppress protobuf warnings
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the server
from yamcs_mcp.server import main

if __name__ == "__main__":
    main()