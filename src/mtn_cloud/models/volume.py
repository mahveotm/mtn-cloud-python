"""
Volume Models
=============

Models for MTN Cloud storage volumes.
"""

from typing import Any

from pydantic import Field

from mtn_cloud.models.base import Resource


class StorageVolume(Resource):
    """
    MTN Cloud storage volume.

    Represents a block storage volume that can be attached to instances.
    """

    # Volume details
    description: str | None = Field(default=None)

    # Size
    size: int | None = Field(default=None, alias="maxStorage", description="Size in bytes")
    size_gb: int | None = Field(default=None, description="Size in GB")

    # Type
    storage_type: dict[str, Any] | None = Field(default=None, alias="storageType")
    volume_type: str | None = Field(default=None, alias="volumeType")

    # Status
    status: str | None = Field(default=None, description="Volume status")

    # Attachment
    instance_id: int | None = Field(default=None, alias="instanceId")
    device_name: str | None = Field(default=None, alias="deviceName")

    # Root volume
    root_volume: bool = Field(default=False, alias="rootVolume")

    # Datastore
    datastore: dict[str, Any] | None = Field(default=None)
    datastore_id: str | None = Field(default=None, alias="datastoreId")

    # Cloud/Zone
    zone: dict[str, Any] | None = Field(default=None)

    # External reference
    external_id: str | None = Field(default=None, alias="externalId")

    @property
    def is_attached(self) -> bool:
        """Check if volume is attached to an instance."""
        return self.instance_id is not None


# Alias for backwards compatibility
Volume = StorageVolume
