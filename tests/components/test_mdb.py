"""Tests for the MDB component."""

from unittest.mock import Mock

import pytest

from yamcs_mcp.components.mdb import MDBComponent


class TestMDBComponent:
    """Test the MDB component."""

    @pytest.fixture
    def mdb_component(self, mock_client_manager, mock_yamcs_config):
        """Create an MDB component instance."""
        return MDBComponent(mock_client_manager, mock_yamcs_config)

    @pytest.fixture
    def mock_server(self):
        """Create a mock FastMCP server."""
        server = Mock()
        server._tools = {}
        server._resources = {}

        # Mock the decorators
        def tool_decorator():
            def decorator(func):
                server._tools[func.__name__] = Mock(name=func.__name__, fn=func)
                return func
            return decorator

        def resource_decorator(uri):
            def decorator(func):
                server._resources[uri] = Mock(uri=uri, fn=func)
                return func
            return decorator

        server.tool = tool_decorator
        server.resource = resource_decorator
        return server

    def test_component_initialization(self, mdb_component):
        """Test that the component initializes correctly."""
        assert mdb_component.name == "YamcsMDB"
        assert mdb_component.client_manager is not None
        assert mdb_component.config is not None

    def test_register_with_server(self, mdb_component, mock_server):
        """Test component registration with server."""
        mdb_component.register_with_server(mock_server)

        # Check tools were registered
        expected_tools = [
            "mdb_list_parameters",
            "mdb_get_parameter",
            "mdb_list_commands",
            "mdb_get_command",
            "mdb_list_space_systems",
        ]

        for tool_name in expected_tools:
            assert tool_name in mock_server._tools

        # Check resources were registered
        expected_resources = [
            "mdb://parameters",
            "mdb://commands",
        ]

        for resource_uri in expected_resources:
            assert resource_uri in mock_server._resources

    @pytest.mark.asyncio
    async def test_mdb_list_parameters(self, mdb_component, mock_server, mock_yamcs_client):
        """Test listing parameters."""
        # Register component
        mdb_component.register_with_server(mock_server)

        # Mock the MDB client
        mock_mdb = Mock()
        mock_param1 = Mock(
            name="param1",
            qualified_name="/system/param1",
            type="float",  # Note: type is now a string, not an object
            units="V",
            description="Test parameter 1",
        )
        mock_param2 = Mock(
            name="param2",
            qualified_name="/system/param2",
            type="integer",
            units="A",
            description="Test parameter 2",
        )
        mock_mdb.list_parameters.return_value = [mock_param1, mock_param2]
        mock_yamcs_client.get_mdb.return_value = mock_mdb

        # Get the tool function
        list_params_tool = mock_server._tools["mdb_list_parameters"].fn

        # Call the tool
        result = await list_params_tool()

        # Verify results
        assert result["instance"] == "test-instance"
        assert result["count"] == 2
        assert len(result["parameters"]) == 2
        assert result["parameters"][0]["name"] == "param1"
        assert result["parameters"][0]["type"] == "float"
        assert result["parameters"][1]["name"] == "param2"
        assert result["parameters"][1]["type"] == "integer"

    @pytest.mark.asyncio
    async def test_mdb_list_parameters_with_filters(self, mdb_component, mock_server, mock_yamcs_client):
        """Test listing parameters with filters."""
        # Register component
        mdb_component.register_with_server(mock_server)

        # Mock the MDB client
        mock_mdb = Mock()
        mock_params = [
            Mock(
                name="voltage",
                qualified_name="/power/voltage",
                type="float",
                units="V",
                description="Voltage parameter",
            ),
            Mock(
                name="current",
                qualified_name="/power/current",
                type="float",
                units="A",
                description="Current parameter",
            ),
            Mock(
                name="temp",
                qualified_name="/thermal/temp",
                type="float",
                units="C",
                description="Temperature parameter",
            ),
        ]
        mock_mdb.list_parameters.return_value = mock_params
        mock_yamcs_client.get_mdb.return_value = mock_mdb

        # Get the tool function
        list_params_tool = mock_server._tools["mdb_list_parameters"].fn

        # Test system filter
        result = await list_params_tool(system="/power")
        assert result["count"] == 2
        assert all(p["qualified_name"].startswith("/power") for p in result["parameters"])

        # Test search filter
        result = await list_params_tool(search="volt")
        assert result["count"] == 1
        assert result["parameters"][0]["name"] == "voltage"

    @pytest.mark.asyncio
    async def test_mdb_get_parameter(self, mdb_component, mock_server, mock_yamcs_client):
        """Test getting a specific parameter."""
        # Register component
        mdb_component.register_with_server(mock_server)

        # Mock the MDB client
        mock_mdb = Mock()
        mock_param = Mock(
            name="voltage",
            qualified_name="/power/voltage",
            type="float",
            units="V",
            description="Battery voltage",
            data_source="TELEMETERED",
            aliases_dict={
                "MIL-STD-1553": Mock(name="BATT_V", namespace="MIL-STD-1553"),
            },
        )
        mock_mdb.get_parameter.return_value = mock_param
        mock_yamcs_client.get_mdb.return_value = mock_mdb

        # Get the tool function
        get_param_tool = mock_server._tools["mdb_get_parameter"].fn

        result = await get_param_tool(parameter="/power/voltage")

        assert result["name"] == "voltage"
        assert result["qualified_name"] == "/power/voltage"
        assert result["type"] == "float"
        assert result["units"] == "V"
        assert result["data_source"] == "TELEMETERED"
        assert len(result["aliases"]) == 1
        assert result["aliases"][0]["name"] == "BATT_V"

    @pytest.mark.asyncio
    async def test_error_handling(self, mdb_component, mock_server, mock_yamcs_client):
        """Test error handling in tools."""
        # Register component
        mdb_component.register_with_server(mock_server)

        # Mock an error
        mock_yamcs_client.get_mdb.side_effect = Exception("Connection lost")

        # Get the tool function
        list_params_tool = mock_server._tools["mdb_list_parameters"].fn

        result = await list_params_tool()

        assert result["error"] is True
        assert "Connection lost" in result["message"]
        assert result["operation"] == "mdb_list_parameters"
        assert result["component"] == "YamcsMDB"

    @pytest.mark.asyncio
    async def test_resource_handlers(self, mdb_component, mock_server, mock_yamcs_client):
        """Test resource handlers."""
        # Register component
        mdb_component.register_with_server(mock_server)

        # Mock the MDB client for parameters resource
        mock_mdb = Mock()
        mock_params = [
            Mock(
                name=f"param{i}",
                qualified_name=f"/system/param{i}",
                type="float",
                units="V",
                description=f"Test parameter {i}",
            )
            for i in range(60)  # More than 50 to test truncation
        ]
        mock_mdb.list_parameters.return_value = mock_params
        mock_yamcs_client.get_mdb.return_value = mock_mdb

        # Test parameters resource
        params_resource = mock_server._resources["mdb://parameters"].fn
        result = await params_resource()

        assert "Parameters in test-instance (60 total):" in result
        assert "/system/param0 (float)" in result
        assert "... and 10 more" in result  # Should show first 50 and mention 10 more

        # Test commands resource
        mock_commands = [
            Mock(
                name=f"cmd{i}",
                qualified_name=f"/system/cmd{i}",
                description=f"Test command {i}",
                abstract=False,
            )
            for i in range(30)
        ]
        mock_mdb.list_commands.return_value = mock_commands

        commands_resource = mock_server._resources["mdb://commands"].fn
        result = await commands_resource()

        assert "Commands in test-instance (30 total):" in result
        assert "/system/cmd0" in result

    @pytest.mark.asyncio
    async def test_missing_attributes_handling(self, mdb_component, mock_server, mock_yamcs_client):
        """Test handling of missing attributes in parameter objects."""
        # Register component
        mdb_component.register_with_server(mock_server)

        # Mock parameter with missing attributes
        mock_mdb = Mock()
        mock_param = Mock(spec=[])  # Empty spec means no attributes
        mock_param.name = "test_param"
        mock_param.qualified_name = "/test/param"
        mock_param.type = "float"
        # Don't set units, description, or aliases_dict to test missing attributes

        mock_mdb.get_parameter.return_value = mock_param
        mock_yamcs_client.get_mdb.return_value = mock_mdb

        # Get the tool function
        get_param_tool = mock_server._tools["mdb_get_parameter"].fn

        result = await get_param_tool(parameter="/test/param")

        # Should handle missing attributes gracefully
        assert result["name"] == "test_param"
        assert result["units"] is None
        assert result["description"] is None
        assert result["aliases"] == []
