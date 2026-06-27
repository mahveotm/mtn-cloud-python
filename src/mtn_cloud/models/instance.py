"""Models for MTN Cloud compute instances and payload builders."""

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

    id: int | None = Field(default=-1, description="Volume ID (-1 for new volumes)")
    name: str = "root"
    size: int = Field(..., description="Volume size in GB")
    size_id: int | None = Field(default=None, alias="sizeId")
    storage_type: int | None = Field(default=None, alias="storageType")
    datastore_id: str | None = Field(default="auto", alias="datastoreId")
    root_volume: bool = Field(default=True, alias="rootVolume")


class InstanceNetwork(BaseModel):
    """Network interface configuration for an instance."""

    id: int | None = None
    network_id: str | None = Field(
        default=None, alias="networkId", description="Network ID (e.g., 'network-298')"
    )
    ip_address: str | None = Field(default=None, alias="ipAddress")
    ip_mode: str | None = Field(
        default=None, alias="ipMode", description="IP mode: 'static', 'dhcp', or 'pool'"
    )

    # API responses embed the full network object instead of only the ID.
    network: dict[str, Any] | None = None

    def to_api_payload(self) -> dict[str, Any]:
        """Convert to API request payload for network interface."""
        payload: dict[str, Any] = {}

        if self.network_id:
            payload["network"] = {"id": self.network_id}
        elif self.network:
            payload["network"] = self.network

        if self.ip_address:
            payload["ipAddress"] = self.ip_address
            payload["ipMode"] = self.ip_mode or "static"
        elif self.ip_mode:
            payload["ipMode"] = self.ip_mode

        return payload


