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

    def _register_tools(self) -> None:
        """Register Link Management-specific tools."""
        
        @self.tool()
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
                async with self.client_manager.get_client() as client:
                    links = []
                    for link in client.list_links(instance or self.config.instance):
                        links.append({
                            "name": link.name,
                            "type": link.type,
                            "status": link.status,
                            "disabled": link.disabled,
                            "parent": link.parent_name if hasattr(link, 'parent_name') else None,
                            "data_in_count": link.data_in_count,
                            "data_out_count": link.data_out_count,
                        })
                    
                    return {
                        "instance": instance or self.config.instance,
                        "count": len(links),
                        "links": links,
                    }
            except Exception as e:
                return self._handle_error("link_list_links", e)

        @self.tool()
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
                async with self.client_manager.get_client() as client:
                    link_obj = client.get_link(
                        instance=instance or self.config.instance,
                        link=link,
                    )
                    
                    return {
                        "name": link_obj.name,
                        "type": link_obj.type,
                        "status": link_obj.status,
                        "disabled": link_obj.disabled,
                        "statistics": {
                            "data_in_count": link_obj.data_in_count,
                            "data_out_count": link_obj.data_out_count,
                            "last_data_in": link_obj.last_data_in_time,
                            "last_data_out": link_obj.last_data_out_time,
                        },
                        "details": link_obj.detail_status if hasattr(link_obj, 'detail_status') else None,
                    }
            except Exception as e:
                return self._handle_error("link_get_status", e)

        @self.tool()
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
                async with self.client_manager.get_client() as client:
                    link_obj = client.get_link(
                        instance=instance or self.config.instance,
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
                return self._handle_error("link_enable_link", e)

        @self.tool()
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
                async with self.client_manager.get_client() as client:
                    link_obj = client.get_link(
                        instance=instance or self.config.instance,
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
                return self._handle_error("link_disable_link", e)

        @self.tool()
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
                async with self.client_manager.get_client() as client:
                    link_obj = client.get_link(
                        instance=instance or self.config.instance,
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
                return self._handle_error("link_reset_link", e)

        @self.tool()
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
                async with self.client_manager.get_client() as client:
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
                    
                    for link in client.list_links(instance or self.config.instance):
                        stats["total_links"] += 1
                        
                        if link.disabled:
                            stats["disabled_links"] += 1
                        else:
                            stats["enabled_links"] += 1
                        
                        if link.status == "OK":
                            stats["ok_links"] += 1
                        elif link.status == "FAILED":
                            stats["failed_links"] += 1
                        
                        stats["total_data_in"] += link.data_in_count or 0
                        stats["total_data_out"] += link.data_out_count or 0
                        
                        stats["links"].append({
                            "name": link.name,
                            "status": link.status,
                            "data_in": link.data_in_count,
                            "data_out": link.data_out_count,
                        })
                    
                    return {
                        "instance": instance or self.config.instance,
                        "statistics": stats,
                    }
            except Exception as e:
                return self._handle_error("link_get_statistics", e)

    def _register_resources(self) -> None:
        """Register Link Management-specific resources."""
        
        @self.resource("link://status")
        async def get_all_links_status() -> str:
            """Get current status of all links."""
            result = await self.link_list_links()
            if "error" in result:
                return f"Error: {result['message']}"
            
            lines = [f"Links in {result['instance']} ({result['count']} total):"]
            for link in result.get("links", []):
                status = "DISABLED" if link["disabled"] else link["status"]
                lines.append(
                    f"  - {link['name']} ({link['type']}): {status} "
                    f"[in: {link['data_in_count']}, out: {link['data_out_count']}]"
                )
            
            return "\n".join(lines)

        @self.resource("link://statistics")
        async def get_link_statistics() -> str:
            """Get link performance statistics."""
            result = await self.link_get_statistics()
            if "error" in result:
                return f"Error: {result['message']}"
            
            stats = result["statistics"]
            lines = [
                f"Link Statistics for {result['instance']}:",
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