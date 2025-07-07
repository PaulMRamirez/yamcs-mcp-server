"""Alarms server for Yamcs MCP."""

from datetime import datetime
from typing import Any

from ..client import YamcsClientManager
from .base_server import BaseYamcsServer
from ..config import YamcsConfig


class AlarmsServer(BaseYamcsServer):
    """Alarms server for managing Yamcs alarms."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Alarms server.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("Alarms", client_manager, config)
        self._register_alarm_tools()
        self._register_alarm_resources()

    def _register_alarm_tools(self) -> None:
        """Register alarm-specific tools."""
        
        @self.tool()
        async def list_alarms(
            processor: str = "realtime",
            include_pending: bool = False,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """List active alarms on a processor.

            Args:
                processor: Processor name (default: realtime)
                include_pending: Include pending alarms
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: List of active alarms
            """
            try:
                async with self.client_manager.get_client() as client:
                    proc = client.get_processor(
                        instance=instance or self.config.instance,
                        processor=processor,
                    )
                    
                    alarms = []
                    # Count alarm states (independent counts)
                    total_count = 0
                    acknowledged_count = 0
                    unacknowledged_count = 0
                    shelved_count = 0
                    ok_count = 0
                    latched_count = 0
                    
                    for alarm in proc.list_alarms(include_pending=include_pending):
                        alarm_info = {
                            "name": alarm.name,
                            "sequence_number": alarm.sequence_number,
                            "trigger_time": alarm.trigger_time.isoformat() if alarm.trigger_time else None,
                            "severity": alarm.severity,
                            "violation_count": alarm.violation_count,
                            "count": alarm.count,
                            "is_acknowledged": alarm.is_acknowledged,
                            "is_ok": alarm.is_ok,
                            "is_shelved": getattr(alarm, 'is_shelved', False),
                        }
                        
                        # Update counts (independent)
                        total_count += 1
                        if alarm.is_acknowledged:
                            acknowledged_count += 1
                        else:
                            unacknowledged_count += 1
                        if getattr(alarm, 'is_shelved', False):
                            shelved_count += 1
                        if alarm.is_ok:
                            ok_count += 1
                        if getattr(alarm, 'is_latched', False):
                            latched_count += 1
                        
                        alarms.append(alarm_info)
                    
                    return {
                        "instance": instance or self.config.instance,
                        "processor": processor,
                        "summary": {
                            "total": total_count,
                            "acknowledged": acknowledged_count,
                            "unacknowledged": unacknowledged_count,
                            "shelved": shelved_count,
                            "ok": ok_count,
                            "latched": latched_count,
                        },
                        "include_pending": include_pending,
                        "alarms": alarms,
                    }
            except Exception as e:
                return self._handle_error("list_alarms", e)

        @self.tool()
        async def describe_alarm(
            alarm: str,
            processor: str = "realtime",
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get detailed information about a specific alarm.

            Args:
                alarm: Alarm name (parameter name)
                processor: Processor name (default: realtime)
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Detailed alarm information
            """
            try:
                async with self.client_manager.get_client() as client:
                    proc = client.get_processor(
                        instance=instance or self.config.instance,
                        processor=processor,
                    )
                    
                    # List all alarms and find the one matching the name
                    for alarm_obj in proc.list_alarms():
                        if alarm_obj.name == alarm:
                            # Build alarm details based on documented Alarm model attributes
                            alarm_info = {
                                "name": alarm_obj.name,
                                "sequence_number": alarm_obj.sequence_number,
                                "trigger_time": alarm_obj.trigger_time.isoformat() if alarm_obj.trigger_time else None,
                                "update_time": alarm_obj.update_time.isoformat() if alarm_obj.update_time else None,
                                "severity": alarm_obj.severity,
                                "violation_count": alarm_obj.violation_count,
                                "count": alarm_obj.count,
                                "is_acknowledged": alarm_obj.is_acknowledged,
                                "is_ok": alarm_obj.is_ok,
                                "is_process_ok": getattr(alarm_obj, 'is_process_ok', None),
                                "is_latched": getattr(alarm_obj, 'is_latched', None),
                                "is_latching": getattr(alarm_obj, 'is_latching', None),
                                "is_shelved": getattr(alarm_obj, 'is_shelved', None),
                            }
                            
                            # Add acknowledge info if present
                            if hasattr(alarm_obj, 'acknowledge_time') and alarm_obj.acknowledge_time:
                                alarm_info["acknowledge_time"] = alarm_obj.acknowledge_time.isoformat()
                            if hasattr(alarm_obj, 'acknowledged_by'):
                                alarm_info["acknowledged_by"] = alarm_obj.acknowledged_by
                            if hasattr(alarm_obj, 'acknowledge_message'):
                                alarm_info["acknowledge_message"] = alarm_obj.acknowledge_message
                            
                            return {
                                "instance": instance or self.config.instance,
                                "processor": processor,
                                "alarm": alarm_info,
                            }
                    
                    # Alarm not found
                    return {
                        "error": True,
                        "message": f"Alarm '{alarm}' not found on processor '{processor}'",
                        "instance": instance or self.config.instance,
                        "processor": processor,
                    }
                    
            except Exception as e:
                return self._handle_error("describe_alarm", e)

        @self.tool()
        async def acknowledge_alarm(
            alarm: str,
            sequence_number: int,
            comment: str | None = None,
            processor: str = "realtime",
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Acknowledge a specific alarm.

            Args:
                alarm: Alarm name
                sequence_number: Alarm sequence number
                comment: Optional acknowledgment comment
                processor: Processor name (default: realtime)
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
                    
                    proc.acknowledge_alarm(alarm, sequence_number, comment=comment)
                    
                    return {
                        "success": True,
                        "alarm": alarm,
                        "sequence_number": sequence_number,
                        "processor": processor,
                        "instance": instance or self.config.instance,
                        "message": f"Alarm '{alarm}' (seq: {sequence_number}) acknowledged",
                    }
            except Exception as e:
                return self._handle_error("acknowledge_alarm", e)

        @self.tool()
        async def shelve_alarm(
            alarm: str,
            sequence_number: int,
            comment: str | None = None,
            processor: str = "realtime",
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Shelve (temporarily suspend) an alarm.

            Args:
                alarm: Alarm name
                sequence_number: Alarm sequence number
                comment: Optional shelve comment
                processor: Processor name (default: realtime)
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
                    
                    proc.shelve_alarm(alarm, sequence_number, comment=comment)
                    
                    return {
                        "success": True,
                        "alarm": alarm,
                        "sequence_number": sequence_number,
                        "processor": processor,
                        "instance": instance or self.config.instance,
                        "message": f"Alarm '{alarm}' (seq: {sequence_number}) shelved",
                    }
            except Exception as e:
                return self._handle_error("shelve_alarm", e)

        @self.tool()
        async def unshelve_alarm(
            alarm: str,
            sequence_number: int,
            comment: str | None = None,
            processor: str = "realtime",
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Unshelve (reactivate) a previously shelved alarm.

            Args:
                alarm: Alarm name
                sequence_number: Alarm sequence number
                comment: Optional unshelve comment
                processor: Processor name (default: realtime)
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
                    
                    proc.unshelve_alarm(alarm, sequence_number, comment=comment)
                    
                    return {
                        "success": True,
                        "alarm": alarm,
                        "sequence_number": sequence_number,
                        "processor": processor,
                        "instance": instance or self.config.instance,
                        "message": f"Alarm '{alarm}' (seq: {sequence_number}) unshelved",
                    }
            except Exception as e:
                return self._handle_error("unshelve_alarm", e)

        @self.tool()
        async def clear_alarm(
            alarm: str,
            sequence_number: int,
            comment: str | None = None,
            processor: str = "realtime",
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Clear a specific alarm.

            Args:
                alarm: Alarm name
                sequence_number: Alarm sequence number
                comment: Optional clear comment
                processor: Processor name (default: realtime)
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
                    
                    proc.clear_alarm(alarm, sequence_number, comment=comment)
                    
                    return {
                        "success": True,
                        "alarm": alarm,
                        "sequence_number": sequence_number,
                        "processor": processor,
                        "instance": instance or self.config.instance,
                        "message": f"Alarm '{alarm}' (seq: {sequence_number}) cleared",
                    }
            except Exception as e:
                return self._handle_error("clear_alarm", e)

        @self.tool()
        async def read_log(
            name: str | None = None,
            start: str | None = None,
            stop: str | None = None,
            lines: int = 10,
            descending: bool = True,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Read alarm history from the archive.

            Args:
                name: Optional alarm name filter
                start: Start time (ISO 8601 format or 'now', 'today', 'yesterday')
                stop: Stop time (ISO 8601 format or 'now', 'today', 'yesterday')
                lines: Maximum number of alarms to return (default: 10)
                descending: Sort order, True for most recent first (default: True)
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Historical alarm records
            """
            try:
                async with self.client_manager.get_client() as client:
                    archive = client.get_archive(instance or self.config.instance)
                    
                    # Parse time strings
                    start_dt = None
                    stop_dt = None
                    
                    if start:
                        if start == "now":
                            start_dt = datetime.now()
                        elif start == "today":
                            start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        elif start == "yesterday":
                            start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                            start_dt = start_dt.replace(day=start_dt.day - 1)
                        else:
                            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    
                    if stop:
                        if stop == "now":
                            stop_dt = datetime.now()
                        elif stop == "today":
                            stop_dt = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
                        elif stop == "yesterday":
                            stop_dt = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
                            stop_dt = stop_dt.replace(day=stop_dt.day - 1)
                        else:
                            stop_dt = datetime.fromisoformat(stop.replace('Z', '+00:00'))
                    
                    # Get alarms from archive
                    alarms = []
                    count = 0
                    
                    for alarm in archive.list_alarms(
                        name=name,
                        start=start_dt,
                        stop=stop_dt,
                        descending=descending,
                    ):
                        if count >= lines:
                            break
                            
                        alarm_info = {
                            "name": alarm.name,
                            "sequence_number": alarm.sequence_number,
                            "trigger_time": alarm.trigger_time.isoformat() if alarm.trigger_time else None,
                            "update_time": alarm.update_time.isoformat() if alarm.update_time else None,
                            "severity": alarm.severity,
                            "violation_count": alarm.violation_count,
                            "count": alarm.count,
                            "is_acknowledged": alarm.is_acknowledged,
                            "is_ok": alarm.is_ok,
                            "is_shelved": getattr(alarm, 'is_shelved', False),
                        }
                        
                        # Add acknowledge info if documented attributes are present
                        if alarm.is_acknowledged:
                            if hasattr(alarm, 'acknowledge_time') and alarm.acknowledge_time:
                                alarm_info["acknowledge_time"] = alarm.acknowledge_time.isoformat()
                            if hasattr(alarm, 'acknowledged_by'):
                                alarm_info["acknowledged_by"] = alarm.acknowledged_by
                            if hasattr(alarm, 'acknowledge_message'):
                                alarm_info["acknowledge_message"] = alarm.acknowledge_message
                        
                        alarms.append(alarm_info)
                        count += 1
                    
                    return {
                        "instance": instance or self.config.instance,
                        "filter": {
                            "name": name,
                            "start": start,
                            "stop": stop,
                            "descending": descending,
                        },
                        "count": len(alarms),
                        "requested_lines": lines,
                        "alarms": alarms,
                    }
            except Exception as e:
                return self._handle_error("read_log", e)

    def _register_alarm_resources(self) -> None:
        """Register alarm-specific resources."""
        
        @self.resource("alarms://list")
        async def list_alarms_resource() -> str:
            """Get a summary of active alarms across all processors."""
            try:
                async with self.client_manager.get_client() as client:
                    lines = ["Active Yamcs Alarms:"]
                    total_alarms = 0
                    total_acknowledged = 0
                    total_unacknowledged = 0
                    total_shelved = 0
                    total_ok = 0
                    total_latched = 0
                    
                    # Get all instances
                    for inst in client.list_instances():
                        instance_alarms = []
                        
                        # Get all processors for this instance
                        for proc in client.list_processors(inst.name):
                            proc_client = client.get_processor(inst.name, proc.name)
                            
                            # Get active alarms for this processor
                            proc_alarms = list(proc_client.list_alarms())
                            if proc_alarms:
                                instance_alarms.append((proc.name, proc_alarms))
                                total_alarms += len(proc_alarms)
                                
                                # Count alarm states (independent counts)
                                for alarm in proc_alarms:
                                    if alarm.is_acknowledged:
                                        total_acknowledged += 1
                                    else:
                                        total_unacknowledged += 1
                                    if getattr(alarm, 'is_shelved', False):
                                        total_shelved += 1
                                    if alarm.is_ok:
                                        total_ok += 1
                                    if getattr(alarm, 'is_latched', False):
                                        total_latched += 1
                        
                        # Display instance alarms
                        if instance_alarms:
                            lines.append(f"\n  Instance: {inst.name}")
                            for proc_name, alarms in instance_alarms:
                                lines.append(f"    Processor: {proc_name}")
                                for alarm in alarms:
                                    severity = getattr(alarm, 'severity', 'UNKNOWN')
                                    ack_status = "ACK" if alarm.is_acknowledged else "UNACK"
                                    shelved_status = " [SHELVED]" if getattr(alarm, 'is_shelved', False) else ""
                                    ok_status = " [OK]" if alarm.is_ok else ""
                                    lines.append(
                                        f"      - {alarm.name} (seq: {getattr(alarm, 'sequence_number', 'N/A')}) "
                                        f"[{severity}] {ack_status}{shelved_status}{ok_status}"
                                    )
                    
                    if total_alarms == 0:
                        lines.append("  No active alarms")
                    else:
                        lines.append(f"\n  Summary:")
                        lines.append(f"    Total: {total_alarms}")
                        lines.append(f"    Acknowledged: {total_acknowledged}")
                        lines.append(f"    Unacknowledged: {total_unacknowledged}")
                        lines.append(f"    Shelved: {total_shelved}")
                        lines.append(f"    OK: {total_ok}")
                        lines.append(f"    Latched: {total_latched}")
                    
                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"