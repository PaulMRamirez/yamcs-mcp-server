"""Link Management server for Yamcs MCP."""

from typing import Any

from ..client import YamcsClientManager
from .base_server import BaseYamcsServer
from ..config import YamcsConfig


class LinkServer(BaseYamcsServer):
    """Link server for data link operations."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Link server.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("Links", client_manager, config)
        self._register_link_tools()
        self._register_link_resources()

    def _register_link_tools(self) -> None:
        """Register link-specific tools."""
        
        @self.tool()
        async def list_links(
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
                            "type": getattr(link, 'class_name', None),
                            "status": link.status,
                            "disabled": not getattr(link, 'enabled', True),
                            "parent": getattr(link, 'parent_name', None),
                            "data_in_count": getattr(link, 'in_count', 0),
                            "data_out_count": getattr(link, 'out_count', 0),
                        })

                    return {
                        "instance": instance or self.config.instance,
                        "count": len(links),
                        "links": links,
                    }
            except Exception as e:
                return self._handle_error("list_links", e)

        @self.tool()
        async def get_status(
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
                    link_client = client.get_link(
                        instance=instance or self.config.instance,
                        link=link,
                    )
                    
                    # Get the link info from the LinkClient
                    link_info = link_client.get_info()

                    return {
                        "name": link_info.name,
                        "type": getattr(link_info, 'class_name', None),
                        "status": link_info.status,
                        "disabled": not getattr(link_info, 'enabled', True),
                        "statistics": {
                            "data_in_count": getattr(link_info, 'in_count', 0),
                            "data_out_count": getattr(link_info, 'out_count', 0),
                            "last_data_in": getattr(link_info, 'dataInTime', None),
                            "last_data_out": getattr(link_info, 'dataOutTime', None),
                        },
                        "details": getattr(link_info, 'detail_status', None),
                        "extra": getattr(link_info, 'extra', {}),
                        "actions": getattr(link_info, 'actions', []),
                    }
            except Exception as e:
                return self._handle_error("get_status", e)

        @self.tool()
        async def enable_link(
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
                    link_obj.enable_link()

                    return {
                        "success": True,
                        "link": link,
                        "operation": "enable",
                        "message": f"Link '{link}' enabled successfully",
                    }
            except Exception as e:
                return self._handle_error("enable_link", e)

        @self.tool()
        async def disable_link(
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
                    link_obj.disable_link()

                    return {
                        "success": True,
                        "link": link,
                        "operation": "disable",
                        "message": f"Link '{link}' disabled successfully",
                    }
            except Exception as e:
                return self._handle_error("disable_link", e)


    def _register_link_resources(self) -> None:
        """Register link-specific resources."""
        
        @self.resource("link://status")
        async def get_all_links_status() -> str:
            """Get current status of all links."""
            try:
                async with self.client_manager.get_client() as client:
                    links = []
                    for link in client.list_links(self.config.instance):
                        links.append({
                            "name": link.name,
                            "type": getattr(link, 'class_name', 'unknown'),
                            "status": link.status,
                            "disabled": not getattr(link, 'enabled', True),
                            "data_in_count": getattr(link, 'in_count', 0),
                            "data_out_count": getattr(link, 'out_count', 0),
                        })

                    lines = [f"Links in {self.config.instance} ({len(links)} total):"]
                    for link in links:
                        status = "DISABLED" if link["disabled"] else link["status"]
                        type_info = f" ({link['type']})" if link['type'] != 'unknown' else ""
                        lines.append(
                            f"  - {link['name']}{type_info}: {status} "
                            f"[in: {link['data_in_count']}, out: {link['data_out_count']}]"
                        )

                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"