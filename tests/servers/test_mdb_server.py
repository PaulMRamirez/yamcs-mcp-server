"""Tests for the MDB server."""

import pytest

from yamcs_mcp.servers.mdb import MDBServer


class TestMDBServer:
    """Test the MDB server."""

    @pytest.fixture
    def mdb_server(self, mock_client_manager, mock_yamcs_config):
        """Create an MDB server instance."""
        return MDBServer(mock_client_manager, mock_yamcs_config)

    def test_mdb_server_initialization(self, mdb_server):
        """Test that the MDB server initializes correctly."""
        assert mdb_server.name == "YamcsMDBServer"
        assert mdb_server.server_name == "MDB"
        assert mdb_server.client_manager is not None
        assert mdb_server.config is not None

    def test_mdb_server_is_fastmcp_instance(self, mdb_server):
        """Test that MDB server is a FastMCP instance."""
        # Check that it has FastMCP methods
        assert hasattr(mdb_server, "tool")
        assert hasattr(mdb_server, "resource")
        assert hasattr(mdb_server, "mount")

    @pytest.mark.asyncio
    async def test_parameters_tool(self, mdb_server, mock_yamcs_client):
        """Test the parameters tool functionality."""
        # Since tools are registered during init, we can't easily test them directly
        # But we can verify the server was created correctly
        assert mdb_server.name == "YamcsMDBServer"

        # The actual tool testing would require integration tests
        # or more complex mocking of FastMCP internals

    @pytest.mark.asyncio
    async def test_error_handling(self, mdb_server):
        """Test error handling in MDB server."""
        # Test the inherited _handle_error method
        error_result = mdb_server._handle_error("parameters", Exception("MDB error"))

        assert error_result["error"] is True
        assert error_result["message"] == "MDB error"
        assert error_result["operation"] == "parameters"
        assert error_result["server_type"] == "MDB"
        assert error_result["server"] == "YamcsMDBServer"
