"""Tests for the MDB component."""

import pytest
from unittest.mock import Mock, AsyncMock

from yamcs_mcp.components.mdb import MDBComponent


class TestMDBComponent:
    """Test the MDB component."""

    @pytest.fixture
    def mdb_component(self, mock_client_manager, mock_yamcs_config):
        """Create an MDB component instance."""
        return MDBComponent(mock_client_manager, mock_yamcs_config)

    def test_component_initialization(self, mdb_component):
        """Test that the component initializes correctly."""
        assert mdb_component.name == "YamcsMDB"
        assert mdb_component.client_manager is not None
        assert mdb_component.config is not None

    def test_tools_registered(self, mdb_component):
        """Test that all expected tools are registered."""
        # Get tool names
        tool_names = [tool.name for tool in mdb_component._tools.values()]
        
        expected_tools = [
            "mdb_list_parameters",
            "mdb_get_parameter",
            "mdb_list_commands",
            "mdb_get_command",
            "mdb_list_space_systems",
        ]
        
        for expected in expected_tools:
            assert expected in tool_names

    def test_resources_registered(self, mdb_component):
        """Test that all expected resources are registered."""
        # Get resource URIs
        resource_uris = list(mdb_component._resources.keys())
        
        expected_resources = [
            "mdb://parameters",
            "mdb://commands",
        ]
        
        for expected in expected_resources:
            assert expected in resource_uris

    @pytest.mark.asyncio
    async def test_mdb_list_parameters(self, mdb_component, mock_yamcs_client):
        """Test listing parameters."""
        # Mock the MDB client
        mock_mdb = Mock()
        mock_param1 = Mock(
            name="param1",
            qualified_name="/system/param1",
            type=Mock(eng_type="float"),
            units="V",
            description="Test parameter 1",
        )
        mock_param2 = Mock(
            name="param2",
            qualified_name="/system/param2",
            type=Mock(eng_type="integer"),
            units="A",
            description="Test parameter 2",
        )
        mock_mdb.list_parameters.return_value = [mock_param1, mock_param2]
        mock_yamcs_client.get_mdb.return_value = mock_mdb
        
        # Get the tool function
        list_params_tool = None
        for tool in mdb_component._tools.values():
            if tool.name == "mdb_list_parameters":
                list_params_tool = tool.fn
                break
        
        assert list_params_tool is not None
        
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
    async def test_mdb_list_parameters_with_filters(self, mdb_component, mock_yamcs_client):
        """Test listing parameters with filters."""
        # Mock the MDB client
        mock_mdb = Mock()
        mock_params = [
            Mock(
                name="voltage",
                qualified_name="/power/voltage",
                type=Mock(eng_type="float"),
                units="V",
                description="Voltage parameter",
            ),
            Mock(
                name="current",
                qualified_name="/power/current",
                type=Mock(eng_type="float"),
                units="A",
                description="Current parameter",
            ),
            Mock(
                name="temp",
                qualified_name="/thermal/temp",
                type=Mock(eng_type="float"),
                units="C",
                description="Temperature parameter",
            ),
        ]
        mock_mdb.list_parameters.return_value = mock_params
        mock_yamcs_client.get_mdb.return_value = mock_mdb
        
        # Get the tool function
        list_params_tool = None
        for tool in mdb_component._tools.values():
            if tool.name == "mdb_list_parameters":
                list_params_tool = tool.fn
                break
        
        # Test system filter
        result = await list_params_tool(system="/power")
        assert result["count"] == 2
        assert all(p["qualified_name"].startswith("/power") for p in result["parameters"])
        
        # Test search filter
        result = await list_params_tool(search="volt")
        assert result["count"] == 1
        assert result["parameters"][0]["name"] == "voltage"

    @pytest.mark.asyncio
    async def test_mdb_get_parameter(self, mdb_component, mock_yamcs_client):
        """Test getting a specific parameter."""
        # Mock the MDB client
        mock_mdb = Mock()
        mock_param = Mock(
            name="voltage",
            qualified_name="/power/voltage",
            type=Mock(eng_type="float", encoding="IEEE754_32"),
            units="V",
            description="Battery voltage",
            data_source="TELEMETERED",
            alias=[
                Mock(name="BATT_V", namespace="MIL-STD-1553"),
            ],
        )
        mock_mdb.get_parameter.return_value = mock_param
        mock_yamcs_client.get_mdb.return_value = mock_mdb
        
        # Get the tool function
        get_param_tool = None
        for tool in mdb_component._tools.values():
            if tool.name == "mdb_get_parameter":
                get_param_tool = tool.fn
                break
        
        result = await get_param_tool(parameter="/power/voltage")
        
        assert result["name"] == "voltage"
        assert result["qualified_name"] == "/power/voltage"
        assert result["type"]["eng_type"] == "float"
        assert result["type"]["encoding"] == "IEEE754_32"
        assert result["units"] == "V"
        assert result["data_source"] == "TELEMETERED"
        assert len(result["alias"]) == 1
        assert result["alias"][0]["name"] == "BATT_V"

    @pytest.mark.asyncio
    async def test_error_handling(self, mdb_component, mock_yamcs_client):
        """Test error handling in tools."""
        # Mock an error
        mock_yamcs_client.get_mdb.side_effect = Exception("Connection lost")
        
        # Get the tool function
        list_params_tool = None
        for tool in mdb_component._tools.values():
            if tool.name == "mdb_list_parameters":
                list_params_tool = tool.fn
                break
        
        result = await list_params_tool()
        
        assert result["error"] is True
        assert "Connection lost" in result["message"]
        assert result["operation"] == "mdb_list_parameters"
        assert result["component"] == "YamcsMDB"