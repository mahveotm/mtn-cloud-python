"""Public package exports for the MTN Cloud Python SDK."""

from mtn_cloud._version import __version__
from mtn_cloud.client import MTNCloud
from mtn_cloud.config import MTNCloudConfig
from mtn_cloud.exceptions import (
    AuthenticationError,
    ForbiddenError,
    MTNCloudError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)

__author__ = "Marvellous Osuolale"
__license__ = "MIT"
__all__ = [
    # Main client
    "MTNCloud",
    # Configuration
    "MTNCloudConfig",
    # Exceptions
    "MTNCloudError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "ForbiddenError",
    "TimeoutError",
    "__version__",
]
