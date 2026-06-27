"""Models for MTN Cloud clouds (zones)."""

from enum import Enum
from typing import Any

from pydantic import Field

from mtn_cloud.models.base import Resource


class CloudType(str, Enum):
    """Cloud/zone types."""

    OPENSTACK = "openstack"
    VMWARE = "vmware"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    STANDARD = "standard"


class Cloud(Resource):
    """
    MTN Cloud cloud (zone).

    Clouds represent infrastructure endpoints where resources can be deployed.
    Also known as "zones" in the Morpheus API.

    Example:
        # List clouds
        for cloud in cloud.clouds.list():
            print(f"{cloud.name}: {cloud.cloud_type}")

        # Get specific cloud
        c = cloud.clouds.get(1)
        print(f"Location: {c.location}")
    """

    description: str | None = Field(default=None)
    code: str | None = Field(default=None)

    zone_type: dict[str, Any] | None = Field(
        default=None,
        alias="zoneType",
        description="Cloud type info",
    )
    cloud_type: str | None = Field(
        default=None,
        alias="cloudType",
        description="Cloud type code",
    )

    location: str | None = Field(default=None)

    status: str | None = Field(default=None)
    enabled: bool = Field(default=True)
    visibility: str | None = Field(default=None)

    account_id: int | None = Field(default=None, alias="accountId")
    account: dict[str, Any] | None = Field(default=None)

    groups: list[dict[str, Any]] = Field(default_factory=list, description="Associated groups")

    server_count: int | None = Field(default=None, alias="serverCount")

    config: dict[str, Any] | None = Field(default=None)

    auto_recover_power_state: bool = Field(default=False, alias="autoRecoverPowerState")
    scale_priority: int | None = Field(default=None, alias="scalePriority")

    cost_status: str | None = Field(default=None, alias="costStatus")
    cost_last_sync: str | None = Field(default=None, alias="costLastSync")

    @property
    def is_enabled(self) -> bool:
        """Check if cloud is enabled."""
        return self.enabled and self.status != "disabled"

    @property
    def group_ids(self) -> list[int]:
        """Get list of associated group IDs."""
        return [g["id"] for g in self.groups if "id" in g]

    @property
    def type_code(self) -> str | None:
        """Get the cloud type code."""
        if self.zone_type:
            return self.zone_type.get("code")
        return self.cloud_type
