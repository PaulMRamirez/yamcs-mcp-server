"""TM/TC Processing component for Yamcs MCP Server."""

from typing import Any

from ..client import YamcsClientManager
from ..config import YamcsConfig
from .base import BaseYamcsComponent


class ProcessorComponent(BaseYamcsComponent):
    """Processor component for TM/TC processing operations."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Processor component.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("Processor", client_manager, config)

    def register_with_server(self, server: Any) -> None:
        """Register Processor tools and resources with the server."""
        
        @server.tool()
        async def processor_list_processors(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """List available processors.

            Args:
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: List of processors with their status
            """
            try:
                async with self.client_manager.get_client() as client:
                    processors = []
                    for proc in client.list_processors(instance or self.config.instance):
                        processors.append({
                            "name": proc.name,
                            "state": proc.state,
                            "persistent": proc.persistent,
                            "time": proc.time,
                            "replay": proc.replay,
                        })
                    
                    return {
                        "instance": instance or self.config.instance,
                        "count": len(processors),
                        "processors": processors,
                    }
            except Exception as e:
                return self._handle_error("processor_list_processors", e)

        @server.tool()
        async def processor_get_status(
            processor: str = "realtime",
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get processor status.

            Args:
                processor: Processor name (default: realtime)
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Processor status information
            """
            try:
                async with self.client_manager.get_client() as client:
                    proc = client.get_processor(
                        instance=instance or self.config.instance,
                        processor=processor,
                    )
                    
                    return {
                        "instance": instance or self.config.instance,
                        "processor": processor,
                        "state": proc.state,
                        "time": proc.time,
                        "mission_time": proc.mission_time,
                        "statistics": {
                            "tm_packets": proc.tm_stats.packet_rate if hasattr(proc, 'tm_stats') else 0,
                            "parameters": proc.tm_stats.data_rate if hasattr(proc, 'tm_stats') else 0,
                        },
                    }
            except Exception as e:
                return self._handle_error("processor_get_status", e)

        @server.tool()
        async def processor_issue_command(
            command: str,
            args: dict[str, Any] | None = None,
            processor: str = "realtime",
            instance: str | None = None,
            dry_run: bool = False,
        ) -> dict[str, Any]:
            """Issue a command through the processor.

            Args:
                command: Command qualified name
                args: Command arguments as key-value pairs
                processor: Processor name (default: realtime)
                instance: Yamcs instance (uses default if not specified)
                dry_run: If true, validate but don't execute

            Returns:
                dict: Command execution result
            """
            try:
                async with self.client_manager.get_client() as client:
                    proc = client.get_processor(
                        instance=instance or self.config.instance,
                        processor=processor,
                    )
                    
                    if dry_run:
                        # Validate command
                        validation = proc.validate_command(command, args=args)
                        return {
                            "dry_run": True,
                            "valid": not validation.issues,
                            "issues": [
                                {"message": issue.message, "severity": issue.severity}
                                for issue in validation.issues
                            ] if validation.issues else [],
                        }
                    else:
                        # Issue command
                        cmd_result = proc.issue_command(command, args=args)
                        
                        return {
                            "success": True,
                            "command_id": cmd_result.id,
                            "command": command,
                            "generation_time": cmd_result.generation_time,
                            "origin": cmd_result.origin,
                            "sequence_number": cmd_result.sequence_number,
                        }
            except Exception as e:
                return self._handle_error("processor_issue_command", e)

        @server.tool()
        async def processor_get_parameter_value(
            parameter: str,
            processor: str = "realtime",
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get current value of a parameter.

            Args:
                parameter: Parameter qualified name
                processor: Processor name (default: realtime)
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Current parameter value and metadata
            """
            try:
                async with self.client_manager.get_client() as client:
                    proc = client.get_processor(
                        instance=instance or self.config.instance,
                        processor=processor,
                    )
                    
                    # Get parameter value
                    pval = proc.get_parameter_value(parameter)
                    
                    return {
                        "parameter": parameter,
                        "value": {
                            "eng_value": pval.eng_value.float_value if pval.eng_value else None,
                            "raw_value": pval.raw_value.sint32_value if pval.raw_value else None,
                            "generation_time": pval.generation_time,
                            "acquisition_time": pval.acquisition_time,
                            "validity": pval.acquisition_status,
                            "monitoring_result": pval.monitoring_result,
                        },
                    }
            except Exception as e:
                return self._handle_error("processor_get_parameter_value", e)

        @server.tool()
        async def processor_set_parameter_value(
            parameter: str,
            value: float | int | str | bool,
            processor: str = "realtime",
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Set parameter value (for writable parameters).

            Args:
                parameter: Parameter qualified name
                value: New parameter value
                processor: Processor name (default: realtime)
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with self.client_manager.get_client() as client:
                    proc = client.get_processor(
                        instance=instance or self.config.instance,
                        processor=processor,
                    )
                    
                    # Set parameter value
                    proc.set_parameter_value(parameter, value)
                    
                    return {
                        "success": True,
                        "parameter": parameter,
                        "value": value,
                        "processor": processor,
                    }
            except Exception as e:
                return self._handle_error("processor_set_parameter_value", e)

        # Register resources
        @server.resource("processor://status/{processor}")
        async def get_processor_status(processor: str = "realtime") -> str:
            """Get real-time processor status."""
            result = await self.processor_get_status(processor=processor)
            if "error" in result:
                return f"Error: {result['message']}"
            
            lines = [
                f"Processor: {result['processor']}",
                f"Instance: {result['instance']}",
                f"State: {result['state']}",
                f"Time: {result['time']}",
                f"Mission Time: {result['mission_time']}",
            ]
            
            if "statistics" in result:
                stats = result["statistics"]
                lines.extend([
                    "",
                    "Statistics:",
                    f"  TM Packets: {stats.get('tm_packets', 0)}/s",
                    f"  Parameters: {stats.get('parameters', 0)}/s",
                ])
            
            return "\n".join(lines)