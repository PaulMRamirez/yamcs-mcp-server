"""Object storage server for Yamcs MCP."""

from typing import Any

from ..client import YamcsClientManager
from ..config import YamcsConfig
from .base_server import BaseYamcsServer


class StorageServer(BaseYamcsServer):
    """Storage server for managing Yamcs object storage."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Storage server.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("Storage", client_manager, config)
        self._register_storage_tools()
        self._register_storage_resources()

    def _register_storage_tools(self) -> None:
        """Register storage-specific tools."""

        @self.tool()
        async def buckets(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """List storage buckets.

            Args:
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: List of buckets
            """
            try:
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage_client()

                    buckets = []
                    for bucket in storage.list_buckets(
                        instance or self.config.instance
                    ):
                        buckets.append(
                            {
                                "name": bucket.name,
                                "size": getattr(bucket, "size", 0),
                                "object_count": getattr(bucket, "num_objects", 0),
                                "created": getattr(bucket, "created", None),
                            }
                        )

                    return {
                        "instance": instance or self.config.instance,
                        "count": len(buckets),
                        "buckets": buckets,
                    }
            except Exception as e:
                return self._handle_error("buckets", e)

        @self.tool()
        async def objects(
            bucket: str,
            prefix: str | None = None,
            instance: str | None = None,
            limit: int = 100,
        ) -> dict[str, Any]:
            """List objects in a bucket.

            Args:
                bucket: Bucket name
                prefix: Object prefix filter
                instance: Yamcs instance (uses default if not specified)
                limit: Maximum number of objects to return (default: 100)

            Returns:
                dict: List of objects
            """
            try:
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage_client()

                    objects = []
                    count = 0
                    for obj in storage.list_objects(
                        instance=instance or self.config.instance,
                        bucket_name=bucket,
                        prefix=prefix,
                    ):
                        if count >= limit:
                            break

                        objects.append(
                            {
                                "name": obj.name,
                                "size": obj.size,
                                "created": obj.created.isoformat()
                                if obj.created
                                else None,
                                "metadata": getattr(obj, "metadata", {}),
                            }
                        )
                        count += 1

                    return {
                        "bucket": bucket,
                        "instance": instance or self.config.instance,
                        "count": len(objects),
                        "objects": objects,
                    }
            except Exception as e:
                return self._handle_error("objects", e)

        @self.tool()
        async def get_object_info(
            bucket: str,
            object_name: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get information about a specific object.

            Args:
                bucket: Bucket name
                object_name: Object name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Object information
            """
            try:
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage_client()

                    # Get object info
                    obj = storage.get_object(
                        instance=instance or self.config.instance,
                        bucket_name=bucket,
                        object_name=object_name,
                    )

                    return {
                        "name": obj.name,
                        "bucket": bucket,
                        "size": obj.size,
                        "created": obj.created.isoformat() if obj.created else None,
                        "metadata": getattr(obj, "metadata", {}),
                        "url": getattr(obj, "url", None),
                    }
            except Exception as e:
                return self._handle_error("get_object_info", e)

        @self.tool()
        async def delete_object(
            bucket: str,
            object_name: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Delete an object from storage.

            Args:
                bucket: Bucket name
                object_name: Object name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage_client()

                    # Delete the object
                    storage.remove_object(
                        instance=instance or self.config.instance,
                        bucket_name=bucket,
                        object_name=object_name,
                    )

                    return {
                        "success": True,
                        "bucket": bucket,
                        "object": object_name,
                        "message": (
                            f"Object '{object_name}' deleted from bucket '{bucket}'"
                        ),
                    }
            except Exception as e:
                return self._handle_error("delete_object", e)

        @self.tool()
        async def create_bucket(
            name: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Create a new storage bucket.

            Args:
                name: Bucket name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Operation result
            """
            try:
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage_client()

                    # Create the bucket
                    bucket = storage.create_bucket(
                        instance=instance or self.config.instance,
                        name=name,
                    )

                    return {
                        "success": True,
                        "bucket": {
                            "name": bucket.name,
                            "created": getattr(bucket, "created", None),
                        },
                        "message": f"Bucket '{name}' created successfully",
                    }
            except Exception as e:
                return self._handle_error("create_bucket", e)

    def _register_storage_resources(self) -> None:
        """Register storage-specific resources."""

        @self.resource("storage://overview")
        async def get_storage_overview() -> str:
            """Get an overview of storage usage."""
            try:
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage_client()

                    lines = [f"Storage Overview for {self.config.instance}:"]

                    total_size = 0
                    total_objects = 0

                    for bucket in storage.list_buckets(self.config.instance):
                        size = getattr(bucket, "size", 0)
                        count = getattr(bucket, "num_objects", 0)
                        total_size += size
                        total_objects += count

                        size_mb = size / (1024 * 1024)
                        lines.append(
                            f"  - {bucket.name}: {count} objects ({size_mb:.1f} MB)"
                        )

                    lines.append("")
                    total_mb = total_size / (1024 * 1024)
                    lines.append(f"Total: {total_objects} objects ({total_mb:.1f} MB)")

                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"
