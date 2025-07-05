"""Pytest configuration and fixtures for Yamcs MCP Server tests."""

import pytest
from unittest.mock import Mock, AsyncMock
from yamcs.client import YamcsClient

from yamcs_mcp.client import YamcsClientManager
from yamcs_mcp.config import Config, YamcsConfig, MCPConfig


@pytest.fixture
def mock_yamcs_config():
    """Create a mock Yamcs configuration."""
    return YamcsConfig(
        url="http://localhost:8090",
        instance="test-instance",
        timeout=30.0,
        max_retries=3,
    )


@pytest.fixture
def mock_mcp_config():
    """Create a mock MCP configuration."""
    return MCPConfig(
        transport="stdio",
        host="127.0.0.1",
        port=8000,
    )


@pytest.fixture
def mock_config(mock_yamcs_config, mock_mcp_config):
    """Create a complete mock configuration."""
    config = Config()
    config.yamcs = mock_yamcs_config
    config.mcp = mock_mcp_config
    return config


@pytest.fixture
def mock_yamcs_client():
    """Create a mock Yamcs client."""
    client = Mock(spec=YamcsClient)
    
    # Mock common methods
    client.get_server_info.return_value = Mock(
        version="5.0.0",
        serverId="test-server",
    )
    
    client.list_instances.return_value = [
        Mock(
            name="test-instance",
            state="RUNNING",
            mission_time="2024-01-01T00:00:00Z",
        )
    ]
    
    return client


@pytest.fixture
def mock_client_manager(mock_yamcs_config, mock_yamcs_client):
    """Create a mock client manager."""
    manager = Mock(spec=YamcsClientManager)
    manager.config = mock_yamcs_config
    
    # Create async context manager mock
    async_cm = AsyncMock()
    async_cm.__aenter__.return_value = mock_yamcs_client
    async_cm.__aexit__.return_value = None
    
    manager.get_client.return_value = async_cm
    manager.test_connection = AsyncMock(return_value=True)
    
    return manager