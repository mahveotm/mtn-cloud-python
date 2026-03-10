"""
Network Models
==============

Models for MTN Cloud networks.
"""

from enum import Enum
from typing import Any, Optional
from pydantic import Field

from mtn_cloud.models.base import Resource


class NetworkType(str, Enum):
    """Network types."""

    VLAN = "vlan"
    VXLAN = "vxlan"
    FLAT = "flat"
    GRE = "gre"
    EXTERNAL = "external"
    INTERNAL = "internal"


class Network(Resource):
    """
    MTN Cloud network.

    Represents a virtual network that instances can connect to.

    Example:
        ```python
        # List networks
        for network in cloud.networks.list():
            print(f"{network.name}: {network.cidr}")

        # Get specific network
        network = cloud.networks.get(123)
        ```
    """

    # Network details
    description: Optional[str] = Field(default=None, description="Network description")
    code: Optional[str] = Field(default=None, description="Network code")

    # Type
    type: Optional[str] = Field(default=None, alias="typeCode", description="Network type")
    type_id: Optional[int] = Field(default=None, alias="typeId")

    # Configuration
    cidr: Optional[str] = Field(default=None, description="CIDR block")
    gateway: Optional[str] = Field(default=None, description="Gateway IP")
    dns_primary: Optional[str] = Field(default=None, alias="dnsPrimary")
    dns_secondary: Optional[str] = Field(default=None, alias="dnsSecondary")

    # VLAN
    vlan_id: Optional[int] = Field(default=None, alias="vlanId")

    # Cloud/Zone
    zone: Optional[dict[str, Any]] = Field(default=None, description="Zone/cloud info")

    # Status
    active: bool = Field(default=True, description="Whether network is active")
    visibility: Optional[str] = Field(default=None, description="Network visibility")

    # DHCP
    dhcp_server: Optional[bool] = Field(default=None, alias="dhcpServer")
    dhcp_range_start: Optional[str] = Field(default=None, alias="dhcpRangeStart")
    dhcp_range_end: Optional[str] = Field(default=None, alias="dhcpRangeEnd")

    # External reference
    external_id: Optional[str] = Field(default=None, alias="externalId")

    @property
    def cloud_id(self) -> Optional[int]:
        """Get the cloud/zone ID."""
        if self.zone:
            return self.zone.get("id")
        return None


class Subnet(Resource):
    """Network subnet."""

    cidr: Optional[str] = Field(default=None, description="Subnet CIDR")
    gateway: Optional[str] = Field(default=None, description="Subnet gateway")
    network_id: Optional[int] = Field(default=None, alias="networkId")

    # Pool info
    pool: Optional[dict[str, Any]] = Field(default=None)

    # DHCP
    dhcp_server: Optional[bool] = Field(default=None, alias="dhcpServer")

    active: bool = Field(default=True)

