#!/usr/bin/env python
"""Test script to verify link_get_status works correctly."""

import asyncio
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yamcs_mcp.server import YamcsMCPServer
from yamcs_mcp.config import Config


async def test_link_get_status():
    """Test the link_get_status functionality."""
    print("🔧 Testing Link Get Status")
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
    
    # Test get_link with LinkClient
    print("\n📊 Testing link_get_status...")
    try:
        async with server.client_manager.get_client() as client:
            # Get the correct instance
            instances = list(client.list_instances())
            if instances:
                actual_instance = instances[0].name
                print(f"📍 Using instance: {actual_instance}")
            else:
                actual_instance = config.yamcs.instance
            
            # First list links to find one to test
            links = list(client.list_links(actual_instance))
            if not links:
                print("❌ No links found")
                return
                
            # Test with the first link
            test_link_name = links[0].name
            print(f"\n🔍 Testing with link: {test_link_name}")
            
            # Get link using get_link (returns LinkClient)
            link_client = client.get_link(actual_instance, test_link_name)
            print(f"✅ Got LinkClient: {type(link_client)}")
            
            # Get link info
            link_info = link_client.get_info()
            print(f"✅ Got Link info: {type(link_info)}")
            
            # Display link information
            print(f"\n📡 Link Information:")
            print(f"   Name: {link_info.name}")
            print(f"   Status: {link_info.status}")
            print(f"   Type: {getattr(link_info, 'type', 'unknown')}")
            print(f"   Disabled: {getattr(link_info, 'disabled', False)}")
            print(f"   In Count: {getattr(link_info, 'in_count', 0):,}")
            print(f"   Out Count: {getattr(link_info, 'out_count', 0):,}")
            print(f"   Details: {getattr(link_info, 'detail_status', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error testing link status: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_link_get_status())