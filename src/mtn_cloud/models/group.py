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

    description: str | None = Field(default=None)
    code: str | None = Field(default=None)

    location: str | None = Field(default=None, description="Group location")

    active: bool = Field(default=True)

    visibility: str | None = Field(default=None)

    account_id: int | None = Field(default=None, alias="accountId")

    server_count: int | None = Field(default=None, alias="serverCount")
    instance_count: int | None = Field(default=None, alias="instanceCount")

    zones: list[dict[str, Any]] = Field(default_factory=list, description="Associated clouds")

    config: dict[str, Any] | None = Field(default=None)

    @property
    def cloud_ids(self) -> list[int]:
        """Get list of associated cloud IDs."""
        return [z["id"] for z in self.zones if "id" in z]
