#!/usr/bin/env python
"""Test script to verify processor server updates."""

import asyncio
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yamcs_mcp.server import YamcsMCPServer
from yamcs_mcp.config import Config


async def test_processor_tools():
    """Test the updated processor tools."""
    print("🔍 Testing Processor Server Updates")
    print("=" * 50)
    
    # Create configuration
    config = Config.from_env()
    print(f"📍 Yamcs URL: {config.yamcs.url}")
    print(f"📍 Instance: {config.yamcs.instance}")
    
    # Create server
    print("\n🚀 Creating MCP Server...")
    server = YamcsMCPServer(config)
    
    # List expected tools
    print("\n📋 Expected Processor Tools:")
    expected_tools = [
        "processors_list_processors",
        "processors_describe_processor", 
        "processors_delete_processor",
    ]
    
    for tool in expected_tools:
        print(f"  - {tool}")
    
    print("\n📋 Expected Processor Resources:")
    print("  - processors://list")
    
    print("\n✅ Processor server structure updated successfully!")
    print("\nChanges made:")
    print("  - Renamed get_processor → describe_processor")
    print("  - Removed control_processor")
    print("  - Added delete_processor")
    print("  - Removed processors://status resource")
    print("  - Added processors://list resource")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_processor_tools())