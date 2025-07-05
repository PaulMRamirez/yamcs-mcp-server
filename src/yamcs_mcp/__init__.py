"""Yamcs MCP Server - Model Context Protocol server for Yamcs."""

from .server import YamcsMCPServer, main
from .config import Config, YamcsConfig, MCPConfig
from .types import (
    YamcsError,
    YamcsConnectionError,
    YamcsAuthenticationError,
    YamcsNotFoundError,
    YamcsValidationError,
    YamcsOperationError,
)

__version__ = "0.1.0"
__all__ = [
    "YamcsMCPServer",
    "main",
    "Config",
    "YamcsConfig",
    "MCPConfig",
    "YamcsError",
    "YamcsConnectionError",
    "YamcsAuthenticationError",
    "YamcsNotFoundError",
    "YamcsValidationError",
    "YamcsOperationError",
]