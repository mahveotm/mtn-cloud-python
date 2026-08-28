"""Tests for the MTNCloud client."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from mtn_cloud import MTNCloud, MTNCloudConfig
from mtn_cloud.models.user import User
from mtn_cloud.resources.archive_buckets import ArchiveBucketsResource
from mtn_cloud.resources.backups import BackupsResource
from mtn_cloud.resources.clouds import CloudsResource
from mtn_cloud.resources.groups import GroupsResource
from mtn_cloud.resources.instance_types import InstanceTypesResource
from mtn_cloud.resources.instances import InstancesResource
from mtn_cloud.resources.networks import NetworksResource
from mtn_cloud.resources.plans import PlansResource
from mtn_cloud.resources.security_groups import SecurityGroupsResource
from mtn_cloud.resources.storage_buckets import StorageBucketsResource
from mtn_cloud.resources.virtual_images import VirtualImagesResource


@pytest.fixture
def patched_http_client():
    """Patch the HTTP client used by MTNCloud."""
    with patch("mtn_cloud.client.HTTPClient") as mock_http_class:
        yield mock_http_class


class TestMTNCloudInit:
    """Tests for MTNCloud initialization."""

    @pytest.mark.parametrize(
        ("kwargs", "field", "expected"),
        [
            ({"token": "test-token"}, "token", "test-token"),
            ({"username": "user", "password": "pass"}, "username", "user"),
            ({"username": "user", "password": "pass"}, "password", "pass"),
            (
                {"token": "test", "url": "https://custom.example.com"},
                "url",
                "https://custom.example.com",
            ),
        ],
    )
    def test_init_config_field(
        self,
        patched_http_client: MagicMock,
        kwargs: dict[str, Any],
        field: str,
        expected: Any,
    ) -> None:
        """Build config from constructor arguments."""
        cloud = MTNCloud(**kwargs)

        if field == "token":
            actual = cloud.config.get_token_value()
        elif field == "password":
            actual = cloud.config.get_password_value()
        else:
            actual = getattr(cloud.config, field)
        assert actual == expected

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("token", "config-token"),
            ("timeout", 60),
        ],
    )
    def test_init_with_config_object(
        self,
        patched_http_client: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Use a provided config object unchanged."""
        config = MTNCloudConfig(token="config-token", timeout=60)

        cloud = MTNCloud(config=config)

        actual = (
            cloud.config.get_token_value() if field == "token" else getattr(cloud.config, field)
        )
        assert actual == expected

    def test_default_url(self, patched_http_client: MagicMock) -> None:
        """Default to the MTN Cloud console URL."""
        cloud = MTNCloud(token="test")

        assert "console.cloud.mtn.ng" in cloud.config.url

    def test_explicit_verify_ssl_true_overrides_environment(
        self,
        patched_http_client: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Honor an explicit secure setting even when the environment disables it."""
        monkeypatch.setenv("MTN_CLOUD_VERIFY_SSL", "false")

        cloud = MTNCloud(token="test", verify_ssl=True)

        assert cloud.config.verify_ssl is True

    def test_omitted_verify_ssl_uses_environment(
        self,
        patched_http_client: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Use settings precedence when the constructor argument is omitted."""
        monkeypatch.setenv("MTN_CLOUD_VERIFY_SSL", "false")

        cloud = MTNCloud(token="test")

        assert cloud.config.verify_ssl is False


class TestMTNCloudResources:
    """Tests for resource manager access."""

    @pytest.mark.parametrize(
        ("property_name", "resource_type"),
        [
            ("instances", InstancesResource),
            ("instance_types", InstanceTypesResource),
            ("networks", NetworksResource),
            ("groups", GroupsResource),
            ("clouds", CloudsResource),
            ("plans", PlansResource),
            ("storage_buckets", StorageBucketsResource),
            ("archive_buckets", ArchiveBucketsResource),
            ("security_groups", SecurityGroupsResource),
            ("backups", BackupsResource),
            ("virtual_images", VirtualImagesResource),
        ],
    )
    def test_resource_property_type(
        self,
        patched_http_client: MagicMock,
        property_name: str,
        resource_type: type,
    ) -> None:
        """Expose each service resource manager."""
        cloud = MTNCloud(token="test")

        assert isinstance(getattr(cloud, property_name), resource_type)

    @pytest.mark.parametrize(
        "property_name",
        [
            "instances",
            "instance_types",
            "networks",
            "groups",
            "clouds",
            "plans",
            "storage_buckets",
            "archive_buckets",
            "security_groups",
            "backups",
            "virtual_images",
        ],
    )
    def test_resource_property_is_cached(
        self,
        patched_http_client: MagicMock,
        property_name: str,
    ) -> None:
        """Cache service resource managers per client."""
        cloud = MTNCloud(token="test")

        assert getattr(cloud, property_name) is getattr(cloud, property_name)


class TestMTNCloudContextManager:
    """Tests for context manager functionality."""

    def test_context_manager_returns_client(self, patched_http_client: MagicMock) -> None:
        """Return the client from context manager entry."""
        patched_http_client.return_value = MagicMock()

        with MTNCloud(token="test") as cloud:
            assert isinstance(cloud, MTNCloud)

    def test_context_manager_closes_http(self, patched_http_client: MagicMock) -> None:
        """Close the HTTP client when leaving a context manager."""
        mock_http = MagicMock()
        patched_http_client.return_value = mock_http

        with MTNCloud(token="test"):
            pass

        mock_http.close.assert_called_once()


class TestMTNCloudWhoami:
    """Tests for whoami method."""

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("username", "testuser"),
            ("email", "test@example.com"),
        ],
    )
    def test_whoami_user_field(
        self,
        patched_http_client: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse the current authenticated user."""
        mock_http = MagicMock()
        mock_http.get.return_value = {
            "user": {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
            }
        }
        patched_http_client.return_value = mock_http

        user = MTNCloud(token="test").whoami()

        assert getattr(user, field) == expected

    def test_whoami_returns_user_model(self, patched_http_client: MagicMock) -> None:
        """Return a User model."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"user": {"id": 1, "username": "testuser"}}
        patched_http_client.return_value = mock_http

        assert isinstance(MTNCloud(token="test").whoami(), User)

    def test_whoami_request_path(self, patched_http_client: MagicMock) -> None:
        """Call the current-user endpoint."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"user": {"id": 1, "username": "testuser"}}
        patched_http_client.return_value = mock_http

        MTNCloud(token="test").whoami()

        mock_http.get.assert_called_with("/whoami")


class TestMTNCloudPing:
    """Tests for ping method."""

    def test_ping_success(self, patched_http_client: MagicMock) -> None:
        """Return true when whoami succeeds."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"user": {"id": 1, "username": "test"}}
        patched_http_client.return_value = mock_http

        assert MTNCloud(token="test").ping() is True

    def test_ping_failure(self, patched_http_client: MagicMock) -> None:
        """Return false when whoami fails."""
        mock_http = MagicMock()
        mock_http.get.side_effect = Exception("Connection failed")
        patched_http_client.return_value = mock_http

        assert MTNCloud(token="test").ping() is False
