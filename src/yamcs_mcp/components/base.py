"""Base component for all Yamcs MCP components."""

from abc import ABC, abstractmethod
from typing import Any

import structlog

from ..client import YamcsClientManager
from ..config import YamcsConfig


class BaseYamcsComponent(ABC):
    """Base component with common functionality for all Yamcs components."""

    def __init__(
        self,
        name: str,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize base component.

        Args:
            name: Component name
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        self.name = f"Yamcs{name}"
        self.client_manager = client_manager
        self.config = config
        self.logger = structlog.get_logger(f"yamcs_mcp.{name.lower()}")
        
        # Store tools and resources
        self.tools = []
        self.resources = []

    @abstractmethod
    def register_with_server(self, server: Any) -> None:
        """Register this component's tools and resources with a server.
        
        Args:
            server: FastMCP server instance
        """
        pass

    async def health_check(self) -> dict[str, Any]:
        """Check component health.

        Returns:
            dict: Health status with details
        """
        try:
            # Test Yamcs connection
            connection_ok = await self.client_manager.test_connection()
            
            return {
                "status": "healthy" if connection_ok else "unhealthy",
                "component": self.name,
                "yamcs_connected": connection_ok,
                "yamcs_url": self.config.url,
                "yamcs_instance": self.config.instance,
            }
        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "component": self.name,
                "error": str(e),
            }

    def _handle_error(self, operation: str, error: Exception) -> dict[str, Any]:
        """Handle errors consistently across components.

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
            "component": self.name,
        }