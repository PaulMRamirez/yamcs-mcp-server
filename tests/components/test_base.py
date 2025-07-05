"""Tests for the base component functionality."""

import pytest
from unittest.mock import Mock, AsyncMock
from abc import ABCMeta

from yamcs_mcp.components.base import BaseYamcsComponent


class ConcreteComponent(BaseYamcsComponent):
    """Concrete implementation for testing."""
    
    def register_with_server(self, server):
        """Implement abstract method."""
        # Register a test tool
        @server.tool()
        async def test_tool():
            return {"result": "success"}
        
        # Register a test resource
        @server.resource("test://resource")
        async def test_resource():
            return "Test resource content"


class TestBaseYamcsComponent:
    """Test the base component functionality."""

    @pytest.fixture
    def base_component(self, mock_client_manager, mock_yamcs_config):
        """Create a concrete component instance for testing."""
        return ConcreteComponent("Test", mock_client_manager, mock_yamcs_config)

    def test_component_initialization(self, base_component, mock_client_manager, mock_yamcs_config):
        """Test base component initialization."""
        assert base_component.name == "YamcsTest"
        assert base_component.client_manager == mock_client_manager
        assert base_component.config == mock_yamcs_config
        assert base_component.logger is not None
        assert base_component.tools == {}
        assert base_component.resources == {}

    def test_abstract_class(self):
        """Test that BaseYamcsComponent is abstract."""
        # Verify it's an abstract base class
        assert ABCMeta in BaseYamcsComponent.__class__.__mro__
        
        # Verify abstract method exists
        assert hasattr(BaseYamcsComponent, 'register_with_server')
        assert getattr(BaseYamcsComponent.register_with_server, '__isabstractmethod__', False)

    @pytest.mark.asyncio
    async def test_health_check_success(self, base_component, mock_client_manager):
        """Test successful health check."""
        mock_client_manager.test_connection = AsyncMock(return_value=True)
        
        result = await base_component.health_check()
        
        assert result["status"] == "healthy"
        assert result["component"] == "YamcsTest"
        assert result["yamcs_connected"] is True
        assert result["yamcs_url"] == "http://localhost:8090"
        assert result["yamcs_instance"] == "test-instance"

    @pytest.mark.asyncio
    async def test_health_check_failure(self, base_component, mock_client_manager):
        """Test health check when connection fails."""
        mock_client_manager.test_connection = AsyncMock(return_value=False)
        
        result = await base_component.health_check()
        
        assert result["status"] == "unhealthy"
        assert result["component"] == "YamcsTest"
        assert result["yamcs_connected"] is False

    @pytest.mark.asyncio
    async def test_health_check_exception(self, base_component, mock_client_manager):
        """Test health check with exception."""
        mock_client_manager.test_connection = AsyncMock(side_effect=Exception("Connection refused"))
        
        result = await base_component.health_check()
        
        assert result["status"] == "unhealthy"
        assert result["component"] == "YamcsTest"
        assert result["error"] == "Connection refused"

    def test_handle_error(self, base_component):
        """Test error handling method."""
        error = ValueError("Test error message")
        
        result = base_component._handle_error("test_operation", error)
        
        assert result["error"] is True
        assert result["message"] == "Test error message"
        assert result["operation"] == "test_operation"
        assert result["component"] == "YamcsTest"

    def test_register_with_server(self, base_component):
        """Test component registration with server."""
        mock_server = Mock()
        mock_server._tools = {}
        mock_server._resources = {}
        
        # Mock decorators
        def tool_decorator():
            def decorator(func):
                mock_server._tools[func.__name__] = func
                return func
            return decorator
        
        def resource_decorator(uri):
            def decorator(func):
                mock_server._resources[uri] = func
                return func
            return decorator
        
        mock_server.tool = tool_decorator
        mock_server.resource = resource_decorator
        
        # Register component
        base_component.register_with_server(mock_server)
        
        # Verify tool and resource were registered
        assert "test_tool" in mock_server._tools
        assert "test://resource" in mock_server._resources

    def test_component_name_formatting(self, mock_client_manager, mock_yamcs_config):
        """Test that component names are formatted correctly."""
        # Test various component names
        test_cases = [
            ("MDB", "YamcsMDB"),
            ("Processor", "YamcsProcessor"),
            ("Archive", "YamcsArchive"),
            ("LinkManagement", "YamcsLinkManagement"),
        ]
        
        for input_name, expected_name in test_cases:
            component = ConcreteComponent(input_name, mock_client_manager, mock_yamcs_config)
            assert component.name == expected_name

    def test_logger_creation(self, base_component):
        """Test that logger is created with correct name."""
        # Logger should be created with lowercased component name
        assert base_component.logger is not None
        # In actual implementation, logger name would be "yamcs_mcp.test"

    @pytest.mark.asyncio
    async def test_inheritance_pattern(self, mock_client_manager, mock_yamcs_config):
        """Test that the inheritance pattern works correctly."""
        
        class CustomComponent(BaseYamcsComponent):
            """Custom component for testing inheritance."""
            
            def __init__(self, client_manager, config):
                super().__init__("Custom", client_manager, config)
                self.custom_attribute = "test_value"
            
            def register_with_server(self, server):
                """Register custom tools."""
                @server.tool()
                async def custom_tool():
                    return {"custom": True}
        
        # Create instance
        custom = CustomComponent(mock_client_manager, mock_yamcs_config)
        
        # Verify inheritance
        assert isinstance(custom, BaseYamcsComponent)
        assert custom.name == "YamcsCustom"
        assert custom.custom_attribute == "test_value"
        
        # Verify health check works
        mock_client_manager.test_connection = AsyncMock(return_value=True)
        health = await custom.health_check()
        assert health["status"] == "healthy"
        assert health["component"] == "YamcsCustom"