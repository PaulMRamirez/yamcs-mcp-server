"""Configuration management for Yamcs MCP Server."""

from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class YamcsConfig(BaseSettings):
    """Yamcs connection configuration."""

    model_config = SettingsConfigDict(
        env_prefix="YAMCS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Connection settings
    url: str = Field(default="http://localhost:8090", description="Yamcs server URL")
    instance: str = Field(default="simulator", description="Default Yamcs instance")

    # Authentication (optional)
    username: str | None = None
    password: SecretStr | None = None

    # Client settings
    timeout: float = Field(default=30.0, ge=1.0, le=300.0)
    max_retries: int = Field(default=3, ge=0, le=10)

    # Server toggles
    enable_mdb: bool = True
    enable_processor: bool = True
    enable_archive: bool = True
    enable_links: bool = True
    enable_storage: bool = True
    enable_instances: bool = True

    # Server settings
    server_name: str = "YamcsServer"
    log_level: str = Field(default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")


class MCPConfig(BaseSettings):
    """MCP server configuration."""

    model_config = SettingsConfigDict(env_prefix="MCP_")

    transport: Literal["stdio", "http", "sse"] = Field(
        default="stdio",
        description="MCP transport type"
    )
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1024, le=65535)


class Config(BaseSettings):
    """Combined configuration for the Yamcs MCP Server."""

    yamcs: YamcsConfig = Field(default_factory=YamcsConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            yamcs=YamcsConfig(),
            mcp=MCPConfig(),
        )
