"""Processors server for Yamcs MCP."""

from typing import Any

from ..client import YamcsClientManager
from .base_server import BaseYamcsServer
from ..config import YamcsConfig


class ProcessorsServer(BaseYamcsServer):
    """Processors server for managing Yamcs processors."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Processors server.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("Processors", client_manager, config)
        self._register_processor_tools()
        self._register_processor_resources()

    def _register_processor_tools(self) -> None:
        """Register processor-specific tools."""
        
        @self.tool()
        async def list_processors(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """List all processors.

            Args:
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: List of processors
            """
            try:
                async with self.client_manager.get_client() as client:
                    processors = []
                    for proc in client.list_processors(instance or self.config.instance):
                        processors.append({
                            "name": proc.name,
                            "state": proc.state,
                            "mission_time": proc.mission_time.isoformat() if proc.mission_time else None,
                            "type": getattr(proc, 'type', 'realtime'),
                            "replay": getattr(proc, 'replay', False),
                            "persistent": getattr(proc, 'persistent', True),
                        })
                    
                    return {
                        "instance": instance or self.config.instance,
                        "count": len(processors),
                        "processors": processors,
                    }
            except Exception as e:
                return self._handle_error("list_processors", e)

        @self.tool()
        async def describe_processor(
            processor: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get comprehensive information about a processor.

            Args:
                processor: Processor name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Complete processor information including configuration and statistics
            """
            try:
                async with self.client_manager.get_client() as client:
                    # Find the processor in the list since ProcessorClient doesn't have the info
                    target_instance = instance or self.config.instance
                    proc_info = None
                    
                    for proc in client.list_processors(target_instance):
                        if proc.name == processor:
                            proc_info = proc
                            break
                    
                    if not proc_info:
                        return self._handle_error(
                            "describe_processor", 
                            Exception(f"Processor '{processor}' not found in instance '{target_instance}'")
                        )
                    
                    # Get processor client for additional operations if needed
                    proc_client = client.get_processor(target_instance, processor)
                    
                    # Build comprehensive processor information
                    processor_details = {
                        "name": proc_info.name,
                        "instance": target_instance,
                        "state": proc_info.state,
                        "type": getattr(proc_info, 'type', 'realtime'),
                        "mission_time": proc_info.mission_time.isoformat() if proc_info.mission_time else None,
                        
                        # Configuration
                        "config": {
                            "persistent": getattr(proc_info, 'persistent', True),
                            "protected": getattr(proc_info, 'protected', False),
                            "synchronous": getattr(proc_info, 'synchronous', False),
                            "checkCommandClearance": getattr(proc_info, 'checkCommandClearance', True),
                        },
                        
                        # Replay information
                        "replay": {
                            "is_replay": getattr(proc_info, 'replay', False),
                            "start": getattr(proc_info, 'replayStart', None),
                            "stop": getattr(proc_info, 'replayStop', None),
                            "state": getattr(proc_info, 'replayState', None),
                            "speed": getattr(proc_info, 'replaySpeed', None),
                        },
                        
                        # Ownership and services
                        "owner": getattr(proc_info, 'owner', None),
                        "creator": getattr(proc_info, 'creator', None),
                        "services": list(getattr(proc_info, 'services', [])),
                        
                        # Statistics
                        "statistics": {
                            "tm_stats": getattr(proc_info, 'tmStats', {}),
                            "tc_stats": getattr(proc_info, 'tcStats', {}),
                            "last_updated": getattr(proc_info, 'lastUpdated', None),
                        },
                        
                        # Additional info
                        "acknowledgments": getattr(proc_info, 'acknowledgments', []),
                        "alarms": getattr(proc_info, 'alarmSequenceCount', 0),
                    }
                    
                    # Remove empty replay section if not a replay processor
                    if not processor_details["replay"]["is_replay"]:
                        processor_details["replay"] = {"is_replay": False}
                    
                    # Clean up None values in statistics
                    if not any(processor_details["statistics"].values()):
                        processor_details["statistics"] = {}
                    
                    return processor_details
            except Exception as e:
                return self._handle_error("describe_processor", e)

        @self.tool()
        async def delete_processor(
            processor: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Delete a processor.

            Args:
                processor: Processor name to delete
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with self.client_manager.get_client() as client:
                    target_instance = instance or self.config.instance
                    
                    # First check if processor exists
                    proc_exists = False
                    for proc in client.list_processors(target_instance):
                        if proc.name == processor:
                            proc_exists = True
                            break
                    
                    if not proc_exists:
                        return self._handle_error(
                            "delete_processor",
                            Exception(f"Processor '{processor}' not found in instance '{target_instance}'")
                        )
                    
                    # Delete the processor
                    client.delete_processor(target_instance, processor)
                    
                    return {
                        "success": True,
                        "processor": processor,
                        "instance": target_instance,
                        "message": f"Processor '{processor}' deleted successfully",
                    }
            except Exception as e:
                return self._handle_error("delete_processor", e)


    def _register_processor_resources(self) -> None:
        """Register processor-specific resources."""
        
        @self.resource("processors://list")
        async def list_processors_resource() -> str:
            """Get a summary of all processors."""
            try:
                async with self.client_manager.get_client() as client:
                    lines = ["Yamcs Processors:"]
                    
                    # Group processors by instance
                    instances_processors = {}
                    
                    # Get all instances first
                    for inst in client.list_instances():
                        processors = list(client.list_processors(inst.name))
                        if processors:
                            instances_processors[inst.name] = processors
                    
                    # Display processors grouped by instance
                    for instance_name, processors in instances_processors.items():
                        if processors:
                            lines.append(f"\n  Instance: {instance_name}")
                            for proc in processors:
                                proc_type = getattr(proc, 'type', 'realtime')
                                replay_info = " (replay)" if getattr(proc, 'replay', False) else ""
                                time_info = ""
                                if proc.mission_time:
                                    time_info = f" @ {proc.mission_time.isoformat()}"
                                
                                lines.append(
                                    f"    - {proc.name}: {proc.state} [{proc_type}{replay_info}]{time_info}"
                                )
                    
                    if not instances_processors:
                        lines.append("  No processors found")
                    
                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"