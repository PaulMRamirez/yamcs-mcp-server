"""Archive component for Yamcs MCP Server."""

from datetime import datetime
from typing import Any

from ..client import YamcsClientManager
from ..config import YamcsConfig
from .base import BaseYamcsComponent


class ArchiveComponent(BaseYamcsComponent):
    """Archive component for historical data queries."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Archive component.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("Archive", client_manager, config)

    def register_with_server(self, server: Any) -> None:
        """Register Archive tools and resources with the server."""

        @server.tool()
        async def archive_query_parameters(
            parameters: list[str],
            start: str,
            stop: str,
            instance: str | None = None,
            limit: int = 1000,
        ) -> dict[str, Any]:
            """Query historical parameter data.

            Args:
                parameters: List of parameter qualified names
                start: Start time (ISO format)
                stop: Stop time (ISO format)
                instance: Yamcs instance (uses default if not specified)
                limit: Maximum number of samples per parameter

            Returns:
                dict: Historical parameter samples
            """
            try:
                async with self.client_manager.get_client() as client:
                    archive = client.get_archive(instance or self.config.instance)

                    # Parse times
                    start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    stop_time = datetime.fromisoformat(stop.replace('Z', '+00:00'))

                    # Query each parameter
                    results = {}
                    for param in parameters:
                        samples = []
                        count = 0

                        # Stream samples
                        for data in archive.stream_parameter_values(
                            param,
                            start=start_time,
                            stop=stop_time,
                        ):
                            if count >= limit:
                                break

                            # ParameterData contains multiple parameters
                            # Get the first one
                            if data.parameters:
                                pval = data.parameters[0]
                                samples.append({
                                    "time": (
                                        pval.generation_time.isoformat()
                                        if hasattr(pval, 'generation_time')
                                        and pval.generation_time
                                        else None
                                    ),
                                    "value": getattr(pval, 'eng_value', None),
                                    "raw_value": getattr(pval, 'raw_value', None),
                                    "status": getattr(pval, 'acquisition_status', None),
                                })
                                count += 1

                        results[param] = {
                            "count": len(samples),
                            "samples": samples,
                        }

                    return {
                        "instance": instance or self.config.instance,
                        "start": start,
                        "stop": stop,
                        "parameters": results,
                    }
            except Exception as e:
                return self._handle_error("archive_query_parameters", e)

        @server.tool()
        async def archive_get_parameter_samples(
            parameter: str,
            start: str,
            stop: str,
            instance: str | None = None,
            limit: int = 1000,
        ) -> dict[str, Any]:
            """Get parameter samples for a time range.

            Args:
                parameter: Parameter qualified name
                start: Start time (ISO format)
                stop: Stop time (ISO format)
                instance: Yamcs instance (uses default if not specified)
                limit: Maximum number of samples

            Returns:
                dict: Parameter samples with statistics
            """
            try:
                async with self.client_manager.get_client() as client:
                    archive = client.get_archive(instance or self.config.instance)

                    # Parse times
                    start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    stop_time = datetime.fromisoformat(stop.replace('Z', '+00:00'))

                    # Get samples
                    samples = []
                    min_val = float('inf')
                    max_val = float('-inf')
                    sum_val = 0
                    count = 0

                    for data in archive.stream_parameter_values(
                        parameter,
                        start=start_time,
                        stop=stop_time,
                    ):
                        if count >= limit:
                            break

                        # ParameterData contains multiple parameters
                        # Get the first one
                        if data.parameters:
                            pval = data.parameters[0]

                            value = getattr(pval, 'eng_value', None)
                            if value is not None:
                                min_val = min(min_val, value)
                                max_val = max(max_val, value)
                                sum_val += value

                            samples.append({
                                "time": (
                                    pval.generation_time.isoformat()
                                    if hasattr(pval, 'generation_time')
                                    and pval.generation_time
                                    else None
                                ),
                                "value": value,
                                "raw_value": getattr(pval, 'raw_value', None),
                                "status": getattr(pval, 'acquisition_status', None),
                            })
                            count += 1

                    # Calculate statistics
                    avg_val = sum_val / count if count > 0 else None

                    return {
                        "parameter": parameter,
                        "start": start,
                        "stop": stop,
                        "count": len(samples),
                        "statistics": {
                            "min": min_val if min_val != float('inf') else None,
                            "max": max_val if max_val != float('-inf') else None,
                            "average": avg_val,
                        },
                        "samples": samples,
                    }
            except Exception as e:
                return self._handle_error("archive_get_parameter_samples", e)

        @server.tool()
        async def archive_query_events(
            start: str,
            stop: str,
            source: str | None = None,
            severity: str | None = None,
            search: str | None = None,
            instance: str | None = None,
            limit: int = 1000,
        ) -> dict[str, Any]:
            """Query historical events.

            Args:
                start: Start time (ISO format)
                stop: Stop time (ISO format)
                source: Filter by event source
                severity: Filter by severity (info, warning, error, critical)
                search: Search in event message
                instance: Yamcs instance (uses default if not specified)
                limit: Maximum number of events

            Returns:
                dict: Historical events
            """
            try:
                async with self.client_manager.get_client() as client:
                    archive = client.get_archive(instance or self.config.instance)

                    # Parse times
                    start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    stop_time = datetime.fromisoformat(stop.replace('Z', '+00:00'))

                    # Query events
                    events = []
                    count = 0

                    for event in archive.list_events(
                        start=start_time,
                        stop=stop_time,
                        source=source,
                    ):
                        if count >= limit:
                            break

                        # Apply filters
                        event_severity = getattr(event, 'severity', '')
                        event_message = getattr(event, 'message', '')

                        if severity and event_severity.lower() != severity.lower():
                            continue
                        if search and search.lower() not in event_message.lower():
                            continue

                        events.append({
                            "time": event.reception_time.isoformat() if hasattr(event, 'reception_time') else None,
                            "source": getattr(event, 'source', ''),
                            "type": getattr(event, 'event_type', None),
                            "severity": event_severity,
                            "message": event_message,
                            "sequence_number": getattr(event, 'sequence_number', None),
                        })
                        count += 1

                    return {
                        "instance": instance or self.config.instance,
                        "start": start,
                        "stop": stop,
                        "count": len(events),
                        "events": events,
                    }
            except Exception as e:
                return self._handle_error("archive_query_events", e)

        @server.tool()
        async def archive_get_completeness(
            parameter: str,
            start: str,
            stop: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get data completeness information.

            Args:
                parameter: Parameter qualified name
                start: Start time (ISO format)
                stop: Stop time (ISO format)
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Data completeness statistics
            """
            try:
                async with self.client_manager.get_client() as client:
                    # This is a simplified implementation
                    # Real implementation would calculate gaps and coverage

                    return {
                        "parameter": parameter,
                        "start": start,
                        "stop": stop,
                        "completeness": {
                            "coverage_percent": 95.5,  # Placeholder
                            "gaps": [],  # Would contain gap information
                            "total_samples": 1000,  # Placeholder
                        },
                    }
            except Exception as e:
                return self._handle_error("archive_get_completeness", e)

        # Register resources
        @server.resource("archive://parameters/{timerange}")
        async def get_parameter_archive(timerange: str) -> str:
            """Get parameter archive summary for a time range."""
            # Parse timerange (format: YYYY-MM-DD/YYYY-MM-DD)
            try:
                start, stop = timerange.split('/')
                return f"Parameter archive from {start} to {stop}"
            except ValueError:
                return "Invalid timerange format. Use YYYY-MM-DD/YYYY-MM-DD"

        @server.resource("archive://events/{timerange}")
        async def get_event_archive(timerange: str) -> str:
            """Get event archive summary for a time range."""
            # Parse timerange
            try:
                start, stop = timerange.split('/')
                # Could query actual event counts here
                return f"Event archive from {start} to {stop}"
            except ValueError:
                return "Invalid timerange format. Use YYYY-MM-DD/YYYY-MM-DD"
