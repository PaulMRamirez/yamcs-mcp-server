"""Tests for the Link Management component."""

import pytest
from unittest.mock import Mock, AsyncMock

from yamcs_mcp.components.links import LinkManagementComponent


class TestLinkManagementComponent:
    """Test the Link Management component."""

    @pytest.fixture
    def links_component(self, mock_client_manager, mock_yamcs_config):
        """Create a Link Management component instance."""
        return LinkManagementComponent(mock_client_manager, mock_yamcs_config)

    @pytest.fixture
    def mock_server(self):
        """Create a mock FastMCP server."""
        server = Mock()
        server._tools = {}
        server._resources = {}
        
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

    def test_component_initialization(self, links_component):
        """Test that the component initializes correctly."""
        assert links_component.name == "YamcsLinkManagement"
        assert links_component.client_manager is not None
        assert links_component.config is not None

    def test_register_with_server(self, links_component, mock_server):
        """Test component registration with server."""
        links_component.register_with_server(mock_server)
        
        # Check tools were registered
        expected_tools = [
            "link_list_links",
            "link_get_status",
            "link_enable_link",
            "link_disable_link",
            "link_reset_link",
            "link_get_statistics",
        ]
        
        for tool_name in expected_tools:
            assert tool_name in mock_server._tools
            
        # Check resources were registered
        expected_resources = [
            "link://status",
            "link://statistics",
        ]
        
        for resource_uri in expected_resources:
            assert resource_uri in mock_server._resources

    @pytest.mark.asyncio
    async def test_link_list_links(self, links_component, mock_server, mock_yamcs_client):
        """Test listing links."""
        links_component.register_with_server(mock_server)
        
        # Mock links
        mock_link1 = Mock(
            name="TM_DOWN",
            status="OK",
        )
        mock_link1.type = "TCP"
        mock_link1.disabled = False
        mock_link1.parent_name = None
        mock_link1.data_in_count = 1000
        mock_link1.data_out_count = 950
        
        mock_link2 = Mock(
            name="TC_UP",
            status="FAILED",
        )
        # Missing optional attributes
        
        mock_yamcs_client.list_links.return_value = [mock_link1, mock_link2]
        
        # Get tool function
        list_links_tool = mock_server._tools["link_list_links"].fn
        
        result = await list_links_tool()
        
        assert result["instance"] == "test-instance"
        assert result["count"] == 2
        assert len(result["links"]) == 2
        
        # Check first link with all attributes
        assert result["links"][0]["name"] == "TM_DOWN"
        assert result["links"][0]["type"] == "TCP"
        assert result["links"][0]["status"] == "OK"
        assert result["links"][0]["disabled"] is False
        assert result["links"][0]["data_in_count"] == 1000
        assert result["links"][0]["data_out_count"] == 950
        
        # Check second link with missing attributes
        assert result["links"][1]["name"] == "TC_UP"
        assert result["links"][1]["type"] is None
        assert result["links"][1]["disabled"] is False  # Default value
        assert result["links"][1]["data_in_count"] == 0  # Default value
        assert result["links"][1]["data_out_count"] == 0  # Default value

    @pytest.mark.asyncio
    async def test_link_get_status(self, links_component, mock_server, mock_yamcs_client):
        """Test getting detailed link status."""
        links_component.register_with_server(mock_server)
        
        # Mock link
        mock_link = Mock(
            name="TM_DOWN",
            status="OK",
        )
        mock_link.type = "TCP"
        mock_link.disabled = False
        mock_link.data_in_count = 5000
        mock_link.data_out_count = 4800
        mock_link.last_data_in_time = "2024-01-01T12:00:00Z"
        mock_link.last_data_out_time = "2024-01-01T12:00:01Z"
        mock_link.detail_status = "Connected to ground station"
        
        mock_yamcs_client.get_link.return_value = mock_link
        
        # Get tool function
        get_status_tool = mock_server._tools["link_get_status"].fn
        
        result = await get_status_tool(link="TM_DOWN")
        
        assert result["name"] == "TM_DOWN"
        assert result["type"] == "TCP"
        assert result["status"] == "OK"
        assert result["disabled"] is False
        assert result["statistics"]["data_in_count"] == 5000
        assert result["statistics"]["data_out_count"] == 4800
        assert result["statistics"]["last_data_in"] == "2024-01-01T12:00:00Z"
        assert result["statistics"]["last_data_out"] == "2024-01-01T12:00:01Z"
        assert result["details"] == "Connected to ground station"

    @pytest.mark.asyncio
    async def test_link_operations(self, links_component, mock_server, mock_yamcs_client):
        """Test link enable/disable/reset operations."""
        links_component.register_with_server(mock_server)
        
        # Mock link
        mock_link = Mock()
        mock_link.enable = Mock()
        mock_link.disable = Mock()
        mock_link.reset_counters = Mock()
        mock_yamcs_client.get_link.return_value = mock_link
        
        # Test enable
        enable_tool = mock_server._tools["link_enable_link"].fn
        result = await enable_tool(link="TM_DOWN", instance="simulator")
        
        assert result["success"] is True
        assert result["link"] == "TM_DOWN"
        assert result["operation"] == "enable"
        mock_link.enable.assert_called_once()
        
        # Test disable
        disable_tool = mock_server._tools["link_disable_link"].fn
        result = await disable_tool(link="TM_DOWN")
        
        assert result["success"] is True
        assert result["link"] == "TM_DOWN"
        assert result["operation"] == "disable"
        mock_link.disable.assert_called_once()
        
        # Test reset
        reset_tool = mock_server._tools["link_reset_link"].fn
        result = await reset_tool(link="TM_DOWN")
        
        assert result["success"] is True
        assert result["link"] == "TM_DOWN"
        assert result["operation"] == "reset"
        assert "counters reset" in result["message"]
        mock_link.reset_counters.assert_called_once()

    @pytest.mark.asyncio
    async def test_link_get_statistics(self, links_component, mock_server, mock_yamcs_client):
        """Test getting link statistics."""
        links_component.register_with_server(mock_server)
        
        # Mock links
        mock_links = [
            Mock(
                name="TM_DOWN",
                status="OK",
                disabled=False,
                data_in_count=1000,
                data_out_count=950,
            ),
            Mock(
                name="TC_UP",
                status="OK",
                disabled=False,
                data_in_count=500,
                data_out_count=500,
            ),
            Mock(
                name="BACKUP",
                status="FAILED",
                disabled=True,
                data_in_count=0,
                data_out_count=0,
            ),
        ]
        
        mock_yamcs_client.list_links.return_value = mock_links
        
        # Get tool function
        get_stats_tool = mock_server._tools["link_get_statistics"].fn
        
        result = await get_stats_tool()
        
        stats = result["statistics"]
        assert stats["total_links"] == 3
        assert stats["enabled_links"] == 2
        assert stats["disabled_links"] == 1
        assert stats["ok_links"] == 2
        assert stats["failed_links"] == 1
        assert stats["total_data_in"] == 1500
        assert stats["total_data_out"] == 1450
        assert len(stats["links"]) == 3

    @pytest.mark.asyncio
    async def test_missing_attributes_handling(self, links_component, mock_server, mock_yamcs_client):
        """Test handling of missing attributes in link objects."""
        links_component.register_with_server(mock_server)
        
        # Create link with minimal attributes
        mock_link = Mock(spec=["name", "status"])
        mock_link.name = "MINIMAL_LINK"
        mock_link.status = "UNAVAILABLE"
        
        mock_yamcs_client.list_links.return_value = [mock_link]
        
        # Test list links with missing attributes
        list_links_tool = mock_server._tools["link_list_links"].fn
        result = await list_links_tool()
        
        assert result["count"] == 1
        link = result["links"][0]
        assert link["name"] == "MINIMAL_LINK"
        assert link["type"] is None
        assert link["disabled"] is False
        assert link["parent"] is None
        assert link["data_in_count"] == 0
        assert link["data_out_count"] == 0
        
        # Test get status with missing attributes
        mock_yamcs_client.get_link.return_value = mock_link
        get_status_tool = mock_server._tools["link_get_status"].fn
        result = await get_status_tool(link="MINIMAL_LINK")
        
        assert result["name"] == "MINIMAL_LINK"
        assert result["type"] is None
        assert result["statistics"]["data_in_count"] == 0
        assert result["statistics"]["last_data_in"] is None
        assert result["details"] is None

    @pytest.mark.asyncio
    async def test_resource_handlers(self, links_component, mock_server, mock_yamcs_client):
        """Test resource handlers."""
        links_component.register_with_server(mock_server)
        
        # Mock links for status resource
        mock_links = [
            Mock(
                name="TM_DOWN",
                status="OK",
                type="TCP",
                disabled=False,
                data_in_count=1000,
                data_out_count=950,
            ),
            Mock(
                name="TC_UP",
                status="FAILED",
                disabled=True,
            ),
        ]
        # Set missing attributes on second link
        mock_links[1].type = None
        mock_links[1].data_in_count = None
        mock_links[1].data_out_count = None
        
        mock_yamcs_client.list_links.return_value = mock_links
        
        # Test status resource
        status_resource = mock_server._resources["link://status"].fn
        result = await status_resource()
        
        assert "Links in test-instance (2 total):" in result
        assert "TM_DOWN (TCP): OK [in: 1000, out: 950]" in result
        assert "TC_UP: DISABLED [in: 0, out: 0]" in result
        
        # Test statistics resource
        stats_resource = mock_server._resources["link://statistics"].fn
        result = await stats_resource()
        
        assert "Link Statistics for test-instance:" in result
        assert "Total Links: 2" in result
        assert "Enabled: 1" in result
        assert "Disabled: 1" in result
        assert "OK: 1" in result
        assert "Failed: 1" in result
        assert "Total Data In: 1000" in result
        assert "Total Data Out: 950" in result

    @pytest.mark.asyncio
    async def test_error_handling(self, links_component, mock_server, mock_yamcs_client):
        """Test error handling in link operations."""
        links_component.register_with_server(mock_server)
        
        # Mock an error
        mock_yamcs_client.list_links.side_effect = Exception("Connection timeout")
        
        # Test error in list links
        list_links_tool = mock_server._tools["link_list_links"].fn
        result = await list_links_tool()
        
        assert result["error"] is True
        assert "Connection timeout" in result["message"]
        assert result["operation"] == "link_list_links"
        
        # Test error in enable link
        mock_yamcs_client.get_link.side_effect = Exception("Link not found")
        enable_tool = mock_server._tools["link_enable_link"].fn
        result = await enable_tool(link="NONEXISTENT")
        
        assert result["error"] is True
        assert "Link not found" in result["message"]
        assert result["operation"] == "link_enable_link"

    @pytest.mark.asyncio
    async def test_null_data_counts(self, links_component, mock_server, mock_yamcs_client):
        """Test handling of null data counts."""
        links_component.register_with_server(mock_server)
        
        # Mock link with None values for data counts
        mock_link = Mock(
            name="NULL_COUNTS",
            status="OK",
            disabled=False,
        )
        mock_link.data_in_count = None
        mock_link.data_out_count = None
        
        mock_yamcs_client.list_links.return_value = [mock_link]
        
        # Test get statistics with null counts
        get_stats_tool = mock_server._tools["link_get_statistics"].fn
        result = await get_stats_tool()
        
        stats = result["statistics"]
        # Should handle None values gracefully
        assert stats["total_data_in"] == 0
        assert stats["total_data_out"] == 0