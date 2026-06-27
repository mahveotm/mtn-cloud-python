"""Models for MTN Cloud storage volumes."""

from typing import Any

from pydantic import Field

from mtn_cloud.models.base import Resource


class StorageVolume(Resource):
    """
    MTN Cloud storage volume.

    Represents a block storage volume that can be attached to instances.
    """

    description: str | None = Field(default=None)

    size: int | None = Field(default=None, alias="maxStorage", description="Size in bytes")
    size_gb: int | None = Field(default=None, description="Size in GB")

    storage_type: dict[str, Any] | None = Field(default=None, alias="storageType")
    volume_type: str | None = Field(default=None, alias="volumeType")

    status: str | None = Field(default=None, description="Volume status")

    instance_id: int | None = Field(default=None, alias="instanceId")
    device_name: str | None = Field(default=None, alias="deviceName")

    root_volume: bool = Field(default=False, alias="rootVolume")

    datastore: dict[str, Any] | None = Field(default=None)
    datastore_id: str | None = Field(default=None, alias="datastoreId")

    zone: dict[str, Any] | None = Field(default=None)

    external_id: str | None = Field(default=None, alias="externalId")

    @property
    def is_attached(self) -> bool:
        """Check if volume is attached to an instance."""
        return self.instance_id is not None


# Backwards-compatible name retained for earlier SDK versions.
Volume = StorageVolume
