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

    def register_with_server(self, server: Any) -> None:
        """Register Instance Management tools and resources with the server."""

        # Store reference to self for use in closures
        component = self

        @server.tool()
        async def instance_list_instances() -> dict[str, Any]:
            """List Yamcs instances.

            Returns:
                dict: List of instances with their status
            """
            try:
                async with component.client_manager.get_client() as client:
                    instances = []
                    for instance in client.list_instances():
                        instances.append({
                            "name": instance.name,
                            "state": instance.state,
                            "mission_time": instance.mission_time,
                            "labels": (
                                instance.labels if hasattr(instance, 'labels') else {}
                            ),
                            "template": (
                                instance.template if hasattr(instance, 'template') else None
                            ),
                            "capabilities": (
                                instance.capabilities
                                if hasattr(instance, 'capabilities')
                                else []
                            ),
                        })

                    return {
                        "count": len(instances),
                        "instances": instances,
                    }
            except Exception as e:
                return component._handle_error("instance_list_instances", e)


        @server.tool()
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
                async with component.client_manager.get_client() as client:
                    inst = client.get_instance(instance or component.config.instance)

                    return {
                        "name": inst.name,
                        "state": inst.state,
                        "mission_time": inst.mission_time,
                        "labels": (
                            inst.labels if hasattr(inst, 'labels') else {}
                        ),
                        "template": (
                            inst.template if hasattr(inst, 'template') else None
                        ),
                        "capabilities": (
                            inst.capabilities
                            if hasattr(inst, 'capabilities')
                            else []
                        ),
                        "processors": (
                            [p.name for p in inst.list_processors()]
                            if hasattr(inst, 'list_processors')
                            else []
                        ),
                    }
            except Exception as e:
                return component._handle_error("instance_get_info", e)

        @server.tool()
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
                async with component.client_manager.get_client() as client:
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
                return component._handle_error("instance_start_instance", e)

        @server.tool()
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
                async with component.client_manager.get_client() as client:
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
                return component._handle_error("instance_stop_instance", e)

        @server.tool()
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
                async with component.client_manager.get_client() as client:
                    services = []
                    for service in client.list_services(
                        instance or component.config.instance
                    ):
                        services.append({
                            "name": service.name,
                            "class": service.class_name,
                            "state": service.state,
                            "processor": (
                                service.processor
                                if hasattr(service, 'processor')
                                else None
                            ),
                        })

                    return {
                        "instance": instance or component.config.instance,
                        "count": len(services),
                        "services": services,
                    }
            except Exception as e:
                return component._handle_error("instance_list_services", e)

        @server.tool()
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
                async with component.client_manager.get_client() as client:
                    # Start service using YamcsClient method
                    client.start_service(
                        instance=instance or component.config.instance,
                        service=service,
                    )

                    return {
                        "success": True,
                        "service": service,
                        "instance": instance or component.config.instance,
                        "operation": "start",
                        "message": f"Service '{service}' started successfully",
                    }
            except Exception as e:
                return component._handle_error("instance_start_service", e)

        @server.tool()
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
                async with component.client_manager.get_client() as client:
                    # Stop service using YamcsClient method
                    client.stop_service(
                        instance=instance or component.config.instance,
                        service=service,
                    )

                    return {
                        "success": True,
                        "service": service,
                        "instance": instance or component.config.instance,
                        "operation": "stop",
                        "message": f"Service '{service}' stopped successfully",
                    }
            except Exception as e:
                return component._handle_error("instance_stop_service", e)

        # Register resources
        @server.resource("instance://list")
        async def list_all_instances() -> str:
            """List all available instances."""
            # Duplicate the logic instead of calling the tool
            try:
                async with component.client_manager.get_client() as client:
                    instances = []
                    for instance in client.list_instances():
                        instances.append({
                            "name": instance.name,
                            "state": instance.state,
                            "template": (
                                instance.template
                                if hasattr(instance, 'template')
                                else None
                            ),
                        })

                    lines = ["Yamcs Instances:"]
                    for inst in instances:
                        lines.append(
                            f"  - {inst['name']}: {inst['state']} "
                            f"(template: {inst.get('template', 'none')})"
                        )

                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"

        @server.resource("instance://services/{instance}")
        async def list_instance_services(instance: str) -> str:
            """List services for a specific instance."""
            # Duplicate the logic instead of calling the tool
            try:
                async with component.client_manager.get_client() as client:
                    services = []
                    for service in client.list_services(
                        instance or component.config.instance
                    ):
                        services.append({
                            "name": service.name,
                            "class": service.class_name,
                            "state": service.state,
                            "processor": (
                                service.processor
                                if hasattr(service, 'processor')
                                else None
                            ),
                        })

                    lines = [
                        f"Services in instance '{instance}' ({len(services)} total):"
                    ]
                    for svc in services:
                        processor_info = (
                            f" (processor: {svc['processor']})"
                            if svc.get('processor')
                            else ""
                        )
                        lines.append(
                            f"  - {svc['name']} [{svc['state']}]: "
                            f"{svc['class']}{processor_info}"
                        )

                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"
