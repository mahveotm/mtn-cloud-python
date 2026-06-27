"""Models for MTN Cloud resource pools."""

from __future__ import annotations

from pydantic import Field

from mtn_cloud.models.base import BaseModel


class ResourcePool(BaseModel):
    """
    A resource pool where an instance is hosted.

    Resource pools are the placement target for instances. You must know
    your resource pool ID before provisioning. Discover them with
    :meth:`InstancesResource.list_resource_pools`.

    The :attr:`code` (e.g. ``"pool-214"``) is what you pass as
    ``resource_pool_id`` to :meth:`InstancesResource.create`.

    Example:
        for pool in cloud.instances.list_resource_pools(cloud_id=4, group_id=621):
            print(f"{pool.code}: {pool.name}")
    """

    id: int = Field(..., description="Numeric resource pool ID")
    code: str = Field(
        ...,
        alias="value",
        description="Pool code used as resource_pool_id when creating instances (e.g. 'pool-214')",
    )
    name: str | None = Field(default=None, description="Resource pool display name")
    external_id: str | None = Field(
        default=None,
        alias="externalId",
        description="Underlying provider (OpenStack) pool ID",
    )
    is_default: bool = Field(
        default=False,
        alias="isDefault",
        description="Whether this is the default pool",
    )

    def __str__(self) -> str:
        """Return string representation with code and name."""
        return f"ResourcePool(id={self.id}, code={self.code!r}, name={self.name!r})"

    def __repr__(self) -> str:
        """Return detailed representation."""
        return self.__str__()
