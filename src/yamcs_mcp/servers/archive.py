"""Archive server for Yamcs MCP."""

from datetime import datetime
from typing import Any

from ..client import YamcsClientManager
from ..components.base_server import BaseYamcsServer
from ..config import YamcsConfig


class ArchiveServer(BaseYamcsServer):
    """Archive server for accessing Yamcs data archive."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Archive server.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("Archive", client_manager, config)
        self._register_archive_tools()
        self._register_archive_resources()

    def _register_archive_tools(self) -> None:
        """Register archive-specific tools."""
        
        @self.tool()
        async def list(
            instance: str | None = None,
            start: str | None = None,
            stop: str | None = None,
            name: str | None = None,
            limit: int = 100,
        ) -> dict[str, Any]:
            """List packets from the archive.

            Args:
                instance: Yamcs instance (uses default if not specified)
                start: Start time (ISO format)
                stop: Stop time (ISO format)
                name: Filter by packet name
                limit: Maximum number of packets to return (default: 100)

            Returns:
                dict: List of packets
            """
            try:
                async with self.client_manager.get_client() as client:
                    archive = client.get_archive(instance or self.config.instance)
                    
                    # Prepare query parameters
                    kwargs = {"limit": limit}
                    if start:
                        kwargs["start"] = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    if stop:
                        kwargs["stop"] = datetime.fromisoformat(stop.replace('Z', '+00:00'))
                    if name:
                        kwargs["name"] = name
                    
                    # Query packets
                    packets = []
                    for packet in archive.list_packets(**kwargs):
                        packets.append({
                            "id": packet.id,
                            "name": packet.name,
                            "generation_time": packet.generation_time.isoformat() if packet.generation_time else None,
                            "reception_time": packet.reception_time.isoformat() if packet.reception_time else None,
                            "size": packet.size,
                        })
                    
                    return {
                        "instance": instance or self.config.instance,
                        "count": len(packets),
                        "packets": packets,
                    }
            except Exception as e:
                return self._handle_error("list", e)

        @self.tool()
        async def get_parameter_values(
            parameter: str,
            instance: str | None = None,
            start: str | None = None,
            stop: str | None = None,
            limit: int = 100,
        ) -> dict[str, Any]:
            """Get parameter values from the archive.

            Args:
                parameter: Parameter qualified name
                instance: Yamcs instance (uses default if not specified)
                start: Start time (ISO format)
                stop: Stop time (ISO format)
                limit: Maximum number of values to return (default: 100)

            Returns:
                dict: Parameter values
            """
            try:
                async with self.client_manager.get_client() as client:
                    archive = client.get_archive(instance or self.config.instance)
                    
                    # Prepare query parameters
                    kwargs = {"limit": limit}
                    if start:
                        kwargs["start"] = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    if stop:
                        kwargs["stop"] = datetime.fromisoformat(stop.replace('Z', '+00:00'))
                    
                    # Query parameter values
                    values = []
                    for pval in archive.list_parameter_values(parameter, **kwargs):
                        # Extract value based on type
                        value = None
                        if hasattr(pval, 'eng_value'):
                            value = pval.eng_value
                        elif hasattr(pval, 'raw_value'):
                            value = pval.raw_value
                        
                        values.append({
                            "time": pval.generation_time.isoformat() if pval.generation_time else None,
                            "value": value,
                            "status": getattr(pval, 'monitoring_result', None),
                        })
                    
                    return {
                        "parameter": parameter,
                        "instance": instance or self.config.instance,
                        "count": len(values),
                        "values": values,
                    }
            except Exception as e:
                return self._handle_error("get_parameter_values", e)

        @self.tool()
        async def get_command_history(
            command: str | None = None,
            instance: str | None = None,
            start: str | None = None,
            stop: str | None = None,
            limit: int = 100,
        ) -> dict[str, Any]:
            """Get command history from the archive.

            Args:
                command: Command name filter (optional)
                instance: Yamcs instance (uses default if not specified)
                start: Start time (ISO format)
                stop: Stop time (ISO format)
                limit: Maximum number of commands to return (default: 100)

            Returns:
                dict: Command history
            """
            try:
                async with self.client_manager.get_client() as client:
                    archive = client.get_archive(instance or self.config.instance)
                    
                    # Prepare query parameters
                    kwargs = {"limit": limit}
                    if start:
                        kwargs["start"] = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    if stop:
                        kwargs["stop"] = datetime.fromisoformat(stop.replace('Z', '+00:00'))
                    
                    # Query command history
                    commands = []
                    for cmd in archive.list_command_history(**kwargs):
                        # Filter by command name if specified
                        if command and command not in cmd.name:
                            continue
                        
                        commands.append({
                            "id": cmd.id,
                            "name": cmd.name,
                            "generation_time": cmd.generation_time.isoformat() if cmd.generation_time else None,
                            "origin": cmd.origin,
                            "username": getattr(cmd, 'username', None),
                            "final_status": getattr(cmd, 'final_status', None),
                        })
                    
                    return {
                        "instance": instance or self.config.instance,
                        "count": len(commands),
                        "commands": commands,
                    }
            except Exception as e:
                return self._handle_error("get_command_history", e)

        @self.tool()
        async def get_events(
            instance: str | None = None,
            start: str | None = None,
            stop: str | None = None,
            severity: str | None = None,
            source: str | None = None,
            limit: int = 100,
        ) -> dict[str, Any]:
            """Get events from the archive.

            Args:
                instance: Yamcs instance (uses default if not specified)
                start: Start time (ISO format)
                stop: Stop time (ISO format)
                severity: Filter by severity (info, warning, error, critical)
                source: Filter by event source
                limit: Maximum number of events to return (default: 100)

            Returns:
                dict: List of events
            """
            try:
                async with self.client_manager.get_client() as client:
                    archive = client.get_archive(instance or self.config.instance)
                    
                    # Prepare query parameters
                    kwargs = {"limit": limit}
                    if start:
                        kwargs["start"] = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    if stop:
                        kwargs["stop"] = datetime.fromisoformat(stop.replace('Z', '+00:00'))
                    if severity:
                        kwargs["severity"] = severity.upper()
                    if source:
                        kwargs["source"] = source
                    
                    # Query events
                    events = []
                    for event in archive.list_events(**kwargs):
                        events.append({
                            "generation_time": event.generation_time.isoformat() if event.generation_time else None,
                            "source": event.source,
                            "type": event.type,
                            "message": event.message,
                            "severity": event.severity,
                        })
                    
                    return {
                        "instance": instance or self.config.instance,
                        "count": len(events),
                        "events": events,
                    }
            except Exception as e:
                return self._handle_error("get_events", e)

    def _register_archive_resources(self) -> None:
        """Register archive-specific resources."""
        
        @self.resource("archive://overview")
        async def get_archive_overview() -> str:
            """Get an overview of the archive."""
            try:
                async with self.client_manager.get_client() as client:
                    # Get instance info
                    instance = client.get_instance(self.config.instance)
                    
                    lines = [
                        f"Archive Overview for {self.config.instance}:",
                        f"  State: {instance.state}",
                    ]
                    
                    if hasattr(instance, 'mission_time'):
                        lines.append(f"  Mission Time: {instance.mission_time}")
                    
                    # Try to get some statistics
                    try:
                        archive = client.get_archive(self.config.instance)
                        # Get recent packet count
                        packet_count = sum(1 for _ in archive.list_packets(limit=1000))
                        lines.append(f"  Recent Packets: {packet_count} (last 1000)")
                    except Exception:
                        pass
                    
                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"