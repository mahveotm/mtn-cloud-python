"""
Tests for configuration.
"""

import os
import pytest
from unittest.mock import patch

from mtn_cloud.config import MTNCloudConfig


class TestMTNCloudConfig:
    """Tests for configuration."""

    def test_default_values(self):
        """Test default configuration values."""
        config = MTNCloudConfig()

        assert config.url == "https://console.cloud.mtn.ng"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.verify_ssl is True

    def test_explicit_values(self):
        """Test explicit configuration values."""
        config = MTNCloudConfig(
            token="my-token",
            url="https://custom.example.com",
            timeout=60,
            max_retries=5,
        )

        assert config.token == "my-token"
        assert config.url == "https://custom.example.com"
        assert config.timeout == 60
        assert config.max_retries == 5

    def test_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from URL."""
        config = MTNCloudConfig(url="https://example.com/")
        assert config.url == "https://example.com"

    def test_api_url_property(self):
        """Test api_url property."""
        config = MTNCloudConfig(url="https://example.com")
        assert config.api_url == "https://example.com/api"

    def test_has_credentials_with_token(self):
        """Test has_credentials with token."""
        config = MTNCloudConfig(token="test-token")
        assert config.has_credentials is True

    def test_has_credentials_with_username_password(self):
        """Test has_credentials with username/password."""
        config = MTNCloudConfig(username="user", password="pass")
        assert config.has_credentials is True

    def test_has_credentials_empty(self):
        """Test has_credentials when empty."""
        config = MTNCloudConfig()
        assert config.has_credentials is False

    def test_get_auth_method_token(self):
        """Test auth method detection for token."""
        config = MTNCloudConfig(token="test-token")
        assert config.get_auth_method() == "token"

    def test_get_auth_method_credentials(self):
        """Test auth method detection for credentials."""
        config = MTNCloudConfig(username="user", password="pass")
        assert config.get_auth_method() == "credentials"

    def test_get_auth_method_none(self):
        """Test auth method detection when none configured."""
        config = MTNCloudConfig()
        assert config.get_auth_method() == "none"

    def test_env_variable_token(self):
        """Test loading token from environment variable."""
        with patch.dict(os.environ, {"MTN_CLOUD_TOKEN": "env-token"}):
            config = MTNCloudConfig()
            assert config.token == "env-token"

    def test_env_variable_url(self):
        """Test loading URL from environment variable."""
        with patch.dict(os.environ, {"MTN_CLOUD_URL": "https://env.example.com"}):
            config = MTNCloudConfig()
            assert config.url == "https://env.example.com"

    def test_explicit_overrides_env(self):
        """Test that explicit values override environment."""
        with patch.dict(os.environ, {"MTN_CLOUD_TOKEN": "env-token"}):
            config = MTNCloudConfig(token="explicit-token")
            assert config.token == "explicit-token"

    def test_timeout_validation(self):
        """Test timeout validation."""
        # Valid range
        config = MTNCloudConfig(timeout=60)
        assert config.timeout == 60

        # Too low
        with pytest.raises(ValueError):
            MTNCloudConfig(timeout=0.5)

        # Too high
        with pytest.raises(ValueError):
            MTNCloudConfig(timeout=500)

    def test_max_retries_validation(self):
        """Test max_retries validation."""
        # Valid range
        config = MTNCloudConfig(max_retries=5)
        assert config.max_retries == 5

        # Too high
        with pytest.raises(ValueError):
            MTNCloudConfig(max_retries=20)

