"""Base server class for all Yamcs MCP servers."""

from typing import Any

import structlog
from fastmcp import FastMCP

from ..client import YamcsClientManager
from ..config import YamcsConfig


class BaseYamcsServer(FastMCP):
    """Base server with common functionality for all Yamcs servers."""

    def __init__(
        self,
        name: str,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
        version: str = "0.1.0-beta",
    ) -> None:
        """Initialize base server.

        Args:
            name: Server name (e.g., "MDB", "Links")
            client_manager: Yamcs client manager
            config: Yamcs configuration
            version: Server version
        """
        super().__init__(name=f"Yamcs{name}Server", version=version)

        self.server_name = name
        self.client_manager = client_manager
        self.config = config
        self.logger = structlog.get_logger(f"yamcs_mcp.{name.lower()}")

    def _handle_error(self, operation: str, error: Exception) -> dict[str, Any]:
        """Handle errors consistently across servers.

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
            "server_type": self.server_name,
            "server": self.name,
        }
