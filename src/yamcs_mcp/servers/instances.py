"""Instance management server for Yamcs MCP."""

from typing import Any

from ..client import YamcsClientManager
from ..config import YamcsConfig
from .base_server import BaseYamcsServer


class InstancesServer(BaseYamcsServer):
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
        super().__init__("Instances", client_manager, config)
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
                        processor_count = len(
                            list(client.list_processors(instance.name))
                        )

                        instances.append(
                            {
                                "name": instance.name,
                                "state": instance.state,
                                "mission_time": instance.mission_time.isoformat()
                                if instance.mission_time
                                else None,
                                "processors": processor_count,
                            }
                        )

                    return {
                        "count": len(instances),
                        "instances": instances,
                    }
            except Exception as e:
                return self._handle_error("list_instances", e)

        @self.tool()
        async def describe_instance(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get comprehensive information about a Yamcs instance.

            Args:
                instance: Instance name (uses default if not specified)

            Returns:
                dict: Complete instance info (status, services, processors, etc.)
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
                        return self._handle_error(
                            "describe_instance",
                            Exception(f"Instance '{instance_name}' not found"),
                        )

                    # Get processors for this instance
                    processors = []
                    for proc in client.list_processors(inst.name):
                        processors.append(
                            {
                                "name": proc.name,
                                "state": proc.state,
                                "type": getattr(proc, "type", "realtime"),
                                "persistent": getattr(proc, "persistent", False),
                                "time": proc.time.isoformat()
                                if hasattr(proc, "time") and proc.time
                                else None,
                                "replay": getattr(proc, "replay", False),
                            }
                        )

                    # Get services for this instance
                    services = []
                    for service in client.list_services(inst.name):
                        services.append(
                            {
                                "name": service.name,
                                "state": service.state,
                                "class": getattr(service, "class_name", None),
                            }
                        )

                    # Build comprehensive instance information
                    instance_info = {
                        "name": inst.name,
                        "state": inst.state,
                        "mission_time": inst.mission_time.isoformat()
                        if inst.mission_time
                        else None,
                        # Basic information
                        "labels": getattr(inst, "labels", {}),
                        "capabilities": list(getattr(inst, "capabilities", [])),
                        "failure_cause": getattr(inst, "failure_cause", None),
                        # Template information
                        "template": getattr(inst, "template", None),
                        "template_args": getattr(inst, "template_args", {}),
                        "template_available": getattr(inst, "template_available", None),
                        "template_changed": getattr(inst, "template_changed", None),
                        # Components
                        "processors": {
                            "count": len(processors),
                            "items": processors,
                        },
                        "services": {
                            "count": len(services),
                            "items": services,
                        },
                        # Mission database info
                        "mission_database": {
                            "name": getattr(inst, "mission_database", {}).get(
                                "name", None
                            )
                            if hasattr(inst, "mission_database")
                            else None,
                            "version": getattr(inst, "mission_database", {}).get(
                                "version", None
                            )
                            if hasattr(inst, "mission_database")
                            else None,
                        },
                    }

                    # Remove empty/None fields for cleaner output
                    if not instance_info["template"]:
                        del instance_info["template"]
                        del instance_info["template_args"]
                        del instance_info["template_available"]
                        del instance_info["template_changed"]

                    if not instance_info["failure_cause"]:
                        del instance_info["failure_cause"]

                    if not any(instance_info["mission_database"].values()):
                        del instance_info["mission_database"]

                    return instance_info
            except Exception as e:
                return self._handle_error("describe_instance", e)

        @self.tool()
        async def start_instance(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Start a Yamcs instance.

            Args:
                instance: Instance name (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with self.client_manager.get_client() as client:
                    instance_name = instance or self.config.instance
                    client.start_instance(instance_name)

                    return {
                        "success": True,
                        "instance": instance_name,
                        "message": f"Instance '{instance_name}' started",
                    }
            except Exception as e:
                return self._handle_error("start_instance", e)

        @self.tool()
        async def stop_instance(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Stop a Yamcs instance.

            Args:
                instance: Instance name (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with self.client_manager.get_client() as client:
                    instance_name = instance or self.config.instance
                    client.stop_instance(instance_name)

                    return {
                        "success": True,
                        "instance": instance_name,
                        "message": f"Instance '{instance_name}' stopped",
                    }
            except Exception as e:
                return self._handle_error("stop_instance", e)

    def _register_instance_resources(self) -> None:
        """Register instance-specific resources."""

        @self.resource("instances://list")
        async def list_instances_resource() -> str:
            """Get a summary of all instances."""
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
