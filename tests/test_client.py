"""
Tests for MTNCloud client.
"""

from unittest.mock import MagicMock, patch

from mtn_cloud import MTNCloud, MTNCloudConfig
from mtn_cloud.models.user import User


class TestMTNCloudInit:
    """Tests for MTNCloud initialization."""

    def test_init_with_token(self):
        """Test initialization with token."""
        with patch("mtn_cloud.client.HTTPClient"):
            cloud = MTNCloud(token="test-token")
            assert cloud.config.token == "test-token"

    def test_init_with_username_password(self):
        """Test initialization with username/password."""
        with patch("mtn_cloud.client.HTTPClient"):
            cloud = MTNCloud(username="user", password="pass")
            assert cloud.config.username == "user"
            assert cloud.config.password == "pass"

    def test_init_with_custom_url(self):
        """Test initialization with custom URL."""
        with patch("mtn_cloud.client.HTTPClient"):
            cloud = MTNCloud(token="test", url="https://custom.example.com")
            assert cloud.config.url == "https://custom.example.com"

    def test_init_with_config_object(self):
        """Test initialization with config object."""
        config = MTNCloudConfig(token="config-token", timeout=60)
        with patch("mtn_cloud.client.HTTPClient"):
            cloud = MTNCloud(config=config)
            assert cloud.config.token == "config-token"
            assert cloud.config.timeout == 60

    def test_default_url(self):
        """Test that default URL is MTN Cloud."""
        with patch("mtn_cloud.client.HTTPClient"):
            cloud = MTNCloud(token="test")
            assert "console.cloud.mtn.ng" in cloud.config.url


class TestMTNCloudResources:
    """Tests for resource manager access."""

    def test_instances_property(self):
        """Test instances resource manager."""
        with patch("mtn_cloud.client.HTTPClient"):
            cloud = MTNCloud(token="test")
            instances = cloud.instances
            assert instances is not None
            # Should return same instance on repeated access
            assert cloud.instances is instances

    def test_networks_property(self):
        """Test networks resource manager."""
        with patch("mtn_cloud.client.HTTPClient"):
            cloud = MTNCloud(token="test")
            networks = cloud.networks
            assert networks is not None

    def test_groups_property(self):
        """Test groups resource manager."""
        with patch("mtn_cloud.client.HTTPClient"):
            cloud = MTNCloud(token="test")
            groups = cloud.groups
            assert groups is not None

    def test_clouds_property(self):
        """Test clouds resource manager."""
        with patch("mtn_cloud.client.HTTPClient"):
            cloud = MTNCloud(token="test")
            clouds = cloud.clouds
            assert clouds is not None

    def test_plans_property(self):
        """Test plans resource manager."""
        with patch("mtn_cloud.client.HTTPClient"):
            cloud = MTNCloud(token="test")
            plans = cloud.plans
            assert plans is not None


class TestMTNCloudContextManager:
    """Tests for context manager functionality."""

    def test_context_manager(self):
        """Test using client as context manager."""
        with patch("mtn_cloud.client.HTTPClient") as MockHTTP:
            mock_http = MagicMock()
            MockHTTP.return_value = mock_http

            with MTNCloud(token="test") as cloud:
                assert cloud is not None

            # Should close on exit
            mock_http.close.assert_called_once()


class TestMTNCloudWhoami:
    """Tests for whoami method."""

    def test_whoami(self):
        """Test getting current user."""
        with patch("mtn_cloud.client.HTTPClient") as MockHTTP:
            mock_http = MagicMock()
            mock_http.get.return_value = {
                "user": {
                    "id": 1,
                    "username": "testuser",
                    "email": "test@example.com",
                }
            }
            MockHTTP.return_value = mock_http

            cloud = MTNCloud(token="test")
            cloud._http = mock_http

            user = cloud.whoami()

            assert isinstance(user, User)
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            mock_http.get.assert_called_with("/whoami")


class TestMTNCloudPing:
    """Tests for ping method."""

    def test_ping_success(self):
        """Test ping returns True on success."""
        with patch("mtn_cloud.client.HTTPClient") as MockHTTP:
            mock_http = MagicMock()
            mock_http.get.return_value = {"user": {"id": 1, "username": "test"}}
            MockHTTP.return_value = mock_http

            cloud = MTNCloud(token="test")
            cloud._http = mock_http

            assert cloud.ping() is True

    def test_ping_failure(self):
        """Test ping returns False on failure."""
        with patch("mtn_cloud.client.HTTPClient") as MockHTTP:
            mock_http = MagicMock()
            mock_http.get.side_effect = Exception("Connection failed")
            MockHTTP.return_value = mock_http

            cloud = MTNCloud(token="test")
            cloud._http = mock_http

            assert cloud.ping() is False
