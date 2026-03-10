"""
Volume Models
=============

Models for MTN Cloud storage volumes.
"""

from typing import Any, Optional
from pydantic import Field

from mtn_cloud.models.base import Resource


class StorageVolume(Resource):
    """
    MTN Cloud storage volume.

    Represents a block storage volume that can be attached to instances.
    """

    # Volume details
    description: Optional[str] = Field(default=None)

    # Size
    size: Optional[int] = Field(default=None, alias="maxStorage", description="Size in bytes")
    size_gb: Optional[int] = Field(default=None, description="Size in GB")

    # Type
    storage_type: Optional[dict[str, Any]] = Field(default=None, alias="storageType")
    volume_type: Optional[str] = Field(default=None, alias="volumeType")

    # Status
    status: Optional[str] = Field(default=None, description="Volume status")

    # Attachment
    instance_id: Optional[int] = Field(default=None, alias="instanceId")
    device_name: Optional[str] = Field(default=None, alias="deviceName")

    # Root volume
    root_volume: bool = Field(default=False, alias="rootVolume")

    # Datastore
    datastore: Optional[dict[str, Any]] = Field(default=None)
    datastore_id: Optional[str] = Field(default=None, alias="datastoreId")

    # Cloud/Zone
    zone: Optional[dict[str, Any]] = Field(default=None)

    # External reference
    external_id: Optional[str] = Field(default=None, alias="externalId")

    @property
    def is_attached(self) -> bool:
        """Check if volume is attached to an instance."""
        return self.instance_id is not None


# Alias for backwards compatibility
Volume = StorageVolume

