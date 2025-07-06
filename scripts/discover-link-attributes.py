#!/usr/bin/env python
"""Script to discover all available attributes on a Yamcs Link object."""

import asyncio
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yamcs_mcp.server import YamcsMCPServer
from yamcs_mcp.config import Config


async def discover_link_attributes():
    """Discover all attributes available on Link objects."""
    print("🔍 Discovering Link Attributes")
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
        if not connected:
            print("❌ Failed to connect to Yamcs")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Get link information
    print("\n📊 Getting link information...")
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
            print(f"\n🔍 Examining link: {test_link_name}")
            
            # Get link using get_link (returns LinkClient)
            link_client = client.get_link(actual_instance, test_link_name)
            
            # Get link info
            link_info = link_client.get_info()
            
            # Display all attributes
            print(f"\n📋 All attributes on link_info object:")
            print(f"   Type: {type(link_info)}")
            print(f"   Module: {type(link_info).__module__}")
            
            # Get all attributes
            all_attrs = dir(link_info)
            
            # Filter out private/magic methods
            public_attrs = [attr for attr in all_attrs if not attr.startswith('_')]
            
            print(f"\n🔧 Public attributes ({len(public_attrs)} total):")
            for attr in sorted(public_attrs):
                try:
                    value = getattr(link_info, attr, '<not accessible>')
                    # Skip methods
                    if callable(value):
                        continue
                    print(f"   - {attr}: {value}")
                except Exception as e:
                    print(f"   - {attr}: <error accessing: {e}>")
            
            # Check for specific timestamp-related attributes
            print("\n⏰ Checking timestamp-related attributes:")
            timestamp_attrs = [
                'dataInTime', 'dataOutTime', 'data_in_time', 'data_out_time',
                'lastDataIn', 'lastDataOut', 'last_data_in', 'last_data_out',
                'inTime', 'outTime', 'in_time', 'out_time',
                'lastInTime', 'lastOutTime', 'last_in_time', 'last_out_time',
                'timestamp', 'lastActivity', 'last_activity'
            ]
            
            for attr in timestamp_attrs:
                if hasattr(link_info, attr):
                    value = getattr(link_info, attr, None)
                    print(f"   ✅ {attr}: {value}")
            
            # Also check the raw protobuf if available
            if hasattr(link_info, '_proto'):
                print("\n🔬 Checking raw protobuf attributes:")
                proto = link_info._proto
                proto_attrs = dir(proto)
                proto_public = [attr for attr in proto_attrs if not attr.startswith('_')]
                
                for attr in sorted(proto_public):
                    if 'time' in attr.lower() or 'data' in attr.lower():
                        try:
                            value = getattr(proto, attr, '<not accessible>')
                            if not callable(value):
                                print(f"   - {attr}: {value}")
                        except:
                            pass
            
    except Exception as e:
        print(f"❌ Error discovering link attributes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the discovery
    asyncio.run(discover_link_attributes())