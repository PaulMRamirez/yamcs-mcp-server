"""Instance management server for Yamcs MCP."""

from typing import Any

from ..client import YamcsClientManager
from .base_server import BaseYamcsServer
from ..config import YamcsConfig


class InstanceServer(BaseYamcsServer):
    """Instance server for managing Yamcs instances."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Instance server.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("Instance", client_manager, config)
        self._register_instance_tools()
        self._register_instance_resources()

    def _register_instance_tools(self) -> None:
        """Register instance-specific tools."""
        
        @self.tool()
        async def list_instances() -> dict[str, Any]:
            """List all Yamcs instances.

            Returns:
                dict: List of instances
            """
            try:
                async with self.client_manager.get_client() as client:
                    instances = []
                    for instance in client.list_instances():
                        # Count processors for this instance
                        processor_count = len(list(client.list_processors(instance.name)))
                        
                        instances.append({
                            "name": instance.name,
                            "state": instance.state,
                            "mission_time": instance.mission_time.isoformat() if instance.mission_time else None,
                            "processors": processor_count,
                        })
                    
                    return {
                        "count": len(instances),
                        "instances": instances,
                    }
            except Exception as e:
                return self._handle_error("list_instances", e)

        @self.tool()
        async def get_instance(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get detailed instance information.

            Args:
                instance: Instance name (uses default if not specified)

            Returns:
                dict: Instance details
            """
            try:
                async with self.client_manager.get_client() as client:
                    # Find the instance by name
                    instance_name = instance or self.config.instance
                    inst = None
                    for i in client.list_instances():
                        if i.name == instance_name:
                            inst = i
                            break
                    
                    if not inst:
                        return self._handle_error("get_instance", Exception(f"Instance '{instance_name}' not found"))
                    
                    # Count processors for this instance
                    processor_count = len(list(client.list_processors(inst.name)))
                    
                    # Get capabilities
                    capabilities = []
                    if hasattr(inst, 'capabilities'):
                        capabilities = [cap for cap in inst.capabilities]
                    
                    return {
                        "name": inst.name,
                        "state": inst.state,
                        "mission_time": inst.mission_time.isoformat() if inst.mission_time else None,
                        "processors": processor_count,
                        "capabilities": capabilities,
                        "labels": getattr(inst, 'labels', {}),
                    }
            except Exception as e:
                return self._handle_error("get_instance", e)

        @self.tool()
        async def control_instance(
            action: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Control instance state.

            Args:
                action: Action to perform (start, stop, restart)
                instance: Instance name (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with self.client_manager.get_client() as client:
                    instance_name = instance or self.config.instance
                    
                    # Perform the requested action using client methods
                    if action == "start":
                        client.start_instance(instance_name)
                        message = f"Instance '{instance_name}' started"
                    elif action == "stop":
                        client.stop_instance(instance_name)
                        message = f"Instance '{instance_name}' stopped"
                    elif action == "restart":
                        client.restart_instance(instance_name)
                        message = f"Instance '{instance_name}' restarted"
                    else:
                        return {
                            "error": True,
                            "message": f"Invalid action '{action}'. Must be: start, stop, or restart",
                        }
                    
                    return {
                        "success": True,
                        "instance": instance_name,
                        "action": action,
                        "message": message,
                    }
            except Exception as e:
                return self._handle_error("control_instance", e)

        @self.tool()
        async def get_services(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """List services for an instance.

            Args:
                instance: Instance name (uses default if not specified)

            Returns:
                dict: List of services
            """
            try:
                async with self.client_manager.get_client() as client:
                    services = []
                    for service in client.list_services(instance or self.config.instance):
                        services.append({
                            "name": service.name,
                            "state": service.state,
                            "class": getattr(service, 'class_name', None),
                        })
                    
                    return {
                        "instance": instance or self.config.instance,
                        "count": len(services),
                        "services": services,
                    }
            except Exception as e:
                return self._handle_error("get_services", e)

    def _register_instance_resources(self) -> None:
        """Register instance-specific resources."""
        
        @self.resource("instance://status")
        async def get_instances_status() -> str:
            """Get status of all instances."""
            try:
                async with self.client_manager.get_client() as client:
                    lines = ["Yamcs Instances:"]
                    
                    for inst in client.list_instances():
                        time_info = ""
                        if inst.mission_time:
                            time_info = f" @ {inst.mission_time.isoformat()}"
                        
                        # Count processors for this instance
                        proc_count = len(list(client.list_processors(inst.name)))
                        lines.append(
                            f"  - {inst.name}: {inst.state} "
                            f"[{proc_count} processors]{time_info}"
                        )
                    
                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"

        @self.resource("instance://current")
        async def get_current_instance() -> str:
            """Get information about the current configured instance."""
            try:
                async with self.client_manager.get_client() as client:
                    # Find the instance by name
                    inst = None
                    for i in client.list_instances():
                        if i.name == self.config.instance:
                            inst = i
                            break
                    
                    if not inst:
                        return f"Error: Instance '{self.config.instance}' not found"
                    
                    lines = [
                        f"Current Instance: {inst.name}",
                        f"  State: {inst.state}",
                    ]
                    
                    if inst.mission_time:
                        lines.append(f"  Mission Time: {inst.mission_time.isoformat()}")
                    
                    # Count processors for this instance
                    proc_count = len(list(client.list_processors(inst.name)))
                    lines.append(f"  Processors: {proc_count}")
                    
                    if hasattr(inst, 'capabilities') and inst.capabilities:
                        lines.append(f"  Capabilities: {', '.join(inst.capabilities)}")
                    
                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"