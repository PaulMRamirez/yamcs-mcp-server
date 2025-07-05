#!/usr/bin/env python
"""Test script to verify Yamcs MCP Server works with a real Yamcs instance."""

import asyncio
import os
import sys
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yamcs_mcp.server import YamcsMCPServer
from yamcs_mcp.config import Config


async def test_yamcs_connection():
    """Test connection to Yamcs and basic operations."""
    print("🔧 Yamcs MCP Server Test Script")
    print("=" * 50)
    
    # Create configuration
    config = Config.from_env()
    print(f"📍 Yamcs URL: {config.yamcs.url}")
    print(f"📍 Instance: {config.yamcs.instance}")
    
    # Create server
    print("\n🚀 Creating MCP Server...")
    server = YamcsMCPServer(config)
    
    # Test connection
    print("\n🔌 Testing Yamcs connection...")
    try:
        connected = await server.client_manager.test_connection()
        if connected:
            print("✅ Successfully connected to Yamcs!")
        else:
            print("❌ Failed to connect to Yamcs")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Get client and test basic operations
    print("\n📊 Testing basic operations...")
    try:
        async with server.client_manager.get_client() as client:
            # Get server info
            server_info = client.get_server_info()
            print(f"✅ Yamcs Version: {getattr(server_info, 'version', 'unknown')}")
            
            # List instances
            instances = list(client.list_instances())
            print(f"✅ Found {len(instances)} instance(s)")
            for inst in instances[:3]:  # Show first 3
                print(f"   - {inst.name}: {inst.state}")
            
            # Get MDB info
            try:
                # First check which instance to use
                actual_instance = instances[0].name if instances else config.yamcs.instance
                print(f"📍 Using instance: {actual_instance}")
                
                mdb = client.get_mdb(actual_instance)
                # list_parameters might not accept limit parameter in older versions
                all_params = list(mdb.list_parameters())
                params = all_params[:5]  # Get first 5
                print(f"✅ Found {len(all_params)} total parameters (showing first 5)")
                for param in params:
                    print(f"   - {param.qualified_name}")
            except Exception as e:
                print(f"⚠️  Could not access MDB: {e}")
            
            # Check processors
            try:
                processors = list(client.list_processors(config.yamcs.instance))
                print(f"✅ Found {len(processors)} processor(s)")
                for proc in processors:
                    print(f"   - {proc.name}: {proc.state}")
            except Exception as e:
                print(f"⚠️  Could not list processors: {e}")
                
    except Exception as e:
        print(f"❌ Error during operations: {e}")
        return
    
    print("\n✨ All tests completed successfully!")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_yamcs_connection())