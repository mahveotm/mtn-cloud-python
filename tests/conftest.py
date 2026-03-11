"""
Test configuration and fixtures.
"""

from unittest.mock import MagicMock, patch

import pytest

from mtn_cloud import MTNCloud, MTNCloudConfig
from mtn_cloud.http import HTTPClient


@pytest.fixture
def mock_config():
    """Create a test configuration."""
    return MTNCloudConfig(
        token="test-token-12345",
        url="https://test.cloud.mtn.ng",
        timeout=10,
        verify_ssl=False,
    )


@pytest.fixture
def mock_http_client(mock_config):
    """Create a mocked HTTP client."""
    with patch.object(HTTPClient, "_create_session") as mock_session:
        mock_session.return_value = MagicMock()
        client = HTTPClient(mock_config)
        client._token = "test-token-12345"
        yield client


@pytest.fixture
def cloud_client(mock_config, mock_http_client):
    """Create a MTNCloud client with mocked HTTP."""
    with patch("mtn_cloud.client.HTTPClient") as MockHTTP:
        MockHTTP.return_value = mock_http_client
        client = MTNCloud(config=mock_config)
        client._http = mock_http_client
        yield client


# Sample API responses for testing
SAMPLE_INSTANCE = {
    "id": 123,
    "name": "test-instance",
    "status": "running",
    "description": "Test instance",
    "instanceType": {"id": 1, "name": "MTN-CS10", "code": "MTN-CS10"},
    "plan": {"id": 6923, "name": "Small"},
    "ipAddress": "192.168.1.100",
    "dateCreated": "2024-01-15T10:30:00Z",
    "lastUpdated": "2024-01-15T12:00:00Z",
}

SAMPLE_INSTANCES_LIST = {
    "instances": [
        SAMPLE_INSTANCE,
        {
            "id": 124,
            "name": "test-instance-2",
            "status": "stopped",
            "ipAddress": "192.168.1.101",
        },
    ],
    "meta": {"total": 2},
}

SAMPLE_NETWORK = {
    "id": 298,
    "name": "test-network",
    "displayName": "test-network",
    "type": {"id": 8, "name": "OpenStack Network", "code": "openstackNetwork"},
    "zone": {"id": 1, "name": "MTNNG_CLOUD_AZ_1"},
    "cidr": "192.168.1.0/24",
    "gateway": "192.168.1.1",
    "active": True,
}

SAMPLE_GROUP = {
    "id": 1,
    "name": "MTNNG_CLOUD_AZ_1",
    "location": "Lagos",
    "active": True,
}

SAMPLE_CLOUD = {
    "id": 1,
    "name": "MTNNG_CLOUD_AZ_1",
    "code": "mtnng-az1",
    "zoneType": {"id": 999, "code": "openstack", "name": "OpenStack"},
    "cloudType": "openstack",
    "enabled": True,
}

SAMPLE_USER = {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "firstName": "Test",
    "lastName": "User",
}
