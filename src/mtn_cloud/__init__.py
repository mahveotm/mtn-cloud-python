"""
MTN Cloud Python SDK
====================

A community-maintained Python SDK for interacting with MTN Cloud (Morpheus).

Quick Start:
    ```python
    from mtn_cloud import MTNCloud

    # Initialize client
    cloud = MTNCloud(token="your-api-token")

    # List instances
    for instance in cloud.instances.list():
        print(f"{instance.name}: {instance.status}")

    # Create an instance
    instance = cloud.instances.create(
        name="my-app",
        cloud_id=1,
        group_id=1,
        instance_type_code="MTN-CS10",
        plan_id=6923,
        layout_id=327,
    )

    # Instance actions
    instance.stop()
    instance.start()
    instance.delete()
    ```

Environment Variables:
    MTN_CLOUD_TOKEN: API access token
    MTN_CLOUD_URL: API URL (defaults to https://console.cloud.mtn.ng)

Author: Marvellous Osuolale
License: MIT
"""

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

__version__ = "0.1.11"
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
]
