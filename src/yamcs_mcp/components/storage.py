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

    def _register_tools(self) -> None:
        """Register Object Storage-specific tools."""
        
        @self.tool()
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
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage(instance or self.config.instance)
                    
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
                        "instance": instance or self.config.instance,
                        "count": len(buckets),
                        "buckets": buckets,
                    }
            except Exception as e:
                return self._handle_error("object_list_buckets", e)

        @self.tool()
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
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage(instance or self.config.instance)
                    bucket_obj = storage.get_bucket(bucket)
                    
                    objects = []
                    prefixes = []
                    count = 0
                    
                    listing = bucket_obj.list_objects(
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
                return self._handle_error("object_list_objects", e)

        @self.tool()
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
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage(instance or self.config.instance)
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
                return self._handle_error("object_get_object", e)

        @self.tool()
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
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage(instance or self.config.instance)
                    bucket_obj = storage.get_bucket(bucket)
                    
                    # Upload object
                    bucket_obj.upload_object(
                        object_name=object_name,
                        data=content.encode('utf-8'),
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
                return self._handle_error("object_put_object", e)

        @self.tool()
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
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage(instance or self.config.instance)
                    bucket_obj = storage.get_bucket(bucket)
                    
                    # Delete object
                    bucket_obj.delete_object(object_name)
                    
                    return {
                        "success": True,
                        "bucket": bucket,
                        "object_name": object_name,
                        "message": f"Object '{object_name}' deleted from bucket '{bucket}'",
                    }
            except Exception as e:
                return self._handle_error("object_delete_object", e)

        @self.tool()
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
                async with self.client_manager.get_client() as client:
                    storage = client.get_storage(instance or self.config.instance)
                    bucket_obj = storage.get_bucket(bucket)
                    
                    # Get object
                    obj = bucket_obj.get_object(object_name)
                    
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
                return self._handle_error("object_get_metadata", e)

    def _register_resources(self) -> None:
        """Register Object Storage-specific resources."""
        
        @self.resource("object://buckets")
        async def list_all_buckets() -> str:
            """List all available storage buckets."""
            result = await self.object_list_buckets()
            if "error" in result:
                return f"Error: {result['message']}"
            
            lines = [f"Storage Buckets in {result['instance']} ({result['count']} total):"]
            for bucket in result.get("buckets", []):
                size_mb = bucket["size"] / (1024 * 1024) if bucket["size"] else 0
                lines.append(
                    f"  - {bucket['name']}: {bucket['object_count']} objects, "
                    f"{size_mb:.2f} MB"
                )
            
            return "\n".join(lines)

        @self.resource("object://objects/{bucket}")
        async def list_bucket_objects(bucket: str) -> str:
            """List objects in a specific bucket."""
            result = await self.object_list_objects(bucket=bucket, limit=50)
            if "error" in result:
                return f"Error: {result['message']}"
            
            lines = [f"Objects in bucket '{bucket}' ({result['count']} total):"]
            for obj in result.get("objects", [])[:50]:
                size_kb = obj["size"] / 1024 if obj["size"] else 0
                lines.append(f"  - {obj['name']} ({size_kb:.2f} KB)")
            
            if result["count"] > 50:
                lines.append(f"  ... and {result['count'] - 50} more")
            
            return "\n".join(lines)