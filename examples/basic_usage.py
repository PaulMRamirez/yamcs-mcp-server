"""Basic usage example for Yamcs MCP Server.

This example demonstrates the server composition architecture where each
Yamcs server (MDB, Links, Archive, etc.) is a separate FastMCP server
that gets mounted to the main server with a prefix.
"""

import asyncio
import os

from yamcs_mcp import Config, YamcsMCPServer


async def main():
    """Run a basic example of the Yamcs MCP Server."""

    # Configure the server
    # You can set these via environment variables or .env file
    os.environ["YAMCS_URL"] = "http://localhost:8090"
    os.environ["YAMCS_INSTANCE"] = "simulator"
    os.environ["MCP_TRANSPORT"] = "stdio"

    # Create configuration
    config = Config.from_env()

    # Create server - this will mount all enabled sub-servers
    server = YamcsMCPServer(config)

    # Run the server
    print("Starting Yamcs MCP Server with server composition...")
    print(f"Connecting to Yamcs at {config.yamcs.url}")
    print(f"Default instance: {config.yamcs.instance}")
    print(f"Transport: {config.mcp.transport}")
    
    # The server mounts all enabled sub-servers automatically

    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
