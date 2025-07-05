"""Object Storage component for Yamcs MCP Server."""

from typing import Any

from ..client import YamcsClientManager
from ..config import YamcsConfig
from .base import BaseYamcsComponent


class ObjectStorageComponent(BaseYamcsComponent):
    """Object Storage component for bucket and object management."""

    def __init__(
        self,
        client_manager: YamcsClientManager,
        config: YamcsConfig,
    ) -> None:
        """Initialize Object Storage component.

        Args:
            client_manager: Yamcs client manager
            config: Yamcs configuration
        """
        super().__init__("ObjectStorage", client_manager, config)

    def register_with_server(self, server: Any) -> None:
        """Register Object Storage tools and resources with the server."""

        # Store reference to self for use in closures
        component = self

        @server.tool()
        async def object_list_buckets(
            instance: str | None = None,
        ) -> dict[str, Any]:
            """List storage buckets.

            Args:
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: List of buckets with their properties
            """
            try:
                async with component.client_manager.get_client() as client:
                    storage = client.get_storage_client()

                    buckets = []
                    for bucket in storage.list_buckets():
                        buckets.append({
                            "name": bucket.name,
                            "created": bucket.created,
                            "size": bucket.size,
                            "object_count": bucket.object_count,
                            "max_size": bucket.max_size if hasattr(bucket, 'max_size') else None,
                        })

                    return {
                        "instance": instance or component.config.instance,
                        "count": len(buckets),
                        "buckets": buckets,
                    }
            except Exception as e:
                return component._handle_error("object_list_buckets", e)

        @server.tool()
        async def object_list_objects(
            bucket: str,
            prefix: str | None = None,
            delimiter: str | None = None,
            instance: str | None = None,
            limit: int = 1000,
        ) -> dict[str, Any]:
            """List objects in a bucket.

            Args:
                bucket: Bucket name
                prefix: Object name prefix filter
                delimiter: Delimiter for pseudo-directory listing
                instance: Yamcs instance (uses default if not specified)
                limit: Maximum number of objects to return

            Returns:
                dict: List of objects with their metadata
            """
            try:
                async with component.client_manager.get_client() as client:
                    storage = client.get_storage_client()
                    objects = []
                    prefixes = []
                    count = 0

                    listing = storage.list_objects(
                        bucket_name=bucket,
                        prefix=prefix,
                        delimiter=delimiter,
                    )

                    # Collect objects
                    for obj in listing.objects:
                        if count >= limit:
                            break
                        objects.append({
                            "name": obj.name,
                            "size": obj.size,
                            "created": obj.created,
                            "metadata": obj.metadata if hasattr(obj, 'metadata') else {},
                        })
                        count += 1

                    # Collect prefixes (pseudo-directories)
                    if hasattr(listing, 'prefixes'):
                        prefixes = listing.prefixes

                    return {
                        "bucket": bucket,
                        "prefix": prefix,
                        "count": len(objects),
                        "objects": objects,
                        "prefixes": prefixes,
                    }
            except Exception as e:
                return component._handle_error("object_list_objects", e)

        @server.tool()
        async def object_get_object(
            bucket: str,
            object_name: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get object metadata and download URL.

            Args:
                bucket: Bucket name
                object_name: Object name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Object metadata and content info
            """
            try:
                async with component.client_manager.get_client() as client:
                    storage = client.get_storage_client()
                    bucket_obj = storage.get_bucket(bucket)

                    # Get object info
                    obj = bucket_obj.get_object(object_name)

                    return {
                        "bucket": bucket,
                        "name": object_name,
                        "size": obj.size,
                        "created": obj.created,
                        "metadata": obj.metadata if hasattr(obj, 'metadata') else {},
                        "url": obj.url if hasattr(obj, 'url') else None,
                    }
            except Exception as e:
                return component._handle_error("object_get_object", e)

        @server.tool()
        async def object_put_object(
            bucket: str,
            object_name: str,
            content: str,
            metadata: dict[str, str] | None = None,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Upload an object to a bucket.

            Args:
                bucket: Bucket name
                object_name: Object name
                content: Object content (text)
                metadata: Optional metadata key-value pairs
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Upload result
            """
            try:
                async with component.client_manager.get_client() as client:
                    storage = client.get_storage_client()
                    # Upload object
                    storage.upload_object(
                        bucket_name=bucket,
                        object_name=object_name,
                        file_obj=content.encode('utf-8'),
                        metadata=metadata,
                    )

                    return {
                        "success": True,
                        "bucket": bucket,
                        "object_name": object_name,
                        "size": len(content.encode('utf-8')),
                        "metadata": metadata,
                    }
            except Exception as e:
                return component._handle_error("object_put_object", e)

        @server.tool()
        async def object_delete_object(
            bucket: str,
            object_name: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Delete an object from a bucket.

            Args:
                bucket: Bucket name
                object_name: Object name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Deletion result
            """
            try:
                async with component.client_manager.get_client() as client:
                    storage = client.get_storage_client()
                    # Delete object
                    storage.delete_object(
                        bucket_name=bucket,
                        object_name=object_name,
                    )

                    return {
                        "success": True,
                        "bucket": bucket,
                        "object_name": object_name,
                        "message": f"Object '{object_name}' deleted from bucket '{bucket}'",
                    }
            except Exception as e:
                return component._handle_error("object_delete_object", e)

        @server.tool()
        async def object_get_metadata(
            bucket: str,
            object_name: str,
            instance: str | None = None,
        ) -> dict[str, Any]:
            """Get object metadata.

            Args:
                bucket: Bucket name
                object_name: Object name
                instance: Yamcs instance (uses default if not specified)

            Returns:
                dict: Object metadata
            """
            try:
                async with component.client_manager.get_client() as client:
                    storage = client.get_storage_client()
                    # Get object metadata
                    # Note: The storage client doesn't have a direct get_object method
                    # We need to list objects and find the one we want
                    listing = storage.list_objects(bucket_name=bucket, prefix=object_name)
                    obj = None
                    for o in listing.objects:
                        if o.name == object_name:
                            obj = o
                            break

                    if not obj:
                        raise Exception(f"Object '{object_name}' not found in bucket '{bucket}'")

                    return {
                        "bucket": bucket,
                        "object_name": object_name,
                        "metadata": obj.metadata if hasattr(obj, 'metadata') else {},
                        "system_metadata": {
                            "size": obj.size,
                            "created": obj.created,
                            "content_type": obj.content_type if hasattr(obj, 'content_type') else None,
                        },
                    }
            except Exception as e:
                return component._handle_error("object_get_metadata", e)

        # Register resources
        @server.resource("object://buckets")
        async def list_all_buckets() -> str:
            """List all available storage buckets."""
            # Duplicate the logic instead of calling the tool
            try:
                async with component.client_manager.get_client() as client:
                    storage = client.get_storage_client()

                    buckets = []
                    for bucket in storage.list_buckets():
                        buckets.append({
                            "name": bucket.name,
                            "size": bucket.size,
                            "object_count": bucket.object_count,
                        })

                    lines = [f"Storage Buckets in {component.config.instance} ({len(buckets)} total):"]
                    for bucket in buckets:
                        size_mb = bucket["size"] / (1024 * 1024) if bucket["size"] else 0
                        lines.append(
                            f"  - {bucket['name']}: {bucket['object_count']} objects, "
                            f"{size_mb:.2f} MB"
                        )

                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"

        @server.resource("object://objects/{bucket}")
        async def list_bucket_objects(bucket: str) -> str:
            """List objects in a specific bucket."""
            # Duplicate the logic instead of calling the tool
            try:
                async with component.client_manager.get_client() as client:
                    storage = client.get_storage_client()
                    objects = []
                    count = 0

                    listing = storage.list_objects(bucket_name=bucket)

                    # Collect objects
                    for obj in listing.objects:
                        if count >= 50:
                            break
                        objects.append({
                            "name": obj.name,
                            "size": obj.size,
                        })
                        count += 1

                    lines = [f"Objects in bucket '{bucket}' ({len(objects)} total):"]
                    for obj in objects:
                        size_kb = obj["size"] / 1024 if obj["size"] else 0
                        lines.append(f"  - {obj['name']} ({size_kb:.2f} KB)")

                    # Note: We can't get the total count without iterating through all objects
                    # So we won't show the "and X more" message

                    return "\n".join(lines)
            except Exception as e:
                return f"Error: {e!s}"
