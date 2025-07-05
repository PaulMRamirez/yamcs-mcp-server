"""Tests for the Processor component."""

from unittest.mock import Mock

import pytest

from yamcs_mcp.components.processor import ProcessorComponent


class TestProcessorComponent:
    """Test the Processor component."""

    @pytest.fixture
    def processor_component(self, mock_client_manager, mock_yamcs_config):
        """Create a Processor component instance."""
        return ProcessorComponent(mock_client_manager, mock_yamcs_config)

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

    def test_component_initialization(self, processor_component):
        """Test that the component initializes correctly."""
        assert processor_component.name == "YamcsProcessor"
        assert processor_component.client_manager is not None
        assert processor_component.config is not None

    def test_register_with_server(self, processor_component, mock_server):
        """Test component registration with server."""
        processor_component.register_with_server(mock_server)

        # Check tools were registered
        expected_tools = [
            "processor_list_processors",
            "processor_get_status",
            "processor_issue_command",
            "processor_get_parameter_value",
            "processor_set_parameter_value",
        ]

        for tool_name in expected_tools:
            assert tool_name in mock_server._tools

        # Check resources were registered
        expected_resources = [
            "processor://status/{processor}",
        ]

        for resource_uri in expected_resources:
            assert resource_uri in mock_server._resources

    @pytest.mark.asyncio
    async def test_processor_list_processors(
        self, processor_component, mock_server, mock_yamcs_client
    ):
        """Test listing processors."""
        processor_component.register_with_server(mock_server)

        # Mock processors
        mock_proc1 = Mock(
            name="realtime",
            state="RUNNING",
            persistent=True,
            time="2024-01-01T12:00:00Z",
            replay=False,
        )

        mock_proc2 = Mock(
            name="replay",
            state="STOPPED",
            persistent=False,
            time="2024-01-01T10:00:00Z",
            replay=True,
        )

        mock_yamcs_client.list_processors.return_value = [mock_proc1, mock_proc2]

        # Get tool function
        list_processors_tool = mock_server._tools["processor_list_processors"].fn

        result = await list_processors_tool()

        assert result["instance"] == "test-instance"
        assert result["count"] == 2
        assert len(result["processors"]) == 2

        assert result["processors"][0]["name"] == "realtime"
        assert result["processors"][0]["state"] == "RUNNING"
        assert result["processors"][0]["persistent"] is True
        assert result["processors"][0]["replay"] is False

        assert result["processors"][1]["name"] == "replay"
        assert result["processors"][1]["state"] == "STOPPED"
        assert result["processors"][1]["replay"] is True

    @pytest.mark.asyncio
    async def test_processor_get_status(
        self, processor_component, mock_server, mock_yamcs_client
    ):
        """Test getting processor status."""
        processor_component.register_with_server(mock_server)

        # Mock processor with TM stats
        mock_proc = Mock(
            state="RUNNING",
            time="2024-01-01T12:00:00Z",
            mission_time="2024-01-01T12:00:00.000Z",
        )
        mock_tm_stats = Mock(packet_rate=100.5, data_rate=500.2)
        mock_proc.tm_stats = mock_tm_stats

        mock_yamcs_client.get_processor.return_value = mock_proc

        # Get tool function
        get_status_tool = mock_server._tools["processor_get_status"].fn

        result = await get_status_tool(processor="realtime")

        assert result["processor"] == "realtime"
        assert result["state"] == "RUNNING"
        assert result["time"] == "2024-01-01T12:00:00Z"
        assert result["mission_time"] == "2024-01-01T12:00:00.000Z"
        assert result["statistics"]["tm_packets"] == 100.5
        assert result["statistics"]["parameters"] == 500.2

    @pytest.mark.asyncio
    async def test_processor_get_status_no_stats(
        self, processor_component, mock_server, mock_yamcs_client
    ):
        """Test getting processor status without TM stats."""
        processor_component.register_with_server(mock_server)

        # Mock processor without TM stats
        mock_proc = Mock(spec=["state", "time", "mission_time"])
        mock_proc.state = "RUNNING"
        mock_proc.time = "2024-01-01T12:00:00Z"
        mock_proc.mission_time = "2024-01-01T12:00:00.000Z"

        mock_yamcs_client.get_processor.return_value = mock_proc

        # Get tool function
        get_status_tool = mock_server._tools["processor_get_status"].fn

        result = await get_status_tool()

        assert result["statistics"]["tm_packets"] == 0
        assert result["statistics"]["parameters"] == 0

    @pytest.mark.asyncio
    async def test_processor_issue_command(
        self, processor_component, mock_server, mock_yamcs_client
    ):
        """Test issuing commands."""
        processor_component.register_with_server(mock_server)

        # Mock processor
        mock_proc = Mock()

        # Mock command result
        mock_cmd_result = Mock(
            id="CMD-123",
            generation_time="2024-01-01T12:00:00Z",
            origin="MCP",
            sequence_number=456,
        )
        mock_proc.issue_command.return_value = mock_cmd_result

        mock_yamcs_client.get_processor.return_value = mock_proc

        # Get tool function
        issue_command_tool = mock_server._tools["processor_issue_command"].fn

        # Test issuing command
        result = await issue_command_tool(
            command="/spacecraft/power/enable",
            args={"subsystem": "battery"},
            processor="realtime"
        )

        assert result["success"] is True
        assert result["command_id"] == "CMD-123"
        assert result["command"] == "/spacecraft/power/enable"
        assert result["generation_time"] == "2024-01-01T12:00:00Z"
        assert result["origin"] == "MCP"
        assert result["sequence_number"] == 456

        mock_proc.issue_command.assert_called_once_with(
            "/spacecraft/power/enable",
            args={"subsystem": "battery"}
        )

    @pytest.mark.asyncio
    async def test_processor_issue_command_dry_run(
        self, processor_component, mock_server, mock_yamcs_client
    ):
        """Test dry run command validation."""
        processor_component.register_with_server(mock_server)

        # Mock processor
        mock_proc = Mock()

        # Mock validation result - no issues
        mock_validation = Mock(issues=[])
        mock_proc.validate_command.return_value = mock_validation

        mock_yamcs_client.get_processor.return_value = mock_proc

        # Get tool function
        issue_command_tool = mock_server._tools["processor_issue_command"].fn

        # Test dry run - valid command
        result = await issue_command_tool(
            command="/spacecraft/power/enable",
            dry_run=True
        )

        assert result["dry_run"] is True
        assert result["valid"] is True
        assert result["issues"] == []

        # Test dry run - invalid command
        mock_issue = Mock(message="Missing required argument", severity="ERROR")
        mock_validation.issues = [mock_issue]

        result = await issue_command_tool(
            command="/spacecraft/power/enable",
            dry_run=True
        )

        assert result["dry_run"] is True
        assert result["valid"] is False
        assert len(result["issues"]) == 1
        assert result["issues"][0]["message"] == "Missing required argument"
        assert result["issues"][0]["severity"] == "ERROR"

    @pytest.mark.asyncio
    async def test_processor_get_parameter_value(
        self, processor_component, mock_server, mock_yamcs_client
    ):
        """Test getting parameter values."""
        processor_component.register_with_server(mock_server)

        # Mock processor
        mock_proc = Mock()

        # Mock parameter value with all attributes
        mock_pval = Mock(
            eng_value=25.5,
            raw_value=255,
            generation_time="2024-01-01T12:00:00Z",
            acquisition_time="2024-01-01T12:00:00.500Z",
            acquisition_status="ACQUIRED",
            monitoring_result="IN_LIMITS",
        )
        mock_proc.get_parameter_value.return_value = mock_pval

        mock_yamcs_client.get_processor.return_value = mock_proc

        # Get tool function
        get_param_tool = mock_server._tools["processor_get_parameter_value"].fn

        result = await get_param_tool(parameter="/spacecraft/battery/voltage")

        assert result["parameter"] == "/spacecraft/battery/voltage"
        assert result["value"]["eng_value"] == 25.5
        assert result["value"]["raw_value"] == 255
        assert result["value"]["generation_time"] == "2024-01-01T12:00:00Z"
        assert result["value"]["acquisition_time"] == "2024-01-01T12:00:00.500Z"
        assert result["value"]["validity"] == "ACQUIRED"
        assert result["value"]["monitoring_result"] == "IN_LIMITS"

    @pytest.mark.asyncio
    async def test_processor_get_parameter_value_missing_attrs(
        self, processor_component, mock_server, mock_yamcs_client
    ):
        """Test getting parameter values with missing attributes."""
        processor_component.register_with_server(mock_server)

        # Mock processor
        mock_proc = Mock()

        # Mock parameter value with minimal attributes
        mock_pval = Mock(spec=[])  # No attributes
        mock_proc.get_parameter_value.return_value = mock_pval

        mock_yamcs_client.get_processor.return_value = mock_proc

        # Get tool function
        get_param_tool = mock_server._tools["processor_get_parameter_value"].fn

        result = await get_param_tool(parameter="/spacecraft/test/param")

        assert result["parameter"] == "/spacecraft/test/param"
        assert result["value"]["eng_value"] is None
        assert result["value"]["raw_value"] is None
        assert result["value"]["generation_time"] is None
        assert result["value"]["validity"] is None

    @pytest.mark.asyncio
    async def test_processor_set_parameter_value(
        self, processor_component, mock_server, mock_yamcs_client
    ):
        """Test setting parameter values."""
        processor_component.register_with_server(mock_server)

        # Mock processor
        mock_proc = Mock()
        mock_proc.set_parameter_value = Mock()

        mock_yamcs_client.get_processor.return_value = mock_proc

        # Get tool function
        set_param_tool = mock_server._tools["processor_set_parameter_value"].fn

        # Test setting different value types
        test_cases = [
            ("/spacecraft/config/threshold", 42.5),
            ("/spacecraft/config/enabled", True),
            ("/spacecraft/config/mode", "OPERATIONAL"),
            ("/spacecraft/config/count", 100),
        ]

        for param, value in test_cases:
            result = await set_param_tool(
                parameter=param,
                value=value,
                processor="realtime"
            )

            assert result["success"] is True
            assert result["parameter"] == param
            assert result["value"] == value
            assert result["processor"] == "realtime"

            mock_proc.set_parameter_value.assert_called_with(param, value)

    @pytest.mark.asyncio
    async def test_resource_handler(
        self, processor_component, mock_server, mock_yamcs_client
    ):
        """Test processor status resource handler."""
        processor_component.register_with_server(mock_server)

        # Mock processor with TM stats
        mock_proc = Mock(
            state="RUNNING",
            time="2024-01-01T12:00:00Z",
            mission_time="2024-01-01T12:00:00.000Z",
        )
        mock_tm_stats = Mock()
        mock_tm_stats.packet_rate = 150
        mock_tm_stats.data_rate = 750
        mock_proc.tm_stats = mock_tm_stats

        mock_yamcs_client.get_processor.return_value = mock_proc

        # Test status resource
        status_resource = mock_server._resources["processor://status/{processor}"].fn
        result = await status_resource(processor="realtime")

        assert "Processor: realtime" in result
        assert "Instance: test-instance" in result
        assert "State: RUNNING" in result
        assert "TM Packets: 150/s" in result
        assert "Parameters: 750/s" in result

    @pytest.mark.asyncio
    async def test_error_handling(
        self, processor_component, mock_server, mock_yamcs_client
    ):
        """Test error handling in processor operations."""
        processor_component.register_with_server(mock_server)

        # Mock an error
        mock_yamcs_client.list_processors.side_effect = Exception("Connection lost")

        # Test error in list processors
        list_processors_tool = mock_server._tools["processor_list_processors"].fn
        result = await list_processors_tool()

        assert result["error"] is True
        assert "Connection lost" in result["message"]
        assert result["operation"] == "processor_list_processors"

        # Test error in issue command
        mock_yamcs_client.get_processor.side_effect = Exception("Processor unavailable")
        issue_command_tool = mock_server._tools["processor_issue_command"].fn
        result = await issue_command_tool(command="/test/command")

        assert result["error"] is True
        assert "Processor unavailable" in result["message"]
        assert result["operation"] == "processor_issue_command"