class InstanceConfig(BaseModel):
    """
    MTN Cloud instance configuration options.

    These are the configuration options for provisioning instances on MTN Cloud.
    """

    resource_pool_id: str | None = Field(
        default=None,
        alias="resourcePoolId",
        description="Resource pool ID (e.g., 'pool-214')",
    )
    availability_zone: str | None = Field(
        default=None,
        alias="availabilityZone",
        description="Availability zone (e.g., 'Lagos-AZ-1-fd1')",
    )
    security_group: str | None = Field(
        default=None,
        alias="securityGroup",
        description="Security group name (e.g., 'default')",
    )
    os_external_network_id: str | None = Field(
        default=None,
        alias="osExternalNetworkId",
        description="External network for floating IP (e.g., 'public-network-01')",
    )
    create_user: bool | None = Field(
        default=True, alias="createUser", description="Create your user on the instance"
    )


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
        # Get instance details
        instance = cloud.instances.get(123)
        print(f"Name: {instance.name}")
        print(f"Status: {instance.status}")
        print(f"IP: {instance.primary_ip}")

        # Perform actions
        instance.stop()
        instance.start()
    """

    description: str | None = Field(default=None, description="Instance description")

    status: str = Field(default="unknown", description="Current instance status")
    status_message: str | None = Field(
        default=None,
        alias="statusMessage",
        description="Status details",
    )

    instance_type: InstanceType | None = Field(default=None, alias="instanceType")
    plan: InstancePlan | None = None
    layout: dict[str, Any] | None = None

    cloud: dict[str, Any] | None = Field(default=None, description="Cloud/zone info")
    group: dict[str, Any] | None = Field(default=None, alias="site", description="Group/site info")

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

    volumes: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Attached volumes",
    )

    config: dict[str, Any] | None = Field(default=None, description="Instance config")

    max_memory: int | None = Field(default=None, alias="maxMemory")
    max_cores: int | None = Field(default=None, alias="maxCores")
    max_storage: int | None = Field(default=None, alias="maxStorage")

    labels: list[str] = Field(default_factory=list, description="Instance labels")
    tags: list[dict[str, Any]] = Field(default_factory=list, description="Instance tags")

    provisioned_date: datetime | None = Field(default=None, alias="dateProvisioned")

    # Bound by resource managers so model instances can expose convenience actions.
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
        for field in self.model_fields.keys():
            if hasattr(updated, field):
                setattr(self, field, getattr(updated, field))
        return self


class InstanceCreate(BaseModel):
    """
    Model for creating a new instance on MTN Cloud.

    Based on the Morpheus API specification for instance provisioning.

    Example:
        # MTN Cloud instance creation
        instance = cloud.instances.create(
            name="MyInstanceName",
            cloud="MTNNG_CLOUD_AZ_1",
            type="MTN-CS10",
            group="MTNNG_CLOUD_AZ_1",
            layout=327,
            plan=6923,
            resource_pool_id="pool-214",
            availability_zone="Lagos-AZ-1-fd1",
            security_group="default",
            os_external_network_id="public-network-01",
            volumes=[
                InstanceVolume(name="root", size=10, storage_type=11),
            ],
            network_interfaces=[
                InstanceNetwork(network_id="network-298", ip_address="192.168.100.40"),
            ],
        )
    """

    name: str = Field(..., min_length=1, max_length=255, description="Instance name")
    cloud: str = Field(..., description="Cloud name (e.g., 'MTNNG_CLOUD_AZ_1')")
    type: str = Field(..., description="Instance Type code (e.g., 'MTN-CS10')")
    group_id: int = Field(..., description="Group ID (resolved from group name)")
    layout: int = Field(..., description="Layout ID (e.g., 327)")
    plan: int = Field(..., description="Service plan ID (e.g., 6923)")

    description: str | None = Field(default=None, description="Instance description")
    environment: str | None = Field(default=None, description="Environment code")

    labels: list[str] = Field(default_factory=list, description="Labels (keywords)")
    tags: dict[str, str] | list[dict[str, str]] = Field(
        default_factory=dict, description="Metadata tags"
    )

    copies: int = Field(default=1, description="Number of copies to provision")
    layout_size: int = Field(
        default=1, alias="layoutSize", description="Multiply factor of containers/vms"
    )

    resource_pool_id: str = Field(
        ...,
        min_length=1,
        description="Resource pool ID (e.g., 'pool-214')",
    )
    availability_zone: str | None = Field(
        default=None, description="Availability zone (e.g., 'Lagos-AZ-1-fd1')"
    )
    security_group: str | None = Field(
        default=None, description="Security group name (e.g., 'default')"
    )
    os_external_network_id: str | None = Field(
        default=None,
        description="External network for floating IP (e.g., 'public-network-01')",
    )
    create_user: bool = Field(default=True, description="Create your user on the instance")

    workflow_id: int | None = Field(default=None, description="Workflow ID")
    shutdown_days: int | None = Field(default=None, description="Shutdown days")
    expire_days: int | None = Field(default=None, description="Expiration days")
    create_backup: bool | None = Field(default=None, description="Create backups")

    security_groups: list[str] | None = Field(default=None, description="Security group names")
    ports: list[dict[str, Any]] | None = Field(default=None, description="Exposed ports")
    volumes: list[InstanceVolume] = Field(default_factory=list, description="Volumes to attach")
    network_interfaces: list[InstanceNetwork] = Field(
        default_factory=list,
        description="Network interfaces",
    )
    options: dict[str, Any] = Field(default_factory=dict, description="Additional options")

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
        if self.environment:
            instance["instanceContext"] = self.environment

        instance["cloud"] = self.cloud
        instance["site"] = {"id": self.group_id}
        instance["type"] = self.type
        instance["instanceType"] = {"code": self.type}
        instance["layout"] = {"id": self.layout}
        instance["plan"] = {"id": self.plan}

        if self.labels:
            instance["labels"] = self.labels

        if self.tags:
            if isinstance(self.tags, dict):
                instance["tags"] = [{"name": k, "value": v} for k, v in self.tags.items()]
            else:
                instance["tags"] = self.tags

        config: dict[str, Any] = {}
        config["resourcePoolId"] = self.resource_pool_id

        if self.availability_zone is not None:
            config["availabilityZone"] = self.availability_zone
        if self.security_group is not None:
            config["securityGroup"] = self.security_group
        if self.os_external_network_id is not None:
            config["osExternalNetworkId"] = self.os_external_network_id
        if self.create_user is not None:
            config["createUser"] = self.create_user
        if self.shutdown_days is not None:
            config["shutdownDays"] = str(self.shutdown_days)
        if self.expire_days is not None:
            config["expireDays"] = str(self.expire_days)
        if self.create_backup is not None:
            config["createBackup"] = self.create_backup

        if self.options:
            config.update(self.options)

        if config:
            payload["config"] = config

        if self.copies != 1:
            payload["copies"] = self.copies

        payload["layoutSize"] = self.layout_size

        if self.workflow_id:
            payload["taskSetId"] = self.workflow_id

        if self.security_groups:
            payload["securityGroups"] = [{"id": sg} for sg in self.security_groups]

        if self.ports:
            payload["ports"] = self.ports

        if self.volumes:
            payload["volumes"] = [v.model_dump(by_alias=True) for v in self.volumes]

        if self.network_interfaces:
            payload["networkInterfaces"] = [n.to_api_payload() for n in self.network_interfaces]

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
