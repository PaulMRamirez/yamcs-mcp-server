"""Mission Database (MDB) server for Yamcs MCP."""

from typing import Any

from ..client import YamcsClientManager
from ..components.base_server import BaseYamcsServer
from ..config import YamcsConfig


class MDBServer(BaseYamcsServer):
    """MDB server for accessing Yamcs Mission Database."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize MDB server.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("MDB", client_manager, config)
        self._register_mdb_tools()
        self._register_mdb_resources()

    def _register_mdb_tools(self) -> None:
        """Register MDB-specific tools."""
        
        @self.tool()
        async def list_parameters(
            instance: str | None = None,
            system: str | None = None,
            search: str | None = None,
        ) -> dict[str, Any]:
            """List parameters from the Mission Database.

            Args:
                instance: Yamcs instance (uses default if not specified)
                system: Filter by space system
                search: Search pattern for parameter names

            Returns:
                dict: List of parameters with their details
            """
            try:
                async with self.client_manager.get_client() as client:
                    mdb_client = client.get_mdb(instance or self.config.instance)

                    # Get parameters with optional filtering
                    parameters = []
                    for param in mdb_client.list_parameters():
                        # Apply filters
                        if system and not param.qualified_name.startswith(system):
                            continue
                        if search and search.lower() not in param.qualified_name.lower():
                            continue

                        parameters.append({
                            "name": param.name,
                            "qualified_name": param.qualified_name,
                            "type": param.type,
                            "units": param.units,
                            "description": param.description,
                        })

                    return {
                        "instance": instance or self.config.instance,
                        "count": len(parameters),
                        "parameters": parameters[:100],  # Limit to first 100
                    }
            except Exception as e:
                return self._handle_error("list_parameters", e)

        @self.tool()
        async def get_parameter(
            parameter: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get detailed information about a specific parameter.

            Args:
                parameter: Parameter qualified name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Parameter details
            """
            try:
                async with self.client_manager.get_client() as client:
                    mdb_client = client.get_mdb(instance or self.config.instance)

                    # Get parameter info
                    param = mdb_client.get_parameter(parameter)

                    return {
                        "name": param.name,
                        "qualified_name": param.qualified_name,
                        "alias": param.alias,
                        "type": param.type,
                        "units": param.units,
                        "description": param.description,
                        "data_source": param.data_source,
                    }
            except Exception as e:
                return self._handle_error("get_parameter", e)

        @self.tool()
        async def list_commands(
            instance: str | None = None,
            system: str | None = None,
            search: str | None = None,
        ) -> dict[str, Any]:
            """List commands from the Mission Database.

            Args:
                instance: Yamcs instance (uses default if not specified)
                system: Filter by space system
                search: Search pattern for command names

            Returns:
                dict: List of commands with their details
            """
            try:
                async with self.client_manager.get_client() as client:
                    mdb_client = client.get_mdb(instance or self.config.instance)

                    # Get commands with optional filtering
                    commands = []
                    for cmd in mdb_client.list_commands():
                        # Apply filters
                        if system and not cmd.qualified_name.startswith(system):
                            continue
                        if search and search.lower() not in cmd.qualified_name.lower():
                            continue

                        commands.append({
                            "name": cmd.name,
                            "qualified_name": cmd.qualified_name,
                            "description": cmd.description,
                            "abstract": cmd.abstract,
                        })

                    return {
                        "instance": instance or self.config.instance,
                        "count": len(commands),
                        "commands": commands[:100],  # Limit to first 100
                    }
            except Exception as e:
                return self._handle_error("list_commands", e)

        @self.tool()
        async def get_command(
            command: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get detailed information about a specific command.

            Args:
                command: Command qualified name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Command details
            """
            try:
                async with self.client_manager.get_client() as client:
                    mdb_client = client.get_mdb(instance or self.config.instance)

                    # Get command info
                    cmd = mdb_client.get_command(command)

                    # Extract arguments
                    arguments = []
                    if hasattr(cmd, 'arguments'):
                        for arg in cmd.arguments:
                            arguments.append({
                                "name": arg.name,
                                "description": arg.description,
                                "type": getattr(arg, 'type', 'unknown'),
                                "required": getattr(arg, 'required', True),
                            })

                    return {
                        "name": cmd.name,
                        "qualified_name": cmd.qualified_name,
                        "description": cmd.description,
                        "abstract": cmd.abstract,
                        "arguments": arguments,
                    }
            except Exception as e:
                return self._handle_error("get_command", e)

        @self.tool()
        async def list_space_systems(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """List space systems from the Mission Database.

            Args:
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: List of space systems
            """
            try:
                async with self.client_manager.get_client() as client:
                    mdb_client = client.get_mdb(instance or self.config.instance)

                    # Get space systems
                    space_systems = []
                    for system in mdb_client.list_space_systems():
                        space_systems.append({
                            "name": system.name,
                            "qualified_name": system.qualified_name,
                            "description": getattr(system, 'description', None),
                        })

                    return {
                        "instance": instance or self.config.instance,
                        "count": len(space_systems),
                        "space_systems": space_systems,
                    }
            except Exception as e:
                return self._handle_error("list_space_systems", e)

    def _register_mdb_resources(self) -> None:
        """Register MDB-specific resources."""
        
        @self.resource("mdb://parameters")
        async def get_parameters_summary() -> str:
            """Get a summary of available parameters."""
            try:
                async with self.client_manager.get_client() as client:
                    mdb_client = client.get_mdb(self.config.instance)
                    
                    # Count parameters by system
                    systems: dict[str, int] = {}
                    total = 0
                    
                    for param in mdb_client.list_parameters():
                        total += 1
                        # Extract system from qualified name
                        parts = param.qualified_name.split('/')
                        if len(parts) > 1:
                            system = parts[1]
                            systems[system] = systems.get(system, 0) + 1
                    
                    # Build summary
                    lines = [
                        f"Mission Database Parameters Summary ({self.config.instance}):",
                        f"Total Parameters: {total}",
                        "",
                        "Parameters by System:"
                    ]
                    
                    for system, count in sorted(systems.items()):
                        lines.append(f"  {system}: {count}")
                    
                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"

        @self.resource("mdb://commands")
        async def get_commands_summary() -> str:
            """Get a summary of available commands."""
            try:
                async with self.client_manager.get_client() as client:
                    mdb_client = client.get_mdb(self.config.instance)
                    
                    # Count commands by system
                    systems: dict[str, int] = {}
                    total = 0
                    
                    for cmd in mdb_client.list_commands():
                        total += 1
                        # Extract system from qualified name
                        parts = cmd.qualified_name.split('/')
                        if len(parts) > 1:
                            system = parts[1]
                            systems[system] = systems.get(system, 0) + 1
                    
                    # Build summary
                    lines = [
                        f"Mission Database Commands Summary ({self.config.instance}):",
                        f"Total Commands: {total}",
                        "",
                        "Commands by System:"
                    ]
                    
                    for system, count in sorted(systems.items()):
                        lines.append(f"  {system}: {count}")
                    
                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"