"""Yamcs client factory and connection management."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from yamcs.client import YamcsClient

from .config import YamcsConfig
from .types import YamcsAuthenticationError, YamcsConnectionError

logger = structlog.get_logger(__name__)


class YamcsClientManager:
    """Manages Yamcs client lifecycle with proper cleanup."""

    def __init__(self, config: YamcsConfig) -> None:
        """Initialize client manager.

        Args:
            config: Yamcs configuration
        """
        self.config = config
        self._client: YamcsClient | None = None

    @asynccontextmanager
    async def get_client(self) -> AsyncIterator[YamcsClient]:
        """Get a Yamcs client with proper lifecycle management.

        Yields:
            YamcsClient: Connected Yamcs client

        Raises:
            YamcsConnectionError: If connection fails
            YamcsAuthenticationError: If authentication fails
        """
        client = None
        try:
            # Create client
            client = YamcsClient(self.config.url)

            # Set authentication if provided
            if self.config.username and self.config.password:
                try:
                    client.authenticate(
                        username=self.config.username,
                        password=self.config.password.get_secret_value(),
                    )
                except Exception as e:
                    raise YamcsAuthenticationError(
                        "Failed to authenticate with Yamcs",
                        error_code="AUTH_FAILED",
                        context={
                            "url": self.config.url,
                            "username": self.config.username,
                        },
                        cause=e,
                    ) from e

            # Test connection
            try:
                # Try to get server info to verify connection
                client.get_server_info()
            except Exception as e:
                raise YamcsConnectionError(
                    "Failed to connect to Yamcs server",
                    error_code="CONNECTION_FAILED",
                    context={"url": self.config.url},
                    cause=e,
                ) from e

            logger.info(
                "Connected to Yamcs server",
                url=self.config.url,
                instance=self.config.instance,
            )

            yield client

        finally:
            # Cleanup
            if client:
                try:
                    client.close()
                except Exception as e:
                    logger.warning("Error closing Yamcs client", error=str(e))

    async def create_client(self) -> YamcsClient:
        """Create a new Yamcs client.

        Returns:
            YamcsClient: Connected Yamcs client

        Raises:
            YamcsConnectionError: If connection fails
            YamcsAuthenticationError: If authentication fails
        """
        async with self.get_client() as client:
            # Return a new client instance that won't be closed
            new_client = YamcsClient(self.config.url)
            if self.config.username and self.config.password:
                new_client.authenticate(
                    username=self.config.username,
                    password=self.config.password.get_secret_value(),
                )
            return new_client

    async def test_connection(self) -> bool:
        """Test connection to Yamcs server.

        Returns:
            bool: True if connection successful
        """
        try:
            async with self.get_client() as client:
                info = client.get_server_info()
                logger.info(
                    "Yamcs server info",
                    version=info.version,
                    serverId=info.serverId,
                )
                return True
        except (YamcsConnectionError, YamcsAuthenticationError) as e:
            logger.error("Failed to connect to Yamcs", error=str(e))
            return False