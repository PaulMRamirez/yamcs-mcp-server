"""Processor server for Yamcs MCP."""

from typing import Any

from ..client import YamcsClientManager
from ..components.base_server import BaseYamcsServer
from ..config import YamcsConfig


class ProcessorServer(BaseYamcsServer):
    """Processor server for managing Yamcs processors."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Processor server.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("Processor", client_manager, config)
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
        async def get_processor(
            processor: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get detailed processor information.

            Args:
                processor: Processor name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Processor details
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
                        return {
                            "error": True,
                            "message": f"Processor '{processor}' not found in instance '{target_instance}'",
                            "operation": "get_processor",
                            "component": self.component_name,
                        }
                    
                    return {
                        "name": proc_info.name,
                        "state": proc_info.state,
                        "mission_time": proc_info.mission_time.isoformat() if proc_info.mission_time else None,
                        "type": getattr(proc_info, 'type', 'realtime'),
                        "replay": getattr(proc_info, 'replay', False),
                        "persistent": getattr(proc_info, 'persistent', True),
                        "services": getattr(proc_info, 'services', []),
                        "owner": getattr(proc_info, 'owner', None),
                        "protected": getattr(proc_info, 'protected', False),
                    }
            except Exception as e:
                return self._handle_error("get_processor", e)

        @self.tool()
        async def control_processor(
            processor: str,
            action: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Control processor state.

            Args:
                processor: Processor name
                action: Action to perform (start, pause, resume, stop)
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
                    
                    # Perform the requested action
                    if action == "start":
                        proc.start()
                        message = f"Processor '{processor}' started"
                    elif action == "pause":
                        proc.pause()
                        message = f"Processor '{processor}' paused"
                    elif action == "resume":
                        proc.resume()
                        message = f"Processor '{processor}' resumed"
                    elif action == "stop":
                        proc.stop()
                        message = f"Processor '{processor}' stopped"
                    else:
                        return {
                            "error": True,
                            "message": f"Invalid action '{action}'. Must be: start, pause, resume, or stop",
                        }
                    
                    return {
                        "success": True,
                        "processor": processor,
                        "action": action,
                        "message": message,
                    }
            except Exception as e:
                return self._handle_error("control_processor", e)


    def _register_processor_resources(self) -> None:
        """Register processor-specific resources."""
        
        @self.resource("processor://status")
        async def get_processors_status() -> str:
            """Get status of all processors."""
            try:
                async with self.client_manager.get_client() as client:
                    lines = [f"Processors in {self.config.instance}:"]
                    
                    for proc in client.list_processors(self.config.instance):
                        proc_type = getattr(proc, 'type', 'realtime')
                        replay_info = " (replay)" if getattr(proc, 'replay', False) else ""
                        time_info = ""
                        if proc.mission_time:
                            time_info = f" @ {proc.mission_time.isoformat()}"
                        
                        lines.append(
                            f"  - {proc.name}: {proc.state} [{proc_type}{replay_info}]{time_info}"
                        )
                    
                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"