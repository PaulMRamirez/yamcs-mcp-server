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
                                "significance": self._safe_enum_to_str(getattr(cmd, "significance", None)),
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
                            # Handle argument type - might be an enum
                            arg_type = getattr(arg, "type", "unknown")
                            arg_type = self._safe_enum_to_str(arg_type)
                            
                            arg_info = {
                                "name": arg.name,
                                "description": getattr(arg, "description", ""),
                                "type": arg_type,
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
                            "consequence_level": self._safe_enum_to_str(
                                getattr(cmd, "consequence_level", "NORMAL")
                            ),
                            "reason": getattr(cmd, "reason_for_consequence", None),
                        },
                        "constraints": getattr(cmd, "constraints", []),
                    }
            except Exception as e:
                return self._handle_error("describe_command", e)

        @self.tool()
        async def run_command(
            command: str,
            args: dict[str, Any] | str | None = None,  # Accept both dict and string
            processor: str = "realtime",
            dry_run: bool = False,
            comment: str | None = None,
            sequence_number: int | None = None,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Execute a command on Yamcs.

            To execute SWITCH_VOLTAGE_OFF with voltage_num=1, call this tool with:
            command="/YSS/SIMULATOR/SWITCH_VOLTAGE_OFF" args={"voltage_num": 1}
            
            To execute with multiple arguments:
            command="/YSS/SIMULATOR/SOME_CMD" args={"arg1": "value1", "arg2": 123}
            
            The args parameter should be a dictionary mapping argument names to values.
            If you pass a JSON string, it will be automatically parsed.

            Args:
                command: Full qualified command name like /YSS/SIMULATOR/SWITCH_VOLTAGE_OFF
                args: Dictionary of command arguments like {"voltage_num": 1} or JSON string '{"voltage_num": 1}'
                processor: Processor name, usually "realtime"
                dry_run: If true, validate without executing
                comment: Optional comment for the command
                sequence_number: Optional sequence number
                instance: Yamcs instance name

            Returns:
                dict: Command execution result with ID and status
            """
            try:
                async with self.client_manager.get_client() as client:
                    target_instance = instance or self.config.instance
                    proc_client = client.get_processor(target_instance, processor)

                    # Handle args - convert string to dict if needed
                    command_args = {}
                    if args:
                        if isinstance(args, str):
                            # Claude Desktop sometimes sends args as a JSON string
                            # Parse it to a dict
                            import json
                            try:
                                command_args = json.loads(args)
                                self.logger.info(
                                    f"Automatically parsed JSON string args for command {command}"
                                )
                            except json.JSONDecodeError as e:
                                # Try to provide helpful error message
                                return {
                                    "error": True,
                                    "message": (
                                        f"Failed to parse args as JSON. "
                                        f"Received: '{args}'. "
                                        f"Error: {e}. "
                                        f"Please ensure args is valid JSON like: "
                                        f'{{"voltage_num": 1}}'
                                    ),
                                    "operation": "run_command",
                                    "command": command,
                                }
                        elif isinstance(args, dict):
                            command_args = args
                        else:
                            return {
                                "error": True,
                                "message": f"Invalid args type: expected dict or JSON string, got {type(args).__name__}",
                                "operation": "run_command",
                                "command": command,
                            }
                    
                    # Prepare issue_command parameters
                    issue_params = {
                        "args": command_args if command_args else None,
                        "dry_run": dry_run,
                    }
                    
                    if comment is not None:
                        issue_params["comment"] = comment
                    
                    if sequence_number is not None:
                        issue_params["sequence_number"] = sequence_number

                    # Issue the command (works for both dry_run and actual execution)
                    try:
                        cmd_result = proc_client.issue_command(command, **issue_params)
                        
                        if dry_run:
                            # Dry run succeeded - command is valid
                            return {
                                "success": True,
                                "dry_run": True,
                                "command": command,
                                "processor": processor,
                                "instance": target_instance,
                                "valid": True,
                                "message": f"Command '{command}' validated successfully",
                                "comment": comment,
                            }
                        else:
                            # Actual command execution
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
                                "comment": comment,
                                "message": f"Command '{command}' issued successfully",
                            }
                    except Exception as validation_error:
                        if dry_run:
                            # Dry run failed - validation errors
                            return {
                                "success": False,
                                "dry_run": True,
                                "command": command,
                                "processor": processor,
                                "instance": target_instance,
                                "valid": False,
                                "validation_error": str(validation_error),
                                "message": f"Command validation failed: {validation_error}",
                            }
                        else:
                            # Re-raise for actual execution errors
                            raise

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
                    
                    # Use list_command_history for accessing command history
                    # Note: list_command_history doesn't accept limit parameter directly
                    try:
                        if hasattr(archive_client, 'list_command_history'):
                            # list_command_history doesn't take limit directly
                            cmd_iterator = archive_client.list_command_history(
                                start=start_time,
                                stop=stop_time,
                            )
                        else:
                            # Fallback for older versions
                            cmd_iterator = []
                    except Exception:
                        # Last resort - return empty
                        cmd_iterator = []
                    
                    for cmd_entry in cmd_iterator:
                        # Filter by command name if specified
                        cmd_name = getattr(cmd_entry, "command_name", getattr(cmd_entry, "name", None))
                        if command and cmd_name:
                            if command not in cmd_name:
                                continue
                        
                        commands.append(
                            {
                                "name": cmd_name,
                                "id": getattr(cmd_entry, "id", None),
                                "generation_time": cmd_entry.generation_time.isoformat()
                                if hasattr(cmd_entry, "generation_time") and cmd_entry.generation_time
                                else None,
                                "origin": getattr(cmd_entry, "origin", None),
                                "sequence_number": getattr(cmd_entry, "sequence_number", None),
                                "username": getattr(cmd_entry, "username", None),
                                "queue": getattr(cmd_entry, "queue", None),
                                "source": getattr(cmd_entry, "source", None),
                                "comment": getattr(cmd_entry, "comment", None),
                                "assignments": self._format_assignments(cmd_entry),
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

    def _safe_enum_to_str(self, value: Any) -> Any:
        """Safely convert enum values to strings for serialization.
        
        Args:
            value: Value that might be an enum
            
        Returns:
            String representation if enum, original value otherwise
        """
        if value is None:
            return None
        
        # Check if it's an enum (has 'name' and 'value' attributes)
        if hasattr(value, 'name') and hasattr(value, 'value'):
            return str(value.name)
        
        # Check for Yamcs-specific enum types
        if hasattr(value, '__class__'):
            class_name = str(value.__class__)
            # Handle known Yamcs enum types
            if any(enum_type in class_name for enum_type in [
                'Significance', 'ArgumentType', 'AlarmType', 'ParameterType'
            ]):
                # Try to get the string representation
                if hasattr(value, 'name'):
                    return str(value.name)
                else:
                    return str(value)
        
        return value

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

    def _format_assignments(self, cmd_entry: Any) -> dict[str, Any] | None:
        """Format command argument assignments.

        Args:
            cmd_entry: Command entry from archive

        Returns:
            dict with argument assignments or None
        """
        if not hasattr(cmd_entry, "assignments"):
            return None

        assignments = {}
        for assignment in getattr(cmd_entry, "assignments", []):
            name = getattr(assignment, "name", "unknown")
            value = getattr(assignment, "value", None)
            assignments[name] = value

        return assignments if assignments else None

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