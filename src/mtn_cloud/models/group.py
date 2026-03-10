"""
Group Models
============

Models for MTN Cloud groups (sites).
"""

from typing import Any, Optional
from pydantic import Field

from mtn_cloud.models.base import Resource


class Group(Resource):
    """
    MTN Cloud group (site).

    Groups are organizational units that contain instances and other resources.
    Also known as "sites" in the Morpheus API.

    Example:
        ```python
        # List groups
        for group in cloud.groups.list():
            print(f"{group.name}: {group.location}")

        # Get specific group
        group = cloud.groups.get(1)
        ```
    """

    # Group details
    description: Optional[str] = Field(default=None)
    code: Optional[str] = Field(default=None)

    # Location
    location: Optional[str] = Field(default=None, description="Group location")

    # Status
    active: bool = Field(default=True)

    # Visibility
    visibility: Optional[str] = Field(default=None)

    # Account
    account_id: Optional[int] = Field(default=None, alias="accountId")

    # Stats
    server_count: Optional[int] = Field(default=None, alias="serverCount")
    instance_count: Optional[int] = Field(default=None, alias="instanceCount")

    # Clouds/Zones
    zones: list[dict[str, Any]] = Field(default_factory=list, description="Associated clouds")

    # Config
    config: Optional[dict[str, Any]] = Field(default=None)

    @property
    def cloud_ids(self) -> list[int]:
        """Get list of associated cloud IDs."""
        return [z["id"] for z in self.zones if "id" in z]

