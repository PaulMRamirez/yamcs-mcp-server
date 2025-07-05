"""Instance Management component for Yamcs MCP Server."""

from typing import Any

from ..client import YamcsClientManager
from ..config import YamcsConfig
from .base import BaseYamcsComponent


class InstanceManagementComponent(BaseYamcsComponent):
    """Instance Management component for Yamcs instance and service control."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Instance Management component.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("InstanceManagement", client_manager, config)

    def _register_tools(self) -> None:
        """Register Instance Management-specific tools."""
        
        @self.tool()
        async def instance_list_instances(self) -> dict[str, Any]:
            """List Yamcs instances.

            Returns:
                dict: List of instances with their status
            """
            try:
                async with self.client_manager.get_client() as client:
                    instances = []
                    for instance in client.list_instances():
                        instances.append({
                            "name": instance.name,
                            "state": instance.state,
                            "mission_time": instance.mission_time,
                            "labels": instance.labels if hasattr(instance, 'labels') else {},
                            "template": instance.template if hasattr(instance, 'template') else None,
                            "capabilities": instance.capabilities if hasattr(instance, 'capabilities') else [],
                        })
                    
                    return {
                        "count": len(instances),
                        "instances": instances,
                    }
            except Exception as e:
                return self._handle_error("instance_list_instances", e)

        @self.tool()
        async def instance_get_info(
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
                    inst = client.get_instance(instance or self.config.instance)
                    
                    return {
                        "name": inst.name,
                        "state": inst.state,
                        "mission_time": inst.mission_time,
                        "labels": inst.labels if hasattr(inst, 'labels') else {},
                        "template": inst.template if hasattr(inst, 'template') else None,
                        "capabilities": inst.capabilities if hasattr(inst, 'capabilities') else [],
                        "processors": [p.name for p in inst.list_processors()] if hasattr(inst, 'list_processors') else [],
                    }
            except Exception as e:
                return self._handle_error("instance_get_info", e)

        @self.tool()
        async def instance_start_instance(
            instance: str,
        ) -> dict[str, Any]:
            """Start a Yamcs instance.

            Args:
                instance: Instance name

            Returns:
                dict: Operation result
            """
            try:
                async with self.client_manager.get_client() as client:
                    inst = client.get_instance(instance)
                    
                    # Start instance
                    inst.start()
                    
                    return {
                        "success": True,
                        "instance": instance,
                        "operation": "start",
                        "message": f"Instance '{instance}' started successfully",
                    }
            except Exception as e:
                return self._handle_error("instance_start_instance", e)

        @self.tool()
        async def instance_stop_instance(
            instance: str,
        ) -> dict[str, Any]:
            """Stop a Yamcs instance.

            Args:
                instance: Instance name

            Returns:
                dict: Operation result
            """
            try:
                async with self.client_manager.get_client() as client:
                    inst = client.get_instance(instance)
                    
                    # Stop instance
                    inst.stop()
                    
                    return {
                        "success": True,
                        "instance": instance,
                        "operation": "stop",
                        "message": f"Instance '{instance}' stopped successfully",
                    }
            except Exception as e:
                return self._handle_error("instance_stop_instance", e)

        @self.tool()
        async def instance_list_services(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """List services for an instance.

            Args:
                instance: Instance name (uses default if not specified)

            Returns:
                dict: List of services with their status
            """
            try:
                async with self.client_manager.get_client() as client:
                    services = []
                    for service in client.list_services(instance or self.config.instance):
                        services.append({
                            "name": service.name,
                            "class": service.class_name,
                            "state": service.state,
                            "processor": service.processor if hasattr(service, 'processor') else None,
                        })
                    
                    return {
                        "instance": instance or self.config.instance,
                        "count": len(services),
                        "services": services,
                    }
            except Exception as e:
                return self._handle_error("instance_list_services", e)

        @self.tool()
        async def instance_start_service(
            service: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Start a service.

            Args:
                service: Service name
                instance: Instance name (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with self.client_manager.get_client() as client:
                    svc = client.get_service(
                        instance=instance or self.config.instance,
                        service=service,
                    )
                    
                    # Start service
                    svc.start()
                    
                    return {
                        "success": True,
                        "service": service,
                        "instance": instance or self.config.instance,
                        "operation": "start",
                        "message": f"Service '{service}' started successfully",
                    }
            except Exception as e:
                return self._handle_error("instance_start_service", e)

        @self.tool()
        async def instance_stop_service(
            service: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Stop a service.

            Args:
                service: Service name
                instance: Instance name (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with self.client_manager.get_client() as client:
                    svc = client.get_service(
                        instance=instance or self.config.instance,
                        service=service,
                    )
                    
                    # Stop service
                    svc.stop()
                    
                    return {
                        "success": True,
                        "service": service,
                        "instance": instance or self.config.instance,
                        "operation": "stop",
                        "message": f"Service '{service}' stopped successfully",
                    }
            except Exception as e:
                return self._handle_error("instance_stop_service", e)

    def _register_resources(self) -> None:
        """Register Instance Management-specific resources."""
        
        @self.resource("instance://list")
        async def list_all_instances() -> str:
            """List all available instances."""
            result = await self.instance_list_instances()
            if "error" in result:
                return f"Error: {result['message']}"
            
            lines = ["Yamcs Instances:"]
            for inst in result.get("instances", []):
                lines.append(
                    f"  - {inst['name']}: {inst['state']} "
                    f"(template: {inst.get('template', 'none')})"
                )
            
            return "\n".join(lines)

        @self.resource("instance://services/{instance}")
        async def list_instance_services(instance: str) -> str:
            """List services for a specific instance."""
            result = await self.instance_list_services(instance=instance)
            if "error" in result:
                return f"Error: {result['message']}"
            
            lines = [f"Services in instance '{instance}' ({result['count']} total):"]
            for svc in result.get("services", []):
                processor_info = f" (processor: {svc['processor']})" if svc.get('processor') else ""
                lines.append(
                    f"  - {svc['name']} [{svc['state']}]: {svc['class']}{processor_info}"
                )
            
            return "\n".join(lines)