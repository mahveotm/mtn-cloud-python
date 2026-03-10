"""
MTN Cloud SDK Configuration
===========================

Configuration management using pydantic-settings.
Supports environment variables and explicit configuration.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MTNCloudConfig(BaseSettings):
    """
    Configuration for the MTN Cloud SDK.

    Configuration can be provided via:
    1. Constructor arguments
    2. Environment variables (prefixed with MTN_CLOUD_)
    3. Default values

    Example:
        ```python
        # From environment: MTN_CLOUD_TOKEN=xxx
        config = MTNCloudConfig()

        # Explicit configuration
        config = MTNCloudConfig(
            token="your-token",
            timeout=60,
        )
        ```

    Environment Variables:
        MTN_CLOUD_TOKEN: API access token
        MTN_CLOUD_URL: API base URL
        MTN_CLOUD_TIMEOUT: Request timeout in seconds
        MTN_CLOUD_MAX_RETRIES: Maximum retry attempts
        MTN_CLOUD_VERIFY_SSL: Enable/disable SSL verification
    """

    model_config = SettingsConfigDict(
        env_prefix="MTN_CLOUD_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Authentication
    token: str | None = Field(
        default=None,
        description="MTN Cloud API access token",
    )

    username: str | None = Field(
        default=None,
        description="MTN Cloud username (alternative to token)",
    )

    password: str | None = Field(
        default=None,
        description="MTN Cloud password (use with username)",
    )

    # API Configuration
    url: str = Field(
        default="https://console.cloud.mtn.ng",
        description="MTN Cloud API base URL",
    )

    api_version: str = Field(
        default="v1",
        description="API version (not currently used, for future)",
    )

    # Request Configuration
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Request timeout in seconds",
    )

    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts",
    )

    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Base delay between retries (exponential backoff)",
    )

    # SSL Configuration
    verify_ssl: bool = Field(
        default=True,
        description="Verify SSL certificates",
    )

    # Client Configuration
    user_agent: str = Field(
        default="mtn-cloud-python/0.1.0",
        description="User-Agent header for API requests",
    )

    # Debug
    debug: bool = Field(
        default=False,
        description="Enable debug logging",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure URL doesn't have trailing slash."""
        return v.rstrip("/")

    @property
    def api_url(self) -> str:
        """Get the full API URL."""
        return f"{self.url}/api"

    @property
    def has_credentials(self) -> bool:
        """Check if any authentication credentials are configured."""
        return bool(self.token or (self.username and self.password))

    def get_auth_method(self) -> str:
        """Determine the authentication method to use."""
        if self.token:
            return "token"
        elif self.username and self.password:
            return "credentials"
        return "none"


# Default configuration instance
default_config = MTNCloudConfig()
