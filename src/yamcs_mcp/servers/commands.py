"""Commands server for Yamcs MCP - handles command execution and history."""

from datetime import datetime, timedelta
from typing import Any

from ..client import YamcsClientManager
from ..config import YamcsConfig
from .base_server import BaseYamcsServer


class CommandsServer(BaseYamcsServer):
    """Commands server for executing commands and accessing command history."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Commands server.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("Commands", client_manager, config)
        self._register_command_tools()

    def _register_command_tools(self) -> None:
        """Register command execution and history tools."""

        @self.tool()
        async def list_commands(
            instance: str | None = None,
            system: str | None = None,
            search: str | None = None,
            limit: int = 100,
        ) -> dict[str, Any]:
            """List available commands for execution.

            Args:
                instance: Yamcs instance (uses default if not specified)
                system: Filter by space system (e.g., "/YSS/SIMULATOR")
                search: Search pattern for command names
                limit: Maximum commands to return (default: 100)

            Returns:
                dict: List of executable commands
            """
            try:
                async with self.client_manager.get_client() as client:
                    mdb_client = client.get_mdb(instance or self.config.instance)

                    commands = []
                    for cmd in mdb_client.list_commands():
                        # Apply filters
                        if system and not cmd.qualified_name.startswith(system):
                            continue
                        if search and search.lower() not in cmd.qualified_name.lower():
                            continue

                        commands.append(
                            {
                                "name": cmd.name,
                                "qualified_name": cmd.qualified_name,
                                "description": cmd.description,
                                "abstract": cmd.abstract,
                                "significance": getattr(cmd, "significance", None),
                            }
                        )

                    return {
                        "instance": instance or self.config.instance,
                        "count": len(commands),
                        "commands": commands[:limit],
                    }
            except Exception as e:
                return self._handle_error("list_commands", e)

        @self.tool()
        async def describe_command(
            command: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get detailed information about a command including arguments.

            Args:
                command: Command qualified name (e.g., "/YSS/SIMULATOR/SWITCH_VOLTAGE_ON")
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Complete command information with arguments
            """
            try:
                async with self.client_manager.get_client() as client:
                    mdb_client = client.get_mdb(instance or self.config.instance)

                    # Get command info
                    cmd = mdb_client.get_command(command)

                    # Extract arguments with full details
                    arguments = []
                    if hasattr(cmd, "arguments"):
                        for arg in cmd.arguments:
                            arg_info = {
                                "name": arg.name,
                                "description": getattr(arg, "description", ""),
                                "type": getattr(arg, "type", "unknown"),
                                "required": getattr(arg, "required", True),
                                "initial_value": getattr(arg, "initial_value", None),
                            }
                            
                            # Add range constraints if present
                            if hasattr(arg, "range_min") or hasattr(arg, "range_max"):
                                arg_info["valid_range"] = {
                                    "min": getattr(arg, "range_min", None),
                                    "max": getattr(arg, "range_max", None),
                                }
                            
                            arguments.append(arg_info)

                    return {
                        "name": cmd.name,
                        "qualified_name": cmd.qualified_name,
                        "description": cmd.description,
                        "abstract": cmd.abstract,
                        "arguments": arguments,
                        "significance": {
                            "consequence_level": getattr(cmd, "consequence_level", "NORMAL"),
                            "reason": getattr(cmd, "reason_for_consequence", None),
                        },
                        "constraints": getattr(cmd, "constraints", []),
                    }
            except Exception as e:
                return self._handle_error("describe_command", e)

        @self.tool()
        async def run_command(
            command: str,
            args: dict[str, Any] | None = None,
            processor: str = "realtime",
            dry_run: bool = False,
            sequence_number: int | None = None,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Execute a command on Yamcs.

            Args:
                command: Command qualified name to execute
                args: Command arguments as key-value pairs
                processor: Target processor (default: "realtime")
                dry_run: Validate command without execution (default: False)
                sequence_number: Optional command sequence number
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Command execution result with ID and status
            """
            try:
                async with self.client_manager.get_client() as client:
                    target_instance = instance or self.config.instance
                    proc_client = client.get_processor(target_instance, processor)

                    # Build command arguments
                    command_args = args or {}
                    
                    # Prepare options
                    issue_options = {
                        "args": command_args,
                        "dry_run": dry_run,
                    }
                    
                    if sequence_number is not None:
                        issue_options["sequence_number"] = sequence_number

                    # Issue the command
                    if dry_run:
                        # For dry run, validate the command
                        result = proc_client.validate_command(command, **command_args)
                        return {
                            "success": True,
                            "dry_run": True,
                            "command": command,
                            "processor": processor,
                            "instance": target_instance,
                            "valid": not bool(result),  # Empty result means valid
                            "validation_messages": result if result else "Command is valid",
                            "message": f"Command '{command}' validated successfully"
                            if not result
                            else f"Command validation found issues: {result}",
                        }
                    else:
                        # Execute the command
                        cmd_result = proc_client.issue_command(command, **command_args)
                        
                        return {
                            "success": True,
                            "dry_run": False,
                            "command": command,
                            "processor": processor,
                            "instance": target_instance,
                            "command_id": cmd_result.id if hasattr(cmd_result, "id") else None,
                            "generation_time": cmd_result.generation_time.isoformat()
                            if hasattr(cmd_result, "generation_time")
                            else None,
                            "origin": getattr(cmd_result, "origin", None),
                            "sequence_number": getattr(cmd_result, "sequence_number", None),
                            "message": f"Command '{command}' issued successfully",
                        }

            except Exception as e:
                return self._handle_error("run_command", e)

        @self.tool()
        async def read_log(
            lines: int = 10,
            since: str | None = None,
            until: str | None = None,
            command: str | None = None,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Read command execution history.

            Args:
                lines: Maximum number of commands to return (default: 10)
                since: Start time (ISO 8601 or 'today', 'yesterday', 'now')
                until: End time (ISO 8601 or 'today', 'yesterday', 'now')
                command: Filter by command name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: List of executed commands with status
            """
            try:
                async with self.client_manager.get_client() as client:
                    target_instance = instance or self.config.instance
                    archive_client = client.get_archive(target_instance)

                    # Parse time filters
                    start_time = self._parse_time(since) if since else None
                    stop_time = self._parse_time(until) if until else None

                    # Query command history
                    commands = []
                    count = 0
                    
                    # List commands from archive
                    cmd_iterator = archive_client.list_commands(
                        start=start_time,
                        stop=stop_time,
                        limit=lines,
                    )
                    
                    for cmd_entry in cmd_iterator:
                        # Apply command name filter if specified
                        if command and command not in cmd_entry.name:
                            continue
                        
                        commands.append(
                            {
                                "name": cmd_entry.name,
                                "generation_time": cmd_entry.generation_time.isoformat()
                                if cmd_entry.generation_time
                                else None,
                                "origin": getattr(cmd_entry, "origin", None),
                                "sequence_number": getattr(cmd_entry, "sequence_number", None),
                                "username": getattr(cmd_entry, "username", None),
                                "queue": getattr(cmd_entry, "queue", None),
                                "source": getattr(cmd_entry, "source", None),
                                "binary": getattr(cmd_entry, "binary", None),
                                "unprocessed_binary": getattr(cmd_entry, "unprocessed_binary", None),
                                "acknowledge": self._format_acknowledge_info(cmd_entry),
                            }
                        )
                        
                        count += 1
                        if count >= lines:
                            break

                    return {
                        "instance": target_instance,
                        "filter": {
                            "lines": lines,
                            "since": since,
                            "until": until,
                            "command": command,
                        },
                        "count": len(commands),
                        "commands": commands,
                    }

            except Exception as e:
                return self._handle_error("read_log", e)

    def _parse_time(self, time_str: str) -> datetime | None:
        """Parse time string to datetime.

        Args:
            time_str: Time string (ISO format or special values)

        Returns:
            datetime object or None
        """
        if not time_str:
            return None

        # Handle special values
        now = datetime.utcnow()
        special_times = {
            "now": now,
            "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
            "yesterday": now.replace(hour=0, minute=0, second=0, microsecond=0)
            - timedelta(days=1),
            "tomorrow": now.replace(hour=0, minute=0, second=0, microsecond=0)
            + timedelta(days=1),
        }

        # Check for UTC suffix
        if time_str.endswith("UTC"):
            time_str = time_str[:-3].strip()

        # Return special time if matched
        if time_str in special_times:
            return special_times[time_str]

        # Try to parse ISO format
        try:
            return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        except ValueError:
            # Return None if parsing fails
            return None

    def _format_acknowledge_info(self, cmd_entry: Any) -> dict[str, Any] | None:
        """Format command acknowledgment information.

        Args:
            cmd_entry: Command entry from archive

        Returns:
            dict with acknowledgment info or None
        """
        if not hasattr(cmd_entry, "acknowledgments"):
            return None

        ack_info = {}
        for ack in getattr(cmd_entry, "acknowledgments", []):
            ack_name = getattr(ack, "name", "unknown")
            ack_info[ack_name] = {
                "status": getattr(ack, "status", None),
                "time": getattr(ack, "time", None),
                "message": getattr(ack, "message", None),
            }

        return ack_info if ack_info else None