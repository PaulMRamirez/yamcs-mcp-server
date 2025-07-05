#!/usr/bin/env python3
"""Test script to verify server can start."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Suppress deprecation warnings from yamcs-client
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

async def test_server():
    """Test basic server functionality."""
    try:
        from yamcs_mcp.server import YamcsMCPServer
        from yamcs_mcp.config import Config
        
        print("Loading configuration...")
        config = Config.from_env()
        
        print(f"Yamcs URL: {config.yamcs.url}")
        print(f"Yamcs Instance: {config.yamcs.instance}")
        
        print("Creating server...")
        server = YamcsMCPServer(config)
        
        print("Testing connection...")
        # Just test that we can create the server
        # Don't actually run it
        
        print("✅ Server created successfully!")
        print("\nTo run the server, use one of these methods:")
        print("1. uv run yamcs-mcp")
        print("2. ./yamcs-mcp-wrapper.sh")
        print("3. python3 run_server.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_server())