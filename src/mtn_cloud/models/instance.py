"""
Instance Models
===============

Models for MTN Cloud compute instances.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from pydantic import Field

from mtn_cloud.models.base import BaseModel, Resource

if TYPE_CHECKING:
    from mtn_cloud.resources.instances import InstancesResource


class InstanceStatus(str, Enum):
    """Possible instance statuses."""

    PROVISIONING = "provisioning"
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    SUSPENDED = "suspended"
    FAILED = "failed"
    RESIZING = "resizing"
    RESTARTING = "restarting"
    UNKNOWN = "unknown"


class InstanceVolume(BaseModel):
    """Volume attached to an instance."""

    id: int | None = None
    name: str = "root"
    size: int = Field(..., description="Volume size in GB")
    storage_type: int | None = Field(default=None, alias="storageType")
    datastore_id: str | None = Field(default="auto", alias="datastoreId")
    root_volume: bool = Field(default=True, alias="rootVolume")


class InstanceNetwork(BaseModel):
    """Network interface configuration for an instance."""

    id: int | None = None
    network_id: int | None = Field(default=None, alias="networkId")
    ip_address: str | None = Field(default=None, alias="ipAddress")
    ip_mode: str | None = Field(default=None, alias="ipMode")

    # Nested network object (from API response)
    network: dict[str, Any] | None = None


class InstanceConfig(BaseModel):
    """Instance configuration options."""

    resource_pool_id: str | None = Field(default=None, alias="resourcePoolId")
    availability_zone: str | None = Field(default=None, alias="availabilityZone")
    security_group: str | None = Field(default="default", alias="securityGroup")
    os_external_network_id: str | None = Field(default=None, alias="osExternalNetworkId")


class InstanceType(BaseModel):
    """Instance type information."""

    id: int | None = None
    name: str | None = None
    code: str | None = None


class InstancePlan(BaseModel):
    """Service plan information."""

    id: int | None = None
    name: str | None = None
    code: str | None = None


class Instance(Resource):
    """
    MTN Cloud compute instance.

    Represents a virtual machine or container running on MTN Cloud.

    Example:
        ```python
        # Get instance details
        instance = cloud.instances.get(123)
        print(f"Name: {instance.name}")
        print(f"Status: {instance.status}")
        print(f"IP: {instance.primary_ip}")

        # Perform actions
        instance.stop()
        instance.start()
        ```
    """

    # Basic info
    description: str | None = Field(default=None, description="Instance description")

    # Status
    status: str = Field(default="unknown", description="Current instance status")
    status_message: str | None = Field(
        default=None,
        alias="statusMessage",
        description="Status details",
    )

    # Type and plan
    instance_type: InstanceType | None = Field(default=None, alias="instanceType")
    plan: InstancePlan | None = None
    layout: dict[str, Any] | None = None

    # Location
    cloud: dict[str, Any] | None = Field(default=None, description="Cloud/zone info")
    group: dict[str, Any] | None = Field(default=None, alias="site", description="Group/site info")

    # Network
    ip_address: str | None = Field(
        default=None,
        alias="ipAddress",
        description="Primary IP address",
    )
    external_ip: str | None = Field(
        default=None,
        alias="externalIp",
        description="External/floating IP address",
    )
    interfaces: list[InstanceNetwork] = Field(
        default_factory=list,
        alias="interfaces",
        description="Network interfaces",
    )

    # Storage
    volumes: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Attached volumes",
    )

    # Configuration
    config: dict[str, Any] | None = Field(default=None, description="Instance config")

    # Resources
    max_memory: int | None = Field(default=None, alias="maxMemory")
    max_cores: int | None = Field(default=None, alias="maxCores")
    max_storage: int | None = Field(default=None, alias="maxStorage")

    # Labels/tags
    labels: list[str] = Field(default_factory=list, description="Instance labels")
    tags: list[dict[str, Any]] = Field(default_factory=list, description="Instance tags")

    # Timestamps
    provisioned_date: datetime | None = Field(default=None, alias="dateProvisioned")

    # Internal reference to resource manager (set by the SDK)
    _resource: Optional["InstancesResource"] = None

    def _set_resource(self, resource: "InstancesResource") -> None:
        """Set the resource manager for action methods."""
        object.__setattr__(self, "_resource", resource)

    @property
    def primary_ip(self) -> str | None:
        """Get the primary IP address."""
        return self.ip_address or self.external_ip

    @property
    def is_running(self) -> bool:
        """Check if instance is running."""
        return self.status.lower() == "running"

    @property
    def is_stopped(self) -> bool:
        """Check if instance is stopped."""
        return self.status.lower() in ("stopped", "off")

    @property
    def cloud_id(self) -> int | None:
        """Get the cloud/zone ID."""
        if self.cloud:
            return self.cloud.get("id")
        return None

    @property
    def group_id(self) -> int | None:
        """Get the group/site ID."""
        if self.group:
            return self.group.get("id")
        return None

    # Action methods - delegate to resource manager
    def start(self) -> "Instance":
        """Start the instance."""
        if self._resource is None:
            raise RuntimeError("Instance not bound to a resource manager")
        return self._resource.start(self.id)

    def stop(self) -> "Instance":
        """Stop the instance."""
        if self._resource is None:
            raise RuntimeError("Instance not bound to a resource manager")
        return self._resource.stop(self.id)

    def restart(self) -> "Instance":
        """Restart the instance."""
        if self._resource is None:
            raise RuntimeError("Instance not bound to a resource manager")
        return self._resource.restart(self.id)

    def suspend(self) -> "Instance":
        """Suspend the instance."""
        if self._resource is None:
            raise RuntimeError("Instance not bound to a resource manager")
        return self._resource.suspend(self.id)

    def delete(self, force: bool = False) -> bool:
        """Delete the instance."""
        if self._resource is None:
            raise RuntimeError("Instance not bound to a resource manager")
        return self._resource.delete(self.id, force=force)

    def refresh(self) -> "Instance":
        """Refresh instance data from API."""
        if self._resource is None:
            raise RuntimeError("Instance not bound to a resource manager")
        updated = self._resource.get(self.id)
        # Update self with new data
        for field in self.model_fields:
            if hasattr(updated, field):
                setattr(self, field, getattr(updated, field))
        return self


class InstanceCreate(BaseModel):
    """
    Model for creating a new instance.

    Example:
        ```python
        instance = cloud.instances.create(
            name="my-app",
            cloud_id=1,
            group_id=1,
            instance_type_code="MTN-CS10",
            layout_id=327,
            plan_id=6923,
            volumes=[
                InstanceVolume(name="root", size=10),
            ],
        )
        ```
    """

    # Required fields
    name: str = Field(..., min_length=1, max_length=255, description="Instance name")

    # Location (one of cloud_id or zone_id required)
    cloud_id: int | None = Field(default=None, alias="zoneId", description="Cloud/zone ID")
    group_id: int | None = Field(default=None, alias="siteId", description="Group/site ID")

    # Type configuration
    instance_type_code: str | None = Field(
        default=None,
        alias="instanceTypeCode",
        description="Instance type code (e.g., MTN-CS10)",
    )
    layout_id: int | None = Field(default=None, alias="layoutId", description="Layout ID")
    plan_id: int | None = Field(default=None, alias="planId", description="Service plan ID")

    # Optional fields
    description: str | None = Field(default=None, description="Instance description")

    # Configuration
    config: InstanceConfig | None = Field(default=None, description="Instance config")

    # Storage
    volumes: list[InstanceVolume] = Field(
        default_factory=list,
        description="Volumes to attach",
    )

    # Network
    network_interfaces: list[InstanceNetwork] = Field(
        default_factory=list,
        alias="networkInterfaces",
        description="Network interfaces",
    )

    # Labels
    labels: list[str] = Field(default_factory=list, description="Labels/tags")

    def to_api_payload(self) -> dict[str, Any]:
        """Convert to API request payload."""
        payload: dict[str, Any] = {
            "instance": {
                "name": self.name,
            }
        }

        instance = payload["instance"]

        if self.description:
            instance["description"] = self.description

        if self.instance_type_code:
            instance["instanceType"] = {"code": self.instance_type_code}

        if self.layout_id:
            instance["layout"] = {"id": self.layout_id}

        if self.plan_id:
            instance["plan"] = {"id": self.plan_id}

        if self.group_id:
            instance["site"] = {"id": self.group_id}

        if self.labels:
            instance["labels"] = self.labels

        # Config
        if self.config:
            config_dict = self.config.model_dump(by_alias=True, exclude_none=True)
            instance["config"] = config_dict

        # Cloud/Zone
        if self.cloud_id:
            payload["zoneId"] = self.cloud_id

        # Volumes
        if self.volumes:
            payload["volumes"] = [
                v.model_dump(by_alias=True, exclude_none=True) for v in self.volumes
            ]

        # Networks
        if self.network_interfaces:
            payload["networkInterfaces"] = [
                n.model_dump(by_alias=True, exclude_none=True) for n in self.network_interfaces
            ]

        return payload


class InstanceUpdate(BaseModel):
    """Model for updating an instance."""

    name: str | None = Field(default=None, description="New instance name")
    description: str | None = Field(default=None, description="New description")
    labels: list[str] | None = Field(default=None, description="New labels")

    def to_api_payload(self) -> dict[str, Any]:
        """Convert to API request payload."""
        instance: dict[str, Any] = {}

        if self.name is not None:
            instance["name"] = self.name
        if self.description is not None:
            instance["description"] = self.description
        if self.labels is not None:
            instance["labels"] = self.labels

        return {"instance": instance}
