"""Tests for the Instance Management component."""

import pytest
from unittest.mock import Mock, AsyncMock

from yamcs_mcp.components.instances import InstanceManagementComponent


class TestInstanceManagementComponent:
    """Test the Instance Management component."""

    @pytest.fixture
    def instances_component(self, mock_client_manager, mock_yamcs_config):
        """Create an Instance Management component instance."""
        return InstanceManagementComponent(mock_client_manager, mock_yamcs_config)

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

    def test_component_initialization(self, instances_component):
        """Test that the component initializes correctly."""
        assert instances_component.name == "YamcsInstanceManagement"
        assert instances_component.client_manager is not None
        assert instances_component.config is not None

    def test_register_with_server(self, instances_component, mock_server):
        """Test component registration with server."""
        instances_component.register_with_server(mock_server)
        
        # Check tools were registered
        expected_tools = [
            "instance_list_instances",
            "instance_get_info",
            "instance_start_instance",
            "instance_stop_instance",
            "instance_list_services",
            "instance_start_service",
            "instance_stop_service",
        ]
        
        for tool_name in expected_tools:
            assert tool_name in mock_server._tools
            
        # Check resources were registered
        expected_resources = [
            "instance://list",
            "instance://services/{instance}",
        ]
        
        for resource_uri in expected_resources:
            assert resource_uri in mock_server._resources

    @pytest.mark.asyncio
    async def test_instance_list_instances(self, instances_component, mock_server, mock_yamcs_client):
        """Test listing instances."""
        instances_component.register_with_server(mock_server)
        
        # Mock instances
        mock_inst1 = Mock(
            name="simulator",
            state="RUNNING",
            mission_time="2024-01-01T12:00:00Z",
        )
        # Add attributes to avoid AttributeError
        mock_inst1.labels = {"env": "dev"}
        mock_inst1.template = "standard"
        mock_inst1.capabilities = ["tm", "tc", "archive"]
        
        mock_inst2 = Mock(
            name="ops",
            state="OFFLINE",
            mission_time="2024-01-01T10:00:00Z",
        )
        # Missing optional attributes
        mock_inst2.labels = None
        mock_inst2.template = None
        mock_inst2.capabilities = []
        
        mock_yamcs_client.list_instances.return_value = [mock_inst1, mock_inst2]
        
        # Get tool function
        list_instances_tool = mock_server._tools["instance_list_instances"].fn
        
        result = await list_instances_tool()
        
        assert result["count"] == 2
        assert len(result["instances"]) == 2
        assert result["instances"][0]["name"] == "simulator"
        assert result["instances"][0]["state"] == "RUNNING"
        assert result["instances"][0]["labels"] == {"env": "dev"}
        assert result["instances"][0]["template"] == "standard"
        assert result["instances"][1]["name"] == "ops"
        assert result["instances"][1]["labels"] == {}  # Default for missing attribute

    @pytest.mark.asyncio
    async def test_instance_get_info(self, instances_component, mock_server, mock_yamcs_client):
        """Test getting instance information."""
        instances_component.register_with_server(mock_server)
        
        # Mock instance
        mock_instance = Mock(
            name="simulator",
            state="RUNNING",
            mission_time="2024-01-01T12:00:00Z",
        )
        mock_instance.labels = {"env": "dev", "version": "1.0"}
        mock_instance.template = "standard"
        mock_instance.capabilities = ["tm", "tc", "archive"]
        
        # Mock processors
        mock_proc1 = Mock(name="realtime")
        mock_proc2 = Mock(name="replay")
        mock_instance.list_processors.return_value = [mock_proc1, mock_proc2]
        
        mock_yamcs_client.get_instance.return_value = mock_instance
        
        # Get tool function
        get_info_tool = mock_server._tools["instance_get_info"].fn
        
        result = await get_info_tool(instance="simulator")
        
        assert result["name"] == "simulator"
        assert result["state"] == "RUNNING"
        assert result["labels"] == {"env": "dev", "version": "1.0"}
        assert result["processors"] == ["realtime", "replay"]

    @pytest.mark.asyncio
    async def test_instance_get_info_default(self, instances_component, mock_server, mock_yamcs_client):
        """Test getting info for default instance."""
        instances_component.register_with_server(mock_server)
        
        # Mock instance without optional attributes
        mock_instance = Mock(spec=["name", "state", "mission_time"])
        mock_instance.name = "test-instance"
        mock_instance.state = "RUNNING"
        mock_instance.mission_time = "2024-01-01T12:00:00Z"
        
        mock_yamcs_client.get_instance.return_value = mock_instance
        
        # Get tool function
        get_info_tool = mock_server._tools["instance_get_info"].fn
        
        # Should use default instance when not specified
        result = await get_info_tool()
        
        # Verify default instance was used
        mock_yamcs_client.get_instance.assert_called_with("test-instance")
        assert result["name"] == "test-instance"
        assert result["labels"] == {}
        assert result["processors"] == []  # No list_processors method

    @pytest.mark.asyncio
    async def test_instance_start_stop(self, instances_component, mock_server, mock_yamcs_client):
        """Test starting and stopping instances."""
        instances_component.register_with_server(mock_server)
        
        # Mock instance
        mock_instance = Mock()
        mock_instance.start = Mock()
        mock_instance.stop = Mock()
        mock_yamcs_client.get_instance.return_value = mock_instance
        
        # Test start
        start_tool = mock_server._tools["instance_start_instance"].fn
        result = await start_tool(instance="simulator")
        
        assert result["success"] is True
        assert result["instance"] == "simulator"
        assert result["operation"] == "start"
        mock_instance.start.assert_called_once()
        
        # Test stop
        stop_tool = mock_server._tools["instance_stop_instance"].fn
        result = await stop_tool(instance="simulator")
        
        assert result["success"] is True
        assert result["instance"] == "simulator"
        assert result["operation"] == "stop"
        mock_instance.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_operations(self, instances_component, mock_server, mock_yamcs_client):
        """Test service listing and control."""
        instances_component.register_with_server(mock_server)
        
        # Mock services
        mock_svc1 = Mock(
            name="CommandHistory",
            class_name="org.yamcs.cmdhistory.CommandHistoryService",
            state="RUNNING",
        )
        mock_svc1.processor = "realtime"
        
        mock_svc2 = Mock(
            name="Archive",
            class_name="org.yamcs.archive.ArchiveService",
            state="RUNNING",
        )
        # Missing processor attribute
        
        mock_yamcs_client.list_services.return_value = [mock_svc1, mock_svc2]
        
        # Test list services
        list_services_tool = mock_server._tools["instance_list_services"].fn
        result = await list_services_tool(instance="simulator")
        
        assert result["instance"] == "simulator"
        assert result["count"] == 2
        assert result["services"][0]["processor"] == "realtime"
        assert result["services"][1]["processor"] is None
        
        # Test start service
        mock_yamcs_client.start_service = Mock()
        start_service_tool = mock_server._tools["instance_start_service"].fn
        result = await start_service_tool(service="Archive", instance="simulator")
        
        assert result["success"] is True
        assert result["service"] == "Archive"
        mock_yamcs_client.start_service.assert_called_with(
            instance="simulator",
            service="Archive"
        )
        
        # Test stop service
        mock_yamcs_client.stop_service = Mock()
        stop_service_tool = mock_server._tools["instance_stop_service"].fn
        result = await stop_service_tool(service="Archive")
        
        assert result["success"] is True
        assert result["service"] == "Archive"
        assert result["instance"] == "test-instance"  # Default instance
        mock_yamcs_client.stop_service.assert_called_with(
            instance="test-instance",
            service="Archive"
        )

    @pytest.mark.asyncio
    async def test_resource_handlers(self, instances_component, mock_server, mock_yamcs_client):
        """Test resource handlers."""
        instances_component.register_with_server(mock_server)
        
        # Mock instances for list resource
        mock_inst1 = Mock(name="simulator", state="RUNNING")
        mock_inst1.template = "standard"
        mock_inst2 = Mock(name="ops", state="OFFLINE")
        # Missing template
        
        mock_yamcs_client.list_instances.return_value = [mock_inst1, mock_inst2]
        
        # Test list instances resource
        list_resource = mock_server._resources["instance://list"].fn
        result = await list_resource()
        
        assert "Yamcs Instances:" in result
        assert "simulator: RUNNING (template: standard)" in result
        assert "ops: OFFLINE (template: none)" in result
        
        # Mock services for services resource
        mock_svc1 = Mock(
            name="CommandHistory",
            class_name="org.yamcs.cmdhistory.CommandHistoryService",
            state="RUNNING",
        )
        mock_svc1.processor = "realtime"
        
        mock_yamcs_client.list_services.return_value = [mock_svc1]
        
        # Test services resource
        services_resource = mock_server._resources["instance://services/{instance}"].fn
        result = await services_resource(instance="simulator")
        
        assert "Services in instance 'simulator' (1 total):" in result
        assert "CommandHistory [RUNNING]: org.yamcs.cmdhistory.CommandHistoryService (processor: realtime)" in result

    @pytest.mark.asyncio
    async def test_error_handling(self, instances_component, mock_server, mock_yamcs_client):
        """Test error handling in instance operations."""
        instances_component.register_with_server(mock_server)
        
        # Mock an error
        mock_yamcs_client.list_instances.side_effect = Exception("Connection refused")
        
        # Test error in list instances
        list_instances_tool = mock_server._tools["instance_list_instances"].fn
        result = await list_instances_tool()
        
        assert result["error"] is True
        assert "Connection refused" in result["message"]
        assert result["operation"] == "instance_list_instances"
        
        # Test error in start instance
        mock_yamcs_client.get_instance.side_effect = Exception("Instance not found")
        start_tool = mock_server._tools["instance_start_instance"].fn
        result = await start_tool(instance="nonexistent")
        
        assert result["error"] is True
        assert "Instance not found" in result["message"]
        assert result["operation"] == "instance_start_instance"

    @pytest.mark.asyncio
    async def test_missing_attributes(self, instances_component, mock_server, mock_yamcs_client):
        """Test handling of missing attributes in instance/service objects."""
        instances_component.register_with_server(mock_server)
        
        # Create instance with minimal attributes
        mock_instance = Mock(spec=["name", "state", "mission_time"])
        mock_instance.name = "minimal"
        mock_instance.state = "RUNNING"
        mock_instance.mission_time = None
        
        mock_yamcs_client.list_instances.return_value = [mock_instance]
        
        # Test list instances with missing attributes
        list_instances_tool = mock_server._tools["instance_list_instances"].fn
        result = await list_instances_tool()
        
        assert result["count"] == 1
        assert result["instances"][0]["labels"] == {}
        assert result["instances"][0]["template"] is None
        assert result["instances"][0]["capabilities"] == []
        
        # Test service with minimal attributes
        mock_service = Mock(spec=["name", "class_name", "state"])
        mock_service.name = "MinimalService"
        mock_service.class_name = "org.yamcs.MinimalService"
        mock_service.state = "RUNNING"
        
        mock_yamcs_client.list_services.return_value = [mock_service]
        
        list_services_tool = mock_server._tools["instance_list_services"].fn
        result = await list_services_tool()
        
        assert result["services"][0]["processor"] is None