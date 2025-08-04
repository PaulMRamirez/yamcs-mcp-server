"""Tests for the Commands server."""

import pytest

from yamcs_mcp.servers.commands import CommandsServer


class TestCommandsServer:
    """Test the Commands server."""

    @pytest.fixture
    def commands_server(self, mock_client_manager, mock_yamcs_config):
        """Create a Commands server instance."""
        return CommandsServer(mock_client_manager, mock_yamcs_config)

    def test_commands_server_initialization(self, commands_server):
        """Test that the Commands server initializes correctly."""
        assert commands_server.name == "YamcsCommandsServer"
        assert commands_server.server_name == "Commands"
        assert commands_server.client_manager is not None
        assert commands_server.config is not None

    def test_commands_server_is_fastmcp_instance(self, commands_server):
        """Test that Commands server is a FastMCP instance."""
        # Check that it has FastMCP methods
        assert hasattr(commands_server, "tool")
        assert hasattr(commands_server, "resource")
        assert hasattr(commands_server, "mount")

    @pytest.mark.asyncio
    async def test_error_handling(self, commands_server):
        """Test error handling in Commands server."""
        # Test the inherited _handle_error method
        error_result = commands_server._handle_error(
            "run_command", Exception("Command execution failed")
        )

        assert error_result["error"] is True
        assert error_result["message"] == "Command execution failed"
        assert error_result["operation"] == "run_command"
        assert error_result["server_type"] == "Commands"
        assert error_result["server"] == "YamcsCommandsServer"

    def test_parse_time_special_values(self, commands_server):
        """Test time parsing with special values."""
        # Test special time values
        now = commands_server._parse_time("now")
        assert now is not None
        
        today = commands_server._parse_time("today")
        assert today is not None
        assert today.hour == 0
        assert today.minute == 0
        assert today.second == 0
        
        yesterday = commands_server._parse_time("yesterday")
        assert yesterday is not None
        assert yesterday.hour == 0
        
        # Test ISO format
        iso_time = commands_server._parse_time("2024-01-15T12:00:00Z")
        assert iso_time is not None
        assert iso_time.year == 2024
        assert iso_time.month == 1
        assert iso_time.day == 15
        
        # Test invalid format returns None
        invalid = commands_server._parse_time("invalid_date")
        assert invalid is None