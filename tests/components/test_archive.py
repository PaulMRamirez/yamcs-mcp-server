"""Tests for the Archive component."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from yamcs_mcp.components.archive import ArchiveComponent


class TestArchiveComponent:
    """Test the Archive component."""

    @pytest.fixture
    def archive_component(self, mock_client_manager, mock_yamcs_config):
        """Create an Archive component instance."""
        return ArchiveComponent(mock_client_manager, mock_yamcs_config)

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

    def test_component_initialization(self, archive_component):
        """Test that the component initializes correctly."""
        assert archive_component.name == "YamcsArchive"
        assert archive_component.client_manager is not None
        assert archive_component.config is not None

    def test_register_with_server(self, archive_component, mock_server):
        """Test component registration with server."""
        archive_component.register_with_server(mock_server)

        # Check tools were registered
        expected_tools = [
            "archive_query_parameters",
            "archive_get_parameter_samples",
            "archive_query_events",
            "archive_get_completeness",
        ]

        for tool_name in expected_tools:
            assert tool_name in mock_server._tools

    @pytest.mark.asyncio
    async def test_archive_query_parameters(
        self, archive_component, mock_server, mock_yamcs_client
    ):
        """Test querying historical parameter data."""
        archive_component.register_with_server(mock_server)

        # Mock archive client
        mock_archive = Mock()

        # Mock parameter data objects
        mock_data1 = Mock()
        mock_data1.parameters = [
            Mock(
                generation_time=datetime(2024, 1, 1, 10, 0, 0),
                eng_value=12.5,
                raw_value=125,
                acquisition_status="ACQUIRED",
            )
        ]

        mock_data2 = Mock()
        mock_data2.parameters = [
            Mock(
                generation_time=datetime(2024, 1, 1, 10, 1, 0),
                eng_value=13.0,
                raw_value=130,
                acquisition_status="ACQUIRED",
            )
        ]

        mock_archive.stream_parameter_values.return_value = [mock_data1, mock_data2]
        mock_yamcs_client.get_archive.return_value = mock_archive

        # Get tool function
        query_params_tool = mock_server._tools["archive_query_parameters"].fn

        # Test query
        result = await query_params_tool(
            parameters=["/test/param1"],
            start="2024-01-01T10:00:00Z",
            stop="2024-01-01T10:05:00Z",
        )

        assert result["instance"] == "test-instance"
        assert "/test/param1" in result["parameters"]
        assert result["parameters"]["/test/param1"]["count"] == 2
        assert len(result["parameters"]["/test/param1"]["samples"]) == 2

    @pytest.mark.asyncio
    async def test_archive_get_parameter_samples(
        self, archive_component, mock_server, mock_yamcs_client
    ):
        """Test getting parameter samples with statistics."""
        archive_component.register_with_server(mock_server)

        # Mock archive client
        mock_archive = Mock()

        # Create parameter data with values for statistics
        values = [10.0, 12.5, 15.0, 11.0, 13.5]
        mock_data_list = []

        for i, value in enumerate(values):
            mock_data = Mock()
            mock_data.parameters = [
                Mock(
                    generation_time=datetime(2024, 1, 1, 10, i, 0),
                    eng_value=value,
                    raw_value=int(value * 10),
                    acquisition_status="ACQUIRED",
                )
            ]
            mock_data_list.append(mock_data)

        mock_archive.stream_parameter_values.return_value = mock_data_list
        mock_yamcs_client.get_archive.return_value = mock_archive

        # Get tool function
        get_samples_tool = mock_server._tools["archive_get_parameter_samples"].fn

        # Test getting samples
        result = await get_samples_tool(
            parameter="/test/voltage",
            start="2024-01-01T10:00:00Z",
            stop="2024-01-01T10:10:00Z",
        )

        assert result["parameter"] == "/test/voltage"
        assert result["count"] == 5
        assert result["statistics"]["min"] == 10.0
        assert result["statistics"]["max"] == 15.0
        assert result["statistics"]["average"] == 12.4  # (10+12.5+15+11+13.5)/5

    @pytest.mark.asyncio
    async def test_archive_query_events(
        self, archive_component, mock_server, mock_yamcs_client
    ):
        """Test querying historical events."""
        archive_component.register_with_server(mock_server)

        # Mock archive client
        mock_archive = Mock()

        # Mock events
        mock_events = [
            Mock(
                reception_time=datetime(2024, 1, 1, 10, 0, 0),
                source="TestSystem",
                event_type="ALARM",  # Using event_type instead of type
                severity="WARNING",
                message="Test warning event",
                sequence_number=1,
            ),
            Mock(
                reception_time=datetime(2024, 1, 1, 10, 1, 0),
                source="TestSystem",
                event_type="INFO",
                severity="INFO",
                message="Test info event",
                sequence_number=2,
            ),
        ]

        mock_archive.list_events.return_value = mock_events
        mock_yamcs_client.get_archive.return_value = mock_archive

        # Get tool function
        query_events_tool = mock_server._tools["archive_query_events"].fn

        # Test query
        result = await query_events_tool(
            start="2024-01-01T10:00:00Z",
            stop="2024-01-01T10:05:00Z",
        )

        assert result["count"] == 2
        assert len(result["events"]) == 2
        assert result["events"][0]["source"] == "TestSystem"
        assert result["events"][0]["type"] == "ALARM"
        assert result["events"][0]["severity"] == "WARNING"

    @pytest.mark.asyncio
    async def test_archive_query_events_with_filters(
        self, archive_component, mock_server, mock_yamcs_client
    ):
        """Test querying events with filters."""
        archive_component.register_with_server(mock_server)

        # Mock archive client
        mock_archive = Mock()

        # Mock events with different severities and messages
        mock_events = [
            Mock(
                reception_time=datetime(2024, 1, 1, 10, 0, 0),
                source="System1",
                severity="WARNING",
                message="Temperature high",
                sequence_number=1,
            ),
            Mock(
                reception_time=datetime(2024, 1, 1, 10, 1, 0),
                source="System2",
                severity="INFO",
                message="System started",
                sequence_number=2,
            ),
            Mock(
                reception_time=datetime(2024, 1, 1, 10, 2, 0),
                source="System1",
                severity="WARNING",
                message="Voltage low",
                sequence_number=3,
            ),
        ]

        # Add event_type attribute to avoid attribute errors
        for event in mock_events:
            event.event_type = None

        mock_archive.list_events.return_value = mock_events
        mock_yamcs_client.get_archive.return_value = mock_archive

        # Get tool function
        query_events_tool = mock_server._tools["archive_query_events"].fn

        # Test severity filter
        result = await query_events_tool(
            start="2024-01-01T10:00:00Z",
            stop="2024-01-01T10:05:00Z",
            severity="warning",  # Should be case insensitive
        )

        assert result["count"] == 2  # Only WARNING events

        # Test search filter
        result = await query_events_tool(
            start="2024-01-01T10:00:00Z",
            stop="2024-01-01T10:05:00Z",
            search="voltage",
        )

        assert result["count"] == 1  # Only event with "voltage" in message

    @pytest.mark.asyncio
    async def test_missing_attributes_handling(
        self, archive_component, mock_server, mock_yamcs_client
    ):
        """Test handling of missing attributes in parameter/event objects."""
        archive_component.register_with_server(mock_server)

        # Mock archive client
        mock_archive = Mock()

        # Create parameter data with missing attributes
        mock_data = Mock()
        mock_param = Mock(spec=[])  # Empty spec - no attributes
        mock_param.generation_time = None  # Explicitly None
        # Don't set eng_value, raw_value, or acquisition_status
        mock_data.parameters = [mock_param]

        mock_archive.stream_parameter_values.return_value = [mock_data]
        mock_yamcs_client.get_archive.return_value = mock_archive

        # Get tool function
        get_samples_tool = mock_server._tools["archive_get_parameter_samples"].fn

        # Should handle missing attributes gracefully
        result = await get_samples_tool(
            parameter="/test/param",
            start="2024-01-01T10:00:00Z",
            stop="2024-01-01T10:05:00Z",
        )

        assert result["count"] == 1
        assert result["samples"][0]["time"] is None
        assert result["samples"][0]["value"] is None
        assert result["samples"][0]["raw_value"] is None
        assert result["samples"][0]["status"] is None

    @pytest.mark.asyncio
    async def test_empty_results(
        self, archive_component, mock_server, mock_yamcs_client
    ):
        """Test handling of empty results."""
        archive_component.register_with_server(mock_server)

        # Mock archive client with no data
        mock_archive = Mock()
        mock_archive.stream_parameter_values.return_value = []
        mock_archive.list_events.return_value = []
        mock_yamcs_client.get_archive.return_value = mock_archive

        # Test empty parameter query
        query_params_tool = mock_server._tools["archive_query_parameters"].fn
        result = await query_params_tool(
            parameters=["/test/param"],
            start="2024-01-01T10:00:00Z",
            stop="2024-01-01T10:05:00Z",
        )

        assert result["parameters"]["/test/param"]["count"] == 0
        assert result["parameters"]["/test/param"]["samples"] == []

        # Test empty event query
        query_events_tool = mock_server._tools["archive_query_events"].fn
        result = await query_events_tool(
            start="2024-01-01T10:00:00Z",
            stop="2024-01-01T10:05:00Z",
        )

        assert result["count"] == 0
        assert result["events"] == []

    @pytest.mark.asyncio
    async def test_error_handling(
        self, archive_component, mock_server, mock_yamcs_client
    ):
        """Test error handling in archive operations."""
        archive_component.register_with_server(mock_server)

        # Mock an error
        mock_yamcs_client.get_archive.side_effect = Exception("Archive unavailable")

        # Get tool function
        query_params_tool = mock_server._tools["archive_query_parameters"].fn

        result = await query_params_tool(
            parameters=["/test/param"],
            start="2024-01-01T10:00:00Z",
            stop="2024-01-01T10:05:00Z",
        )

        assert result["error"] is True
        assert "Archive unavailable" in result["message"]
        assert result["operation"] == "archive_query_parameters"

    @pytest.mark.asyncio
    async def test_parameter_data_structure(
        self, archive_component, mock_server, mock_yamcs_client
    ):
        """Test handling of ParameterData structure from stream_parameter_values."""
        archive_component.register_with_server(mock_server)

        # Mock archive client
        mock_archive = Mock()

        # Test case where ParameterData has empty parameters list
        mock_data_empty = Mock()
        mock_data_empty.parameters = []

        # Test case where ParameterData has multiple parameters
        # (shouldn't happen for single param query)
        mock_data_multi = Mock()
        mock_data_multi.parameters = [
            Mock(generation_time=datetime.now(), eng_value=1.0),
            Mock(generation_time=datetime.now(), eng_value=2.0),
        ]

        mock_archive.stream_parameter_values.return_value = [
            mock_data_empty, mock_data_multi
        ]
        mock_yamcs_client.get_archive.return_value = mock_archive

        # Get tool function
        get_samples_tool = mock_server._tools["archive_get_parameter_samples"].fn

        result = await get_samples_tool(
            parameter="/test/param",
            start="2024-01-01T10:00:00Z",
            stop="2024-01-01T10:05:00Z",
        )

        # Should only process first parameter from each ParameterData
        assert result["count"] == 1  # Only one from mock_data_multi
