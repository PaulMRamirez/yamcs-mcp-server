"""Tests for the base server class."""

from unittest.mock import Mock

import pytest

from yamcs_mcp.servers.base_server import BaseYamcsServer


class TestBaseYamcsServer:
    """Test the base server functionality."""

    @pytest.fixture
    def test_server(self, mock_client_manager, mock_yamcs_config):
        """Create a test implementation of BaseYamcsServer."""
        
        class TestServer(BaseYamcsServer):
            """Test implementation."""
            pass
        
        return TestServer("Test", mock_client_manager, mock_yamcs_config)

    def test_base_server_initialization(self, test_server, mock_client_manager, mock_yamcs_config):
        """Test base server initialization."""
        assert test_server.name == "YamcsTestServer"
        assert test_server.component_name == "Test"
        assert test_server.client_manager == mock_client_manager
        assert test_server.config == mock_yamcs_config
        assert test_server.logger is not None

    def test_handle_error(self, test_server):
        """Test error handling method."""
        error = Exception("Something went wrong")
        result = test_server._handle_error("test_operation", error)
        
        assert result["error"] is True
        assert result["message"] == "Something went wrong"
        assert result["operation"] == "test_operation"
        assert result["component"] == "Test"
        assert result["server"] == "YamcsTestServer"