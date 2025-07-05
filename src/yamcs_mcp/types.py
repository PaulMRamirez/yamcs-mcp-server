"""Shared type definitions and protocols for Yamcs MCP Server."""

from typing import Any, Protocol, runtime_checkable

from yamcs.client import YamcsClient


@runtime_checkable
class YamcsComponent(Protocol):
    """Protocol for all Yamcs MCP components."""

    async def initialize(self, client: YamcsClient, instance: str) -> None:
        """Initialize component with Yamcs client."""
        ...

    async def health_check(self) -> bool:
        """Check component health."""
        ...


class YamcsError(Exception):
    """Base exception for all Yamcs MCP operations."""

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize YamcsError.

        Args:
            message: Error message
            error_code: Optional error code
            context: Optional context information
            cause: Optional underlying exception
        """
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause


class YamcsConnectionError(YamcsError):
    """Raised when connection to Yamcs fails."""

    pass


class YamcsAuthenticationError(YamcsError):
    """Raised when authentication with Yamcs fails."""

    pass


class YamcsNotFoundError(YamcsError):
    """Raised when a requested resource is not found in Yamcs."""

    pass


class YamcsValidationError(YamcsError):
    """Raised when input validation fails."""

    pass


class YamcsOperationError(YamcsError):
    """Raised when a Yamcs operation fails."""

    pass
