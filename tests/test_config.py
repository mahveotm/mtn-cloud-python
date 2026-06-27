"""Tests for configuration."""

import os
from unittest.mock import patch

import pytest

from mtn_cloud.config import MTNCloudConfig


class TestMTNCloudConfig:
    """Tests for configuration."""

    @pytest.fixture(autouse=True)
    def _clear_mtn_cloud_env(self, monkeypatch):
        """Ensure host MTN_CLOUD_* env vars do not leak into config tests."""
        keys = (
            "MTN_CLOUD_TOKEN",
            "MTN_CLOUD_USERNAME",
            "MTN_CLOUD_PASSWORD",
            "MTN_CLOUD_URL",
            "MTN_CLOUD_API_VERSION",
            "MTN_CLOUD_TIMEOUT",
            "MTN_CLOUD_MAX_RETRIES",
            "MTN_CLOUD_RETRY_DELAY",
            "MTN_CLOUD_VERIFY_SSL",
            "MTN_CLOUD_USER_AGENT",
            "MTN_CLOUD_DEBUG",
        )
        for key in keys:
            monkeypatch.delenv(key, raising=False)

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("url", "https://console.cloud.mtn.ng"),
            ("timeout", 30.0),
            ("max_retries", 3),
            ("verify_ssl", True),
        ],
    )
    def test_default_value(self, field, expected):
        """Use documented default values."""
        config = MTNCloudConfig()

        assert getattr(config, field) == expected

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("token", "my-token"),
            ("url", "https://custom.example.com"),
            ("timeout", 60),
            ("max_retries", 5),
        ],
    )
    def test_explicit_value(self, field, expected):
        """Use explicit constructor values."""
        config = MTNCloudConfig(
            token="my-token",
            url="https://custom.example.com",
            timeout=60,
            max_retries=5,
        )

        assert getattr(config, field) == expected

    def test_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from URL."""
        config = MTNCloudConfig(url="https://example.com/")
        assert config.url == "https://example.com"

    def test_api_url_property(self):
        """Test api_url property."""
        config = MTNCloudConfig(url="https://example.com")
        assert config.api_url == "https://example.com/api"

    @pytest.mark.parametrize(
        ("kwargs", "expected"),
        [
            ({"token": "test-token"}, True),
            ({"username": "user", "password": "pass"}, True),
            ({}, False),
        ],
    )
    def test_has_credentials(self, kwargs, expected):
        """Report whether usable credentials are configured."""
        config = MTNCloudConfig(**kwargs)

        assert config.has_credentials is expected

    @pytest.mark.parametrize(
        ("kwargs", "expected"),
        [
            ({"token": "test-token"}, "token"),
            ({"username": "user", "password": "pass"}, "credentials"),
            ({}, "none"),
        ],
    )
    def test_get_auth_method(self, kwargs, expected):
        """Detect the configured authentication method."""
        config = MTNCloudConfig(**kwargs)

        assert config.get_auth_method() == expected

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

    def test_timeout_accepts_valid_value(self):
        """Accept timeout values inside the supported range."""
        config = MTNCloudConfig(timeout=60)

        assert config.timeout == 60

    @pytest.mark.parametrize("timeout", [0.5, 500])
    def test_timeout_rejects_invalid_value(self, timeout):
        """Reject timeout values outside the supported range."""
        with pytest.raises(ValueError):
            MTNCloudConfig(timeout=timeout)

    def test_max_retries_accepts_valid_value(self):
        """Accept retry counts inside the supported range."""
        config = MTNCloudConfig(max_retries=5)

        assert config.max_retries == 5

    def test_max_retries_rejects_invalid_value(self):
        """Reject retry counts outside the supported range."""
        with pytest.raises(ValueError):
            MTNCloudConfig(max_retries=20)
