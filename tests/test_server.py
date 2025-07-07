"""Tests for the main Yamcs MCP Server."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from yamcs_mcp.server import YamcsMCPServer, setup_logging


class TestYamcsMCPServer:
    """Test the main server class."""

    def test_server_initialization(self, mock_config, mock_client_manager):
        """Test server initialization."""
        with patch(
            "yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager
        ):
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

    def test_server_has_mounted_servers(self, mock_config, mock_client_manager):
        """Test that server mounts sub-servers."""
        with patch(
            "yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager
        ):
            server = YamcsMCPServer(mock_config)

            # Verify that mount was called for each enabled server
            # We can't directly check mounts, but we can verify the server was created
            assert server.mcp is not None
            assert hasattr(server.mcp, "mount")

    def test_server_registration(self, mock_config, mock_client_manager):
        """Test that sub-servers are mounted with the main server."""
        # Mock FastMCP and all server classes
        with (
            patch(
                "yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager
            ),
            patch("yamcs_mcp.server.FastMCP") as mock_fastmcp_class,
            patch("yamcs_mcp.server.MDBServer") as mock_mdb_class,
            patch("yamcs_mcp.server.ProcessorsServer") as mock_processor_class,
            patch("yamcs_mcp.server.LinksServer") as mock_link_class,
            patch("yamcs_mcp.server.StorageServer") as mock_storage_class,
            patch("yamcs_mcp.server.InstancesServer") as mock_instance_class,
            patch("yamcs_mcp.server.AlarmsServer") as mock_alarms_class,
        ):
            # Create mock FastMCP instance
            mock_fastmcp = Mock()
            mock_fastmcp_class.return_value = mock_fastmcp

            # Create mock server instances
            mock_mdb = Mock()
            mock_processor = Mock()
            mock_link = Mock()
            mock_storage = Mock()
            mock_instance = Mock()
            mock_alarms = Mock()

            # Set return values
            mock_mdb_class.return_value = mock_mdb
            mock_processor_class.return_value = mock_processor
            mock_link_class.return_value = mock_link
            mock_storage_class.return_value = mock_storage
            mock_instance_class.return_value = mock_instance
            mock_alarms_class.return_value = mock_alarms

            # Create server
            YamcsMCPServer(mock_config)

            # Verify servers were created
            mock_mdb_class.assert_called_once_with(
                mock_client_manager, mock_config.yamcs
            )
            mock_processor_class.assert_called_once_with(
                mock_client_manager, mock_config.yamcs
            )
            mock_link_class.assert_called_once_with(
                mock_client_manager, mock_config.yamcs
            )
            mock_storage_class.assert_called_once_with(
                mock_client_manager, mock_config.yamcs
            )
            mock_instance_class.assert_called_once_with(
                mock_client_manager, mock_config.yamcs
            )
            mock_alarms_class.assert_called_once_with(
                mock_client_manager, mock_config.yamcs
            )

            # Verify mount was called on main server with each sub-server
            assert mock_fastmcp.mount.call_count == 6
            mock_fastmcp.mount.assert_any_call(mock_mdb, prefix="mdb")
            mock_fastmcp.mount.assert_any_call(mock_processor, prefix="processors")
            mock_fastmcp.mount.assert_any_call(mock_link, prefix="links")
            mock_fastmcp.mount.assert_any_call(mock_storage, prefix="storage")
            mock_fastmcp.mount.assert_any_call(mock_instance, prefix="instances")
            mock_fastmcp.mount.assert_any_call(mock_alarms, prefix="alarms")

    def test_server_disabling(self, mock_config, mock_client_manager):
        """Test that servers can be disabled via config."""
        # Disable some servers
        mock_config.yamcs.enable_mdb = False

        with (
            patch(
                "yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager
            ),
            patch("yamcs_mcp.server.MDBServer") as mock_mdb_class,
            patch("yamcs_mcp.server.ProcessorsServer") as mock_processor_class,
            patch("yamcs_mcp.server.LinksServer") as mock_link_class,
            patch("yamcs_mcp.server.StorageServer") as mock_storage_class,
            patch("yamcs_mcp.server.InstancesServer") as mock_instance_class,
            patch("yamcs_mcp.server.AlarmsServer") as mock_alarms_class,
        ):
            YamcsMCPServer(mock_config)

            # Verify disabled servers were not created
            mock_mdb_class.assert_not_called()

            # Verify enabled servers were created
            mock_processor_class.assert_called_once()
            mock_link_class.assert_called_once()
            mock_storage_class.assert_called_once()
            mock_instance_class.assert_called_once()
            mock_alarms_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_method(self, mock_config, mock_client_manager):
        """Test the run method."""
        with patch(
            "yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager
        ):
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

        with patch(
            "yamcs_mcp.server.YamcsClientManager", return_value=mock_client_manager
        ):
            server = YamcsMCPServer(mock_config)
            server.mcp.run_async = AsyncMock()

            # Should continue in demo mode
            await server.run()

            # Verify it still runs despite connection failure
            server.mcp.run_async.assert_called_once()

    def test_main_function(self):
        """Test the main entry point."""
        with (
            patch("yamcs_mcp.server.Config") as mock_config_class,
            patch("yamcs_mcp.server.YamcsMCPServer") as mock_server_class,
            patch("yamcs_mcp.server.asyncio") as mock_asyncio,
        ):
            # Mock config
            mock_config = Mock()
            mock_config_class.from_env.return_value = mock_config

            # Mock server
            mock_server = Mock()
            mock_server_class.return_value = mock_server

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
            mock_config_class.from_env.assert_called_once()
            mock_server_class.assert_called_once_with(mock_config)
            mock_asyncio.run.assert_called_once()
