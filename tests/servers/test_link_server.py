"""Tests for the Link server."""

from unittest.mock import Mock

import pytest

from yamcs_mcp.servers.links import LinkServer


class TestLinkServer:
    """Test the Link server."""

    @pytest.fixture
    def link_server(self, mock_client_manager, mock_yamcs_config):
        """Create a Link server instance."""
        return LinkServer(mock_client_manager, mock_yamcs_config)

    def test_link_server_initialization(self, link_server):
        """Test that the Link server initializes correctly."""
        assert link_server.name == "YamcsLinksServer"
        assert link_server.component_name == "Links"
        assert link_server.client_manager is not None
        assert link_server.config is not None

    def test_link_server_is_fastmcp_instance(self, link_server):
        """Test that Link server is a FastMCP instance."""
        # Check that it has FastMCP methods
        assert hasattr(link_server, 'tool')
        assert hasattr(link_server, 'resource')
        assert hasattr(link_server, 'mount')

    @pytest.mark.asyncio
    async def test_error_handling(self, link_server):
        """Test error handling in Link server."""
        # Test the inherited _handle_error method
        error_result = link_server._handle_error("list", Exception("Link error"))
        
        assert error_result["error"] is True
        assert error_result["message"] == "Link error"
        assert error_result["operation"] == "list"
        assert error_result["component"] == "Links"
        assert error_result["server"] == "YamcsLinksServer"