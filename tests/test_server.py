"""Tests for the main Yamcs MCP Server."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

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

    def test_setup_logging(self):
        """Test logging setup."""
        # Should not raise any exceptions
        setup_logging("INFO")
        setup_logging("DEBUG")

    @pytest.mark.asyncio
    async def test_health_check(self, mock_config, mock_client_manager):
        """Test server health check tool."""
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager):
            server = YamcsMCPServer(mock_config)
            
            # Get the health_check tool by calling it directly
            # In the new pattern, tools are registered during init
            result = await server.health_check()
            
            assert result["status"] == "healthy"
            assert result["server"] == "YamcsServer"
            assert result["version"] == "0.0.1-beta"
            assert result["yamcs_url"] == "http://localhost:8090"

    @pytest.mark.asyncio
    async def test_test_connection(self, mock_config, mock_client_manager):
        """Test connection test tool."""
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager):
            server = YamcsMCPServer(mock_config)
            
            # Test successful connection
            result = await server.test_connection()
            
            assert result["connected"] is True
            assert result["yamcs_url"] == "http://localhost:8090"
            assert "Connection successful" in result["message"]

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, mock_config, mock_client_manager):
        """Test connection test with failure."""
        mock_client_manager.test_connection = AsyncMock(return_value=False)
        
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager):
            server = YamcsMCPServer(mock_config)
            
            # Test failed connection
            result = await server.test_connection()
            
            assert result["connected"] is False
            assert result["yamcs_url"] == "http://localhost:8090"
            assert "Connection failed" in result["message"]

    @pytest.mark.asyncio
    async def test_test_connection_exception(self, mock_config, mock_client_manager):
        """Test connection test with exception."""
        mock_client_manager.test_connection = AsyncMock(side_effect=Exception("Network error"))
        
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager):
            server = YamcsMCPServer(mock_config)
            
            # Test exception handling
            result = await server.test_connection()
            
            assert result["connected"] is False
            assert result["yamcs_url"] == "http://localhost:8090"
            assert "Network error" in result["error"]

    def test_component_registration(self, mock_config, mock_client_manager):
        """Test that components are registered with the server."""
        # Mock all component classes
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager), \
             patch("yamcs_mcp.server.MDBComponent") as MockMDB, \
             patch("yamcs_mcp.server.ProcessorComponent") as MockProcessor, \
             patch("yamcs_mcp.server.ArchiveComponent") as MockArchive, \
             patch("yamcs_mcp.server.LinkManagementComponent") as MockLink, \
             patch("yamcs_mcp.server.ObjectStorageComponent") as MockStorage, \
             patch("yamcs_mcp.server.InstanceManagementComponent") as MockInstance:
            
            # Create mock component instances
            mock_mdb = Mock()
            mock_processor = Mock()
            mock_archive = Mock()
            mock_link = Mock()
            mock_storage = Mock()
            mock_instance = Mock()
            
            # Set return values
            MockMDB.return_value = mock_mdb
            MockProcessor.return_value = mock_processor
            MockArchive.return_value = mock_archive
            MockLink.return_value = mock_link
            MockStorage.return_value = mock_storage
            MockInstance.return_value = mock_instance
            
            # Create server
            server = YamcsMCPServer(mock_config)
            
            # Verify components were created
            MockMDB.assert_called_once_with(mock_client_manager, mock_config.yamcs)
            MockProcessor.assert_called_once_with(mock_client_manager, mock_config.yamcs)
            MockArchive.assert_called_once_with(mock_client_manager, mock_config.yamcs)
            MockLink.assert_called_once_with(mock_client_manager, mock_config.yamcs)
            MockStorage.assert_called_once_with(mock_client_manager, mock_config.yamcs)
            MockInstance.assert_called_once_with(mock_client_manager, mock_config.yamcs)
            
            # Verify register_with_server was called on each component
            mock_mdb.register_with_server.assert_called_once_with(server.mcp)
            mock_processor.register_with_server.assert_called_once_with(server.mcp)
            mock_archive.register_with_server.assert_called_once_with(server.mcp)
            mock_link.register_with_server.assert_called_once_with(server.mcp)
            mock_storage.register_with_server.assert_called_once_with(server.mcp)
            mock_instance.register_with_server.assert_called_once_with(server.mcp)

    def test_component_disabling(self, mock_config, mock_client_manager):
        """Test that components can be disabled via config."""
        # Disable some components
        mock_config.yamcs.enable_mdb = False
        mock_config.yamcs.enable_archive = False
        
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager), \
             patch("yamcs_mcp.server.MDBComponent") as MockMDB, \
             patch("yamcs_mcp.server.ProcessorComponent") as MockProcessor, \
             patch("yamcs_mcp.server.ArchiveComponent") as MockArchive, \
             patch("yamcs_mcp.server.LinkManagementComponent") as MockLink, \
             patch("yamcs_mcp.server.ObjectStorageComponent") as MockStorage, \
             patch("yamcs_mcp.server.InstanceManagementComponent") as MockInstance:
            
            server = YamcsMCPServer(mock_config)
            
            # Verify disabled components were not created
            MockMDB.assert_not_called()
            MockArchive.assert_not_called()
            
            # Verify enabled components were created
            MockProcessor.assert_called_once()
            MockLink.assert_called_once()
            MockStorage.assert_called_once()
            MockInstance.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_method(self, mock_config, mock_client_manager):
        """Test the run method."""
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager):
            server = YamcsMCPServer(mock_config)
            
            # Mock the mcp.run_async method
            server.mcp.run_async = AsyncMock()
            
            # Test stdio transport
            await server.run()
            
            server.mcp.run_async.assert_called_once_with()
            
            # Test HTTP transport
            mock_config.mcp.transport = "http"
            server.mcp.run_async.reset_mock()
            
            await server.run()
            
            server.mcp.run_async.assert_called_once_with(
                transport="http",
                host="127.0.0.1",
                port=8000,
            )

    @pytest.mark.asyncio
    async def test_run_with_connection_failure(self, mock_config, mock_client_manager):
        """Test run method when Yamcs connection fails."""
        mock_client_manager.test_connection = AsyncMock(return_value=False)
        
        with patch("yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager):
            server = YamcsMCPServer(mock_config)
            server.mcp.run_async = AsyncMock()
            
            # Should continue in demo mode
            await server.run()
            
            # Verify it still runs despite connection failure
            server.mcp.run_async.assert_called_once()

    def test_main_function(self):
        """Test the main entry point."""
        with patch("yamcs_mcp.server.Config") as MockConfig, \
             patch("yamcs_mcp.server.YamcsMCPServer") as MockServer, \
             patch("yamcs_mcp.server.asyncio") as mock_asyncio:
            
            # Mock config
            mock_config = Mock()
            MockConfig.from_env.return_value = mock_config
            
            # Mock server
            mock_server = Mock()
            MockServer.return_value = mock_server
            
            # Mock asyncio - simulate no running loop
            mock_asyncio.get_running_loop.side_effect = RuntimeError("No running loop")
            
            # Import and call main
            from yamcs_mcp.server import main
            
            # Should not raise exception
            try:
                main()
            except SystemExit:
                pass  # Expected for normal exit
            
            # Verify server was created and run
            MockConfig.from_env.assert_called_once()
            MockServer.assert_called_once_with(mock_config)
            mock_asyncio.run.assert_called_once()