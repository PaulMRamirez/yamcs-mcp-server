"""Tests for Yamcs client management."""

from unittest.mock import Mock, patch

import pytest

from yamcs_mcp.client import YamcsClientManager
from yamcs_mcp.types import YamcsAuthenticationError, YamcsConnectionError


class TestYamcsClientManager:
    """Test the Yamcs client manager."""

    @pytest.mark.asyncio
    async def test_get_client_success(self, mock_yamcs_config):
        """Test successful client connection."""
        manager = YamcsClientManager(mock_yamcs_config)

        with patch("yamcs_mcp.client.YamcsClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get_server_info.return_value = Mock(version="5.0.0")
            mock_client.close.return_value = None
            mock_client_class.return_value = mock_client

            async with manager.get_client() as client:
                assert client == mock_client
                mock_client_class.assert_called_once_with("http://localhost:8090")
                mock_client.get_server_info.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_connection_error(self, mock_yamcs_config):
        """Test client connection error."""
        manager = YamcsClientManager(mock_yamcs_config)

        with patch("yamcs_mcp.client.YamcsClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get_server_info.side_effect = Exception("Connection failed")
            mock_client_class.return_value = mock_client

            with pytest.raises(YamcsConnectionError) as exc_info:
                async with manager.get_client():
                    pass

            assert "Failed to connect to Yamcs server" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_client_authentication(self, mock_yamcs_config):
        """Test client with authentication."""
        mock_yamcs_config.username = "testuser"
        mock_yamcs_config.password = Mock(get_secret_value=lambda: "testpass")

        manager = YamcsClientManager(mock_yamcs_config)

        with patch("yamcs_mcp.client.YamcsClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get_server_info.return_value = Mock(version="5.0.0")
            mock_client.authenticate.return_value = None
            mock_client.close.return_value = None
            mock_client_class.return_value = mock_client

            async with manager.get_client() as client:
                assert client == mock_client
                mock_client.authenticate.assert_called_once_with(
                    username="testuser", password="testpass"
                )

    @pytest.mark.asyncio
    async def test_get_client_authentication_error(self, mock_yamcs_config):
        """Test client authentication error."""
        mock_yamcs_config.username = "testuser"
        mock_yamcs_config.password = Mock(get_secret_value=lambda: "wrongpass")

        manager = YamcsClientManager(mock_yamcs_config)

        with patch("yamcs_mcp.client.YamcsClient") as mock_client_class:
            mock_client = Mock()
            mock_client.authenticate.side_effect = Exception("Invalid credentials")
            mock_client_class.return_value = mock_client

            with pytest.raises(YamcsAuthenticationError) as exc_info:
                async with manager.get_client():
                    pass

            assert "Failed to authenticate with Yamcs" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_test_connection_success(self, mock_yamcs_config):
        """Test successful connection test."""
        manager = YamcsClientManager(mock_yamcs_config)

        with patch("yamcs_mcp.client.YamcsClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get_server_info.return_value = Mock(
                version="5.0.0", serverId="test-server"
            )
            mock_client.close.return_value = None
            mock_client_class.return_value = mock_client

            result = await manager.test_connection()

            assert result is True

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, mock_yamcs_config):
        """Test failed connection test."""
        manager = YamcsClientManager(mock_yamcs_config)

        with patch("yamcs_mcp.client.YamcsClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get_server_info.side_effect = Exception("Connection failed")
            mock_client_class.return_value = mock_client

            result = await manager.test_connection()

            assert result is False
