"""Models for MTN Cloud groups (sites)."""

from typing import Any

from pydantic import Field

from mtn_cloud.models.base import Resource


class Group(Resource):
    """
    MTN Cloud group (site).

    Groups are organizational units that contain instances and other resources.
    Also known as "sites" in the Morpheus API.

    Example:
        # List groups
        for group in cloud.groups.list():
            print(f"{group.name}: {group.location}")

        # Get specific group
        group = cloud.groups.get(1)
    """

    # Group details
    description: str | None = Field(default=None)
    code: str | None = Field(default=None)

    # Location
    location: str | None = Field(default=None, description="Group location")

    # Status
    active: bool = Field(default=True)

    # Visibility
    visibility: str | None = Field(default=None)

    # Account
    account_id: int | None = Field(default=None, alias="accountId")

    # Stats
    server_count: int | None = Field(default=None, alias="serverCount")
    instance_count: int | None = Field(default=None, alias="instanceCount")

    # Clouds/Zones
    zones: list[dict[str, Any]] = Field(default_factory=list, description="Associated clouds")

    # Config
    config: dict[str, Any] | None = Field(default=None)

    @property
    def cloud_ids(self) -> list[int]:
        """Get list of associated cloud IDs."""
        return [z["id"] for z in self.zones if "id" in z]
