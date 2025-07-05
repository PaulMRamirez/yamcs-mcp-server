"""Main Yamcs MCP Server implementation."""

import asyncio
import sys
from typing import Any

import structlog
from fastmcp import FastMCP
from rich.console import Console
from rich.logging import RichHandler

from .client import YamcsClientManager
from .components.archive import ArchiveComponent
from .components.instances import InstanceManagementComponent
from .components.links import LinkManagementComponent
from .components.mdb import MDBComponent
from .components.processor import ProcessorComponent
from .components.storage import ObjectStorageComponent
from .config import Config


def setup_logging(log_level: str = "INFO") -> None:
    """Set up structured logging with rich console output.

    Args:
        log_level: Logging level
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


class YamcsMCPServer:
    """Main Yamcs MCP Server that composes all components."""

    def __init__(self, config: Config | None = None) -> None:
        """Initialize the Yamcs MCP Server.

        Args:
            config: Server configuration, loads from environment if not provided
        """
        self.config = config or Config.from_env()
        setup_logging(self.config.yamcs.log_level)
        self.logger = structlog.get_logger(__name__)
        
        # Initialize client manager
        self.client_manager = YamcsClientManager(self.config.yamcs)
        
        # Initialize main MCP server
        self.mcp = FastMCP(
            name=self.config.yamcs.server_name,
            version="0.1.0",
        )
        
        # Initialize and compose components
        self._initialize_components()
        
        # Register server-wide tools
        self._register_server_tools()

    def _initialize_components(self) -> None:
        """Initialize and compose all enabled components."""
        self.logger.info("Initializing Yamcs MCP components")
        
        # Store components for reference
        self.components = []
        
        if self.config.yamcs.enable_mdb:
            self.logger.info("Enabling MDB component")
            mdb = MDBComponent(self.client_manager, self.config.yamcs)
            self.components.append(mdb)
            mdb.register_with_server(self.mcp)
        
        if self.config.yamcs.enable_processor:
            self.logger.info("Enabling Processor component")
            processor = ProcessorComponent(self.client_manager, self.config.yamcs)
            self.components.append(processor)
            processor.register_with_server(self.mcp)
        
        if self.config.yamcs.enable_archive:
            self.logger.info("Enabling Archive component")
            archive = ArchiveComponent(self.client_manager, self.config.yamcs)
            self.components.append(archive)
            archive.register_with_server(self.mcp)
        
        if self.config.yamcs.enable_links:
            self.logger.info("Enabling Link Management component")
            links = LinkManagementComponent(self.client_manager, self.config.yamcs)
            self.components.append(links)
            links.register_with_server(self.mcp)
        
        if self.config.yamcs.enable_storage:
            self.logger.info("Enabling Object Storage component")
            storage = ObjectStorageComponent(self.client_manager, self.config.yamcs)
            self.components.append(storage)
            storage.register_with_server(self.mcp)
        
        if self.config.yamcs.enable_instances:
            self.logger.info("Enabling Instance Management component")
            instances = InstanceManagementComponent(self.client_manager, self.config.yamcs)
            self.components.append(instances)
            instances.register_with_server(self.mcp)
        
        self.logger.info(f"Initialized {len(self.components)} components")

    def _register_server_tools(self) -> None:
        """Register server-wide tools."""
        
        @self.mcp.tool()
        async def health_check() -> dict[str, Any]:
            """Check overall server health.

            Returns:
                dict: Server health status
            """
            return {
                "status": "healthy",
                "server": self.config.yamcs.server_name,
                "version": "0.1.0",
                "yamcs_url": self.config.yamcs.url,
                "yamcs_instance": self.config.yamcs.instance,
                "transport": self.config.mcp.transport,
            }
        
        @self.mcp.tool()
        async def test_connection() -> dict[str, Any]:
            """Test connection to Yamcs server.

            Returns:
                dict: Connection test results
            """
            try:
                connected = await self.client_manager.test_connection()
                return {
                    "connected": connected,
                    "yamcs_url": self.config.yamcs.url,
                    "message": "Connection successful" if connected else "Connection failed",
                }
            except Exception as e:
                return {
                    "connected": False,
                    "yamcs_url": self.config.yamcs.url,
                    "error": str(e),
                }

    async def run(self) -> None:
        """Run the MCP server."""
        self.logger.info(
            "Starting Yamcs MCP Server",
            transport=self.config.mcp.transport,
            yamcs_url=self.config.yamcs.url,
        )
        
        # Test Yamcs connection before starting
        if not await self.client_manager.test_connection():
            self.logger.warning(
                "Failed to connect to Yamcs server - running in demo mode",
                url=self.config.yamcs.url,
            )
            # Continue in demo mode without exiting
        
        # Run server based on transport
        if self.config.mcp.transport == "stdio":
            # For stdio, we need to run_async directly since we're already in an event loop
            await self.mcp.run_async()
        else:
            # HTTP/SSE transport
            await self.mcp.run_async(
                transport=self.config.mcp.transport,
                host=self.config.mcp.host,
                port=self.config.mcp.port,
            )


def main() -> None:
    """Main entry point for the Yamcs MCP Server."""
    # Create console for rich output
    console = Console()
    
    try:
        # Load configuration
        config = Config.from_env()
        
        # Create and run server
        server = YamcsMCPServer(config)
        
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're here, we're already in a loop (e.g., Jupyter)
            console.print("[yellow]Already running in an event loop[/yellow]")
            # Create a task for the server
            task = loop.create_task(server.run())
            loop.run_until_complete(task)
        except RuntimeError:
            # No event loop running, create one
            asyncio.run(server.run())
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Server error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()