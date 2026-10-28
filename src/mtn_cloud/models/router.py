"""Models for MTN Cloud routers."""

from typing import Annotated, Any

from pydantic import Field

from mtn_cloud.models.base import BaseModel, Resource
from mtn_cloud.models.network import ResourceReference

PositiveID = Annotated[int, Field(gt=0, strict=True)]


class RouterInterface(BaseModel):
    """An internal network attached to a router."""

    cidr: str | None = None
    network: ResourceReference | None = None


class Router(Resource):
    """A router returned by MTN Cloud."""

    status: str | None = None
    enabled: bool = True
    type: ResourceReference | None = None
    site: ResourceReference | None = None
    zone: ResourceReference | None = None
    external_network: ResourceReference | None = Field(default=None, alias="externalNetwork")
    external_ip: str | None = Field(default=None, alias="externalIp")
    external_id: str | None = Field(default=None, alias="externalId")
    interfaces: list[RouterInterface] = Field(default_factory=list)


class RouterCreate(BaseModel):
    """Typed inputs for creating an MTN neutronRouter."""

    name: str = Field(min_length=1)
    group_id: PositiveID
    cloud_id: PositiveID
    resource_pool_id: PositiveID
    internal_subnet_ids: list[PositiveID] = Field(min_length=1)
    external_network_id: PositiveID | None = None
    enabled: bool = True

    def to_api_payload(self, type_id: int) -> dict[str, Any]:
        """Build the MTN REST request using the resolved neutronRouter type ID."""
        pool_code = f"pool-{self.resource_pool_id}"
        router: dict[str, Any] = {
            "name": self.name,
            "site": {"id": self.group_id},
            "zone": {"id": self.cloud_id},
            "type": {"id": type_id},
            "poolId": pool_code,
            "config": {"poolId": pool_code},
            "enabled": self.enabled,
            "interfaces": [
                {"networkSubnet": {"id": subnet_id}}
                for subnet_id in dict.fromkeys(self.internal_subnet_ids)
            ],
        }
        if self.external_network_id is not None:
            router["externalNetwork"] = {"id": self.external_network_id}
        return {"networkRouter": router}
