"""Link Management component for Yamcs MCP Server."""

from typing import Any

from ..client import YamcsClientManager
from ..config import YamcsConfig
from .base import BaseYamcsComponent


class LinkManagementComponent(BaseYamcsComponent):
    """Link Management component for data link operations."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Link Management component.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("LinkManagement", client_manager, config)

    def register_with_server(self, server: Any) -> None:
        """Register Link Management tools and resources with the server."""
        
        # Store reference to self for use in closures
        component = self
        
        @server.tool()
        async def link_list_links(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """List all data links.

            Args:
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: List of links with their status
            """
            try:
                async with component.client_manager.get_client() as client:
                    links = []
                    for link in client.list_links(instance or component.config.instance):
                        links.append({
                            "name": link.name,
                            "type": getattr(link, 'type', None),
                            "status": link.status,
                            "disabled": getattr(link, 'disabled', False),
                            "parent": getattr(link, 'parent_name', None),
                            "data_in_count": getattr(link, 'data_in_count', 0),
                            "data_out_count": getattr(link, 'data_out_count', 0),
                        })
                    
                    return {
                        "instance": instance or component.config.instance,
                        "count": len(links),
                        "links": links,
                    }
            except Exception as e:
                return component._handle_error("link_list_links", e)

        @server.tool()
        async def link_get_status(
            link: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get detailed link status.

            Args:
                link: Link name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Link status information
            """
            try:
                async with component.client_manager.get_client() as client:
                    link_obj = client.get_link(
                        instance=instance or component.config.instance,
                        link=link,
                    )
                    
                    return {
                        "name": link_obj.name,
                        "type": getattr(link_obj, 'type', None),
                        "status": link_obj.status,
                        "disabled": getattr(link_obj, 'disabled', False),
                        "statistics": {
                            "data_in_count": getattr(link_obj, 'data_in_count', 0),
                            "data_out_count": getattr(link_obj, 'data_out_count', 0),
                            "last_data_in": getattr(link_obj, 'last_data_in_time', None),
                            "last_data_out": getattr(link_obj, 'last_data_out_time', None),
                        },
                        "details": getattr(link_obj, 'detail_status', None),
                    }
            except Exception as e:
                return component._handle_error("link_get_status", e)

        @server.tool()
        async def link_enable_link(
            link: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Enable a data link.

            Args:
                link: Link name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with component.client_manager.get_client() as client:
                    link_obj = client.get_link(
                        instance=instance or component.config.instance,
                        link=link,
                    )
                    
                    # Enable the link
                    link_obj.enable()
                    
                    return {
                        "success": True,
                        "link": link,
                        "operation": "enable",
                        "message": f"Link '{link}' enabled successfully",
                    }
            except Exception as e:
                return component._handle_error("link_enable_link", e)

        @server.tool()
        async def link_disable_link(
            link: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Disable a data link.

            Args:
                link: Link name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with component.client_manager.get_client() as client:
                    link_obj = client.get_link(
                        instance=instance or component.config.instance,
                        link=link,
                    )
                    
                    # Disable the link
                    link_obj.disable()
                    
                    return {
                        "success": True,
                        "link": link,
                        "operation": "disable",
                        "message": f"Link '{link}' disabled successfully",
                    }
            except Exception as e:
                return component._handle_error("link_disable_link", e)

        @server.tool()
        async def link_reset_link(
            link: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Reset a data link.

            Args:
                link: Link name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with component.client_manager.get_client() as client:
                    link_obj = client.get_link(
                        instance=instance or component.config.instance,
                        link=link,
                    )
                    
                    # Reset counters
                    link_obj.reset_counters()
                    
                    return {
                        "success": True,
                        "link": link,
                        "operation": "reset",
                        "message": f"Link '{link}' counters reset successfully",
                    }
            except Exception as e:
                return component._handle_error("link_reset_link", e)

        @server.tool()
        async def link_get_statistics(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get statistics for all links.

            Args:
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Link statistics summary
            """
            try:
                async with component.client_manager.get_client() as client:
                    stats = {
                        "total_links": 0,
                        "enabled_links": 0,
                        "disabled_links": 0,
                        "ok_links": 0,
                        "failed_links": 0,
                        "total_data_in": 0,
                        "total_data_out": 0,
                        "links": [],
                    }
                    
                    for link in client.list_links(instance or component.config.instance):
                        stats["total_links"] += 1
                        
                        if getattr(link, 'disabled', False):
                            stats["disabled_links"] += 1
                        else:
                            stats["enabled_links"] += 1
                        
                        if link.status == "OK":
                            stats["ok_links"] += 1
                        elif link.status == "FAILED":
                            stats["failed_links"] += 1
                        
                        stats["total_data_in"] += getattr(link, 'data_in_count', 0) or 0
                        stats["total_data_out"] += getattr(link, 'data_out_count', 0) or 0
                        
                        stats["links"].append({
                            "name": link.name,
                            "status": link.status,
                            "data_in": getattr(link, 'data_in_count', 0),
                            "data_out": getattr(link, 'data_out_count', 0),
                        })
                    
                    return {
                        "instance": instance or component.config.instance,
                        "statistics": stats,
                    }
            except Exception as e:
                return component._handle_error("link_get_statistics", e)

        # Register resources
        @server.resource("link://status")
        async def get_all_links_status() -> str:
            """Get current status of all links."""
            # Duplicate the logic instead of calling the tool
            try:
                async with component.client_manager.get_client() as client:
                    links = []
                    for link in client.list_links(component.config.instance):
                        links.append({
                            "name": link.name,
                            "type": getattr(link, 'type', 'unknown'),
                            "status": link.status,
                            "disabled": getattr(link, 'disabled', False),
                            "data_in_count": getattr(link, 'data_in_count', 0),
                            "data_out_count": getattr(link, 'data_out_count', 0),
                        })
                    
                    lines = [f"Links in {component.config.instance} ({len(links)} total):"]
                    for link in links:
                        status = "DISABLED" if link["disabled"] else link["status"]
                        type_info = f" ({link['type']})" if link['type'] != 'unknown' else ""
                        lines.append(
                            f"  - {link['name']}{type_info}: {status} "
                            f"[in: {link['data_in_count']}, out: {link['data_out_count']}]"
                        )
                    
                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {str(e)}"

        @server.resource("link://statistics")
        async def get_link_statistics() -> str:
            """Get link performance statistics."""
            # Duplicate the logic instead of calling the tool
            try:
                async with component.client_manager.get_client() as client:
                    stats = {
                        "total_links": 0,
                        "enabled_links": 0,
                        "disabled_links": 0,
                        "ok_links": 0,
                        "failed_links": 0,
                        "total_data_in": 0,
                        "total_data_out": 0,
                    }
                    
                    for link in client.list_links(component.config.instance):
                        stats["total_links"] += 1
                        
                        if getattr(link, 'disabled', False):
                            stats["disabled_links"] += 1
                        else:
                            stats["enabled_links"] += 1
                        
                        if link.status == "OK":
                            stats["ok_links"] += 1
                        elif link.status == "FAILED":
                            stats["failed_links"] += 1
                        
                        stats["total_data_in"] += getattr(link, 'data_in_count', 0) or 0
                        stats["total_data_out"] += getattr(link, 'data_out_count', 0) or 0
                    
                    lines = [
                        f"Link Statistics for {component.config.instance}:",
                        f"  Total Links: {stats['total_links']}",
                        f"  Enabled: {stats['enabled_links']}",
                        f"  Disabled: {stats['disabled_links']}",
                        f"  OK: {stats['ok_links']}",
                        f"  Failed: {stats['failed_links']}",
                        "",
                        f"  Total Data In: {stats['total_data_in']}",
                        f"  Total Data Out: {stats['total_data_out']}",
                    ]
                    
                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {str(e)}"