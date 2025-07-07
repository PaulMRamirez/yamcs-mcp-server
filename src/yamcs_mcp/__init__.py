"""Yamcs MCP Server - Model Context Protocol server for Yamcs."""

from .config import Config, MCPConfig, YamcsConfig
from .server import YamcsMCPServer, main
from .types import (
    YamcsAuthenticationError,
    YamcsConnectionError,
    YamcsError,
    YamcsNotFoundError,
    YamcsOperationError,
    YamcsValidationError,
)

__version__ = "0.2.0-beta"
__all__ = [
    "Config",
    "MCPConfig",
    "YamcsAuthenticationError",
    "YamcsConfig",
    "YamcsConnectionError",
    "YamcsError",
    "YamcsMCPServer",
    "YamcsNotFoundError",
    "YamcsOperationError",
    "YamcsValidationError",
    "main",
]
