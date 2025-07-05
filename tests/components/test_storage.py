"""Tests for the Object Storage component."""

import pytest
from unittest.mock import Mock, AsyncMock

from yamcs_mcp.components.storage import ObjectStorageComponent


class TestObjectStorageComponent:
    """Test the Object Storage component."""

    @pytest.fixture
    def storage_component(self, mock_client_manager, mock_yamcs_config):
        """Create an Object Storage component instance."""
        return ObjectStorageComponent(mock_client_manager, mock_yamcs_config)

    @pytest.fixture
    def mock_server(self):
        """Create a mock FastMCP server."""
        server = Mock()
        server._tools = {}
        server._resources = {}
        
        def tool_decorator():
            def decorator(func):
                server._tools[func.__name__] = Mock(name=func.__name__, fn=func)
                return func
            return decorator
        
        def resource_decorator(uri):
            def decorator(func):
                server._resources[uri] = Mock(uri=uri, fn=func)
                return func
            return decorator
        
        server.tool = tool_decorator
        server.resource = resource_decorator
        return server

    def test_component_initialization(self, storage_component):
        """Test that the component initializes correctly."""
        assert storage_component.name == "YamcsObjectStorage"
        assert storage_component.client_manager is not None
        assert storage_component.config is not None

    def test_register_with_server(self, storage_component, mock_server):
        """Test component registration with server."""
        storage_component.register_with_server(mock_server)
        
        # Check tools were registered
        expected_tools = [
            "object_list_buckets",
            "object_list_objects",
            "object_get_object",
            "object_put_object",
            "object_delete_object",
            "object_get_metadata",
        ]
        
        for tool_name in expected_tools:
            assert tool_name in mock_server._tools
            
        # Check resources were registered
        expected_resources = [
            "object://buckets",
            "object://objects/{bucket}",
        ]
        
        for resource_uri in expected_resources:
            assert resource_uri in mock_server._resources

    @pytest.mark.asyncio
    async def test_object_list_buckets(self, storage_component, mock_server, mock_yamcs_client):
        """Test listing buckets."""
        storage_component.register_with_server(mock_server)
        
        # Mock storage client
        mock_storage = Mock()
        
        # Mock buckets
        mock_bucket1 = Mock(
            name="telemetry",
            created="2024-01-01T00:00:00Z",
            size=1024000,
            object_count=150,
        )
        mock_bucket1.max_size = 10485760  # 10MB
        
        mock_bucket2 = Mock(
            name="commands",
            created="2024-01-02T00:00:00Z",
            size=512000,
            object_count=50,
        )
        # Missing max_size attribute
        
        mock_storage.list_buckets.return_value = [mock_bucket1, mock_bucket2]
        mock_yamcs_client.get_storage_client.return_value = mock_storage
        
        # Get tool function
        list_buckets_tool = mock_server._tools["object_list_buckets"].fn
        
        result = await list_buckets_tool()
        
        assert result["instance"] == "test-instance"
        assert result["count"] == 2
        assert len(result["buckets"]) == 2
        
        assert result["buckets"][0]["name"] == "telemetry"
        assert result["buckets"][0]["size"] == 1024000
        assert result["buckets"][0]["object_count"] == 150
        assert result["buckets"][0]["max_size"] == 10485760
        
        assert result["buckets"][1]["name"] == "commands"
        assert result["buckets"][1]["max_size"] is None

    @pytest.mark.asyncio
    async def test_object_list_objects(self, storage_component, mock_server, mock_yamcs_client):
        """Test listing objects in a bucket."""
        storage_component.register_with_server(mock_server)
        
        # Mock storage client
        mock_storage = Mock()
        
        # Mock listing result
        mock_listing = Mock()
        
        # Mock objects
        mock_obj1 = Mock(
            name="data/2024/01/01/tm_1.dat",
            size=2048,
            created="2024-01-01T10:00:00Z",
        )
        mock_obj1.metadata = {"type": "telemetry", "source": "simulator"}
        
        mock_obj2 = Mock(
            name="data/2024/01/01/tm_2.dat",
            size=4096,
            created="2024-01-01T11:00:00Z",
        )
        # Missing metadata attribute
        
        mock_listing.objects = [mock_obj1, mock_obj2]
        mock_listing.prefixes = ["data/2024/01/02/", "data/2024/01/03/"]
        
        mock_storage.list_objects.return_value = mock_listing
        mock_yamcs_client.get_storage_client.return_value = mock_storage
        
        # Get tool function
        list_objects_tool = mock_server._tools["object_list_objects"].fn
        
        result = await list_objects_tool(
            bucket="telemetry",
            prefix="data/2024/01/",
            delimiter="/"
        )
        
        assert result["bucket"] == "telemetry"
        assert result["prefix"] == "data/2024/01/"
        assert result["count"] == 2
        assert len(result["objects"]) == 2
        
        assert result["objects"][0]["name"] == "data/2024/01/01/tm_1.dat"
        assert result["objects"][0]["size"] == 2048
        assert result["objects"][0]["metadata"] == {"type": "telemetry", "source": "simulator"}
        
        assert result["objects"][1]["metadata"] == {}
        assert result["prefixes"] == ["data/2024/01/02/", "data/2024/01/03/"]

    @pytest.mark.asyncio
    async def test_object_list_objects_limit(self, storage_component, mock_server, mock_yamcs_client):
        """Test listing objects with limit."""
        storage_component.register_with_server(mock_server)
        
        # Mock storage client
        mock_storage = Mock()
        
        # Mock many objects
        mock_listing = Mock()
        mock_listing.objects = [
            Mock(name=f"obj_{i}.dat", size=1024, created="2024-01-01T00:00:00Z")
            for i in range(10)
        ]
        # Set missing prefixes attribute
        mock_listing.prefixes = None
        
        mock_storage.list_objects.return_value = mock_listing
        mock_yamcs_client.get_storage_client.return_value = mock_storage
        
        # Get tool function
        list_objects_tool = mock_server._tools["object_list_objects"].fn
        
        result = await list_objects_tool(bucket="test", limit=5)
        
        assert result["count"] == 5  # Limited to 5
        assert len(result["objects"]) == 5
        assert result["prefixes"] == []  # Default for missing attribute

    @pytest.mark.asyncio
    async def test_object_get_object(self, storage_component, mock_server, mock_yamcs_client):
        """Test getting object info."""
        storage_component.register_with_server(mock_server)
        
        # Mock storage client and bucket
        mock_storage = Mock()
        mock_bucket = Mock()
        
        # Mock object
        mock_obj = Mock(
            size=8192,
            created="2024-01-01T12:00:00Z",
        )
        mock_obj.metadata = {"author": "test-user", "version": "1.0"}
        mock_obj.url = "http://yamcs.local/api/buckets/telemetry/objects/test.dat"
        
        mock_bucket.get_object.return_value = mock_obj
        mock_storage.get_bucket.return_value = mock_bucket
        mock_yamcs_client.get_storage_client.return_value = mock_storage
        
        # Get tool function
        get_object_tool = mock_server._tools["object_get_object"].fn
        
        result = await get_object_tool(
            bucket="telemetry",
            object_name="test.dat"
        )
        
        assert result["bucket"] == "telemetry"
        assert result["name"] == "test.dat"
        assert result["size"] == 8192
        assert result["metadata"] == {"author": "test-user", "version": "1.0"}
        assert result["url"] == "http://yamcs.local/api/buckets/telemetry/objects/test.dat"

    @pytest.mark.asyncio
    async def test_object_put_object(self, storage_component, mock_server, mock_yamcs_client):
        """Test uploading an object."""
        storage_component.register_with_server(mock_server)
        
        # Mock storage client
        mock_storage = Mock()
        mock_storage.upload_object = Mock()
        mock_yamcs_client.get_storage_client.return_value = mock_storage
        
        # Get tool function
        put_object_tool = mock_server._tools["object_put_object"].fn
        
        result = await put_object_tool(
            bucket="config",
            object_name="settings.json",
            content='{"key": "value"}',
            metadata={"type": "configuration", "version": "2.0"}
        )
        
        assert result["success"] is True
        assert result["bucket"] == "config"
        assert result["object_name"] == "settings.json"
        assert result["size"] == len('{"key": "value"}'.encode('utf-8'))
        assert result["metadata"] == {"type": "configuration", "version": "2.0"}
        
        # Verify upload was called
        mock_storage.upload_object.assert_called_once_with(
            bucket_name="config",
            object_name="settings.json",
            file_obj=b'{"key": "value"}',
            metadata={"type": "configuration", "version": "2.0"}
        )

    @pytest.mark.asyncio
    async def test_object_delete_object(self, storage_component, mock_server, mock_yamcs_client):
        """Test deleting an object."""
        storage_component.register_with_server(mock_server)
        
        # Mock storage client
        mock_storage = Mock()
        mock_storage.delete_object = Mock()
        mock_yamcs_client.get_storage_client.return_value = mock_storage
        
        # Get tool function
        delete_object_tool = mock_server._tools["object_delete_object"].fn
        
        result = await delete_object_tool(
            bucket="temp",
            object_name="old_data.dat"
        )
        
        assert result["success"] is True
        assert result["bucket"] == "temp"
        assert result["object_name"] == "old_data.dat"
        assert "deleted" in result["message"]
        
        # Verify delete was called
        mock_storage.delete_object.assert_called_once_with(
            bucket_name="temp",
            object_name="old_data.dat"
        )

    @pytest.mark.asyncio
    async def test_object_get_metadata(self, storage_component, mock_server, mock_yamcs_client):
        """Test getting object metadata."""
        storage_component.register_with_server(mock_server)
        
        # Mock storage client
        mock_storage = Mock()
        
        # Mock listing result
        mock_listing = Mock()
        mock_obj = Mock(
            name="test.dat",
            size=4096,
            created="2024-01-01T15:00:00Z",
        )
        mock_obj.metadata = {"tag": "important"}
        mock_obj.content_type = "application/octet-stream"
        
        mock_listing.objects = [mock_obj]
        mock_storage.list_objects.return_value = mock_listing
        mock_yamcs_client.get_storage_client.return_value = mock_storage
        
        # Get tool function
        get_metadata_tool = mock_server._tools["object_get_metadata"].fn
        
        result = await get_metadata_tool(
            bucket="data",
            object_name="test.dat"
        )
        
        assert result["bucket"] == "data"
        assert result["object_name"] == "test.dat"
        assert result["metadata"] == {"tag": "important"}
        assert result["system_metadata"]["size"] == 4096
        assert result["system_metadata"]["content_type"] == "application/octet-stream"

    @pytest.mark.asyncio
    async def test_object_get_metadata_not_found(self, storage_component, mock_server, mock_yamcs_client):
        """Test getting metadata for non-existent object."""
        storage_component.register_with_server(mock_server)
        
        # Mock storage client with empty listing
        mock_storage = Mock()
        mock_listing = Mock()
        mock_listing.objects = []
        mock_storage.list_objects.return_value = mock_listing
        mock_yamcs_client.get_storage_client.return_value = mock_storage
        
        # Get tool function
        get_metadata_tool = mock_server._tools["object_get_metadata"].fn
        
        result = await get_metadata_tool(
            bucket="data",
            object_name="nonexistent.dat"
        )
        
        assert result["error"] is True
        assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_missing_attributes_handling(self, storage_component, mock_server, mock_yamcs_client):
        """Test handling of missing attributes in storage objects."""
        storage_component.register_with_server(mock_server)
        
        # Mock storage client
        mock_storage = Mock()
        
        # Create object with minimal attributes
        mock_obj = Mock(spec=["name", "size", "created"])
        mock_obj.name = "minimal.dat"
        mock_obj.size = 1024
        mock_obj.created = "2024-01-01T00:00:00Z"
        
        mock_bucket = Mock()
        mock_bucket.get_object.return_value = mock_obj
        mock_storage.get_bucket.return_value = mock_bucket
        mock_yamcs_client.get_storage_client.return_value = mock_storage
        
        # Test get object with missing attributes
        get_object_tool = mock_server._tools["object_get_object"].fn
        result = await get_object_tool(bucket="test", object_name="minimal.dat")
        
        assert result["metadata"] == {}
        assert result["url"] is None

    @pytest.mark.asyncio
    async def test_resource_handlers(self, storage_component, mock_server, mock_yamcs_client):
        """Test resource handlers."""
        storage_component.register_with_server(mock_server)
        
        # Mock storage client
        mock_storage = Mock()
        
        # Mock buckets for buckets resource
        mock_buckets = [
            Mock(name="telemetry", size=2048000, object_count=100),
            Mock(name="commands", size=512000, object_count=25),
        ]
        mock_storage.list_buckets.return_value = mock_buckets
        
        mock_yamcs_client.get_storage_client.return_value = mock_storage
        
        # Test buckets resource
        buckets_resource = mock_server._resources["object://buckets"].fn
        result = await buckets_resource()
        
        assert "Storage Buckets in test-instance (2 total):" in result
        assert "telemetry: 100 objects, 1.95 MB" in result
        assert "commands: 25 objects, 0.49 MB" in result
        
        # Mock objects for objects resource
        mock_listing = Mock()
        mock_listing.objects = [
            Mock(name="file1.dat", size=2048),
            Mock(name="file2.dat", size=4096),
        ]
        mock_storage.list_objects.return_value = mock_listing
        
        # Test objects resource
        objects_resource = mock_server._resources["object://objects/{bucket}"].fn
        result = await objects_resource(bucket="telemetry")
        
        assert "Objects in bucket 'telemetry' (2 total):" in result
        assert "file1.dat (2.00 KB)" in result
        assert "file2.dat (4.00 KB)" in result

    @pytest.mark.asyncio
    async def test_error_handling(self, storage_component, mock_server, mock_yamcs_client):
        """Test error handling in storage operations."""
        storage_component.register_with_server(mock_server)
        
        # Mock an error
        mock_yamcs_client.get_storage_client.side_effect = Exception("Storage unavailable")
        
        # Test error in list buckets
        list_buckets_tool = mock_server._tools["object_list_buckets"].fn
        result = await list_buckets_tool()
        
        assert result["error"] is True
        assert "Storage unavailable" in result["message"]
        assert result["operation"] == "object_list_buckets"
        
        # Test error in put object
        put_object_tool = mock_server._tools["object_put_object"].fn
        result = await put_object_tool(
            bucket="test",
            object_name="error.dat",
            content="test"
        )
        
        assert result["error"] is True
        assert "Storage unavailable" in result["message"]
        assert result["operation"] == "object_put_object"