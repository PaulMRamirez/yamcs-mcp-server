"""Base server class for all Yamcs MCP component servers."""

from typing import Any

import structlog
from fastmcp import FastMCP

from ..client import YamcsClientManager
from ..config import YamcsConfig


class BaseYamcsServer(FastMCP):
    """Base server with common functionality for all Yamcs component servers."""

    def __init__(
        self,
        name: str,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
        version: str = "0.0.1-beta",
    ) -> None:
        """Initialize base server.

        Args:
            name: Component name (e.g., "MDB", "Links")
            client_manager: Yamcs client manager
            config: Yamcs configuration
            version: Server version
        """
        super().__init__(name=f"Yamcs{name}Server", version=version)
        
        self.component_name = name
        self.client_manager = client_manager
        self.config = config
        self.logger = structlog.get_logger(f"yamcs_mcp.{name.lower()}")

        # Register common tools
        self._register_common_tools()

    def _register_common_tools(self) -> None:
        """Register tools common to all component servers."""
        
        @self.tool()
        async def component_health() -> dict[str, Any]:
            """Check component server health.

            Returns:
                dict: Health status with details
            """
            try:
                # Test Yamcs connection
                connection_ok = await self.client_manager.test_connection()

                return {
                    "status": "healthy" if connection_ok else "unhealthy",
                    "component": self.component_name,
                    "server_name": self.name,
                    "yamcs_connected": connection_ok,
                    "yamcs_url": self.config.url,
                    "yamcs_instance": self.config.instance,
                }
            except Exception as e:
                self.logger.error("Health check failed", error=str(e))
                return {
                    "status": "unhealthy",
                    "component": self.component_name,
                    "server_name": self.name,
                    "error": str(e),
                }

    def _handle_error(self, operation: str, error: Exception) -> dict[str, Any]:
        """Handle errors consistently across component servers.

        Args:
            operation: Operation that failed
            error: Exception that occurred

        Returns:
            dict: Error response
        """
        self.logger.error(
            f"{operation} failed",
            operation=operation,
            error=str(error),
            error_type=type(error).__name__,
        )

        return {
            "error": True,
            "message": str(error),
            "operation": operation,
            "component": self.component_name,
            "server": self.name,
        }