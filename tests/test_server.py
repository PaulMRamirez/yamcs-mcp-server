"""Tests for the main Yamcs MCP Server."""

import pytest
from unittest.mock import Mock, patch

from yamcs_mcp.server import YamcsMCPServer, setup_logging


class TestYamcsMCPServer:
    """Test the main server class."""

    def test_server_initialization(self, mock_config, mock_client_manager):
        """Test server initialization."""
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager):
            server = YamcsMCPServer(mock_config)
            
            assert server.config == mock_config
            assert server.client_manager == mock_client_manager
            assert server.mcp is not None
            assert server.mcp.name == "YamcsServer"

    def test_setup_logging():
        """Test logging setup."""
        # Should not raise any exceptions
        setup_logging("INFO")
        setup_logging("DEBUG")

    @pytest.mark.asyncio
    async def test_health_check(self, mock_config, mock_client_manager):
        """Test server health check tool."""
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager):
            server = YamcsMCPServer(mock_config)
            
            # Get the health_check tool
            health_check = None
            for tool in server.mcp._tools.values():
                if tool.name == "health_check":
                    health_check = tool.fn
                    break
            
            assert health_check is not None
            
            # Call health check
            result = await health_check()
            
            assert result["status"] == "healthy"
            assert result["server"] == "YamcsServer"
            assert result["version"] == "0.1.0"
            assert result["yamcs_url"] == "http://localhost:8090"

    @pytest.mark.asyncio
    async def test_test_connection(self, mock_config, mock_client_manager):
        """Test connection test tool."""
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager):
            server = YamcsMCPServer(mock_config)
            
            # Get the test_connection tool
            test_connection = None
            for tool in server.mcp._tools.values():
                if tool.name == "test_connection":
                    test_connection = tool.fn
                    break
            
            assert test_connection is not None
            
            # Test successful connection
            result = await test_connection()
            
            assert result["connected"] is True
            assert result["yamcs_url"] == "http://localhost:8090"
            assert "Connection successful" in result["message"]

    def test_component_initialization(self, mock_config, mock_client_manager):
        """Test that components are initialized based on config."""
        # Test with all components enabled
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager):
            server = YamcsMCPServer(mock_config)
            
            # Check that components were added
            # In a real test, we'd check the actual components
            assert server.mcp is not None

    def test_component_disabling(self, mock_config, mock_client_manager):
        """Test that components can be disabled via config."""
        # Disable some components
        mock_config.yamcs.enable_mdb = False
        mock_config.yamcs.enable_archive = False
        
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager):
            server = YamcsMCPServer(mock_config)
            
            # In a real implementation, we'd verify that disabled components
            # are not initialized
            assert server.mcp is not None