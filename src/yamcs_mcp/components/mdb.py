"""Mission Database (MDB) component for Yamcs MCP Server."""

from typing import Any

from ..client import YamcsClientManager
from ..config import YamcsConfig
from .base import BaseYamcsComponent


class MDBComponent(BaseYamcsComponent):
    """MDB component for accessing Yamcs Mission Database."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize MDB component.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("MDB", client_manager, config)

    def register_with_server(self, server: Any) -> None:
        """Register MDB tools and resources with the server."""
        
        @server.tool()
        async def mdb_list_parameters(
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
                            "type": param.type.eng_type if param.type else None,
                            "units": param.units,
                            "description": param.description,
                        })
                    
                    return {
                        "instance": instance or self.config.instance,
                        "count": len(parameters),
                        "parameters": parameters[:100],  # Limit to first 100
                    }
            except Exception as e:
                return self._handle_error("mdb_list_parameters", e)

        @server.tool()
        async def mdb_get_parameter(
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
                        "type": {
                            "eng_type": param.type.eng_type if param.type else None,
                            "encoding": param.type.encoding if param.type else None,
                        },
                        "units": param.units,
                        "description": param.description,
                        "data_source": param.data_source,
                        "alias": [{"name": a.name, "namespace": a.namespace} for a in param.alias],
                    }
            except Exception as e:
                return self._handle_error("mdb_get_parameter", e)

        @server.tool()
        async def mdb_list_commands(
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
                return self._handle_error("mdb_list_commands", e)

        @server.tool()
        async def mdb_get_command(
            command: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get detailed information about a specific command.

            Args:
                command: Command qualified name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Command details including arguments
            """
            try:
                async with self.client_manager.get_client() as client:
                    mdb_client = client.get_mdb(instance or self.config.instance)
                    
                    # Get command info
                    cmd = mdb_client.get_command(command)
                    
                    # Extract argument info
                    arguments = []
                    if cmd.argument:
                        for arg in cmd.argument:
                            arguments.append({
                                "name": arg.name,
                                "description": arg.description,
                                "type": arg.type,
                                "initial_value": arg.initial_value,
                            })
                    
                    return {
                        "name": cmd.name,
                        "qualified_name": cmd.qualified_name,
                        "description": cmd.description,
                        "abstract": cmd.abstract,
                        "arguments": arguments,
                        "alias": [{"name": a.name, "namespace": a.namespace} for a in cmd.alias],
                    }
            except Exception as e:
                return self._handle_error("mdb_get_command", e)

        @server.tool()
        async def mdb_list_space_systems(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """List space systems from the Mission Database.

            Args:
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Space system hierarchy
            """
            try:
                async with self.client_manager.get_client() as client:
                    mdb_client = client.get_mdb(instance or self.config.instance)
                    
                    # Get space systems
                    systems = []
                    for system in mdb_client.list_space_systems():
                        systems.append({
                            "name": system.name,
                            "qualified_name": system.qualified_name,
                            "description": system.description,
                        })
                    
                    return {
                        "instance": instance or self.config.instance,
                        "count": len(systems),
                        "space_systems": systems,
                    }
            except Exception as e:
                return self._handle_error("mdb_list_space_systems", e)

        # Register resources
        @server.resource("mdb://parameters")
        async def list_all_parameters() -> str:
            """List all parameters in the MDB."""
            result = await self.mdb_list_parameters()
            if "error" in result:
                return f"Error: {result['message']}"
            
            params = result.get("parameters", [])
            lines = [f"Parameters in {result['instance']} ({result['count']} total):"]
            for param in params[:50]:  # Show first 50
                lines.append(f"  - {param['qualified_name']} ({param['type']})")
            if result['count'] > 50:
                lines.append(f"  ... and {result['count'] - 50} more")
            
            return "\n".join(lines)

        @server.resource("mdb://commands")
        async def list_all_commands() -> str:
            """List all commands in the MDB."""
            result = await self.mdb_list_commands()
            if "error" in result:
                return f"Error: {result['message']}"
            
            commands = result.get("commands", [])
            lines = [f"Commands in {result['instance']} ({result['count']} total):"]
            for cmd in commands[:50]:  # Show first 50
                lines.append(f"  - {cmd['qualified_name']}")
            if result['count'] > 50:
                lines.append(f"  ... and {result['count'] - 50} more")
            
            return "\n".join(lines)