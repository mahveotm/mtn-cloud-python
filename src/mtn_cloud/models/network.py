"""
Network Models
==============

Models for MTN Cloud networks.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

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
    description: str | None = Field(default=None, description="Network description")
    code: str | None = Field(default=None, description="Network code")

    # Type - can come as dict or string from API
    type: dict[str, Any] | str | None = Field(default=None, description="Network type info")
    type_id: int | None = Field(default=None, alias="typeId")

    # Configuration
    cidr: str | None = Field(default=None, description="CIDR block")
    gateway: str | None = Field(default=None, description="Gateway IP")
    dns_primary: str | None = Field(default=None, alias="dnsPrimary")
    dns_secondary: str | None = Field(default=None, alias="dnsSecondary")

    # VLAN
    vlan_id: int | None = Field(default=None, alias="vlanId")

    # Cloud/Zone
    zone: dict[str, Any] | None = Field(default=None, description="Zone/cloud info")

    # Status
    active: bool = Field(default=True, description="Whether network is active")
    visibility: str | None = Field(default=None, description="Network visibility")

    # DHCP
    dhcp_server: bool | None = Field(default=None, alias="dhcpServer")
    dhcp_range_start: str | None = Field(default=None, alias="dhcpRangeStart")
    dhcp_range_end: str | None = Field(default=None, alias="dhcpRangeEnd")

    # External reference
    external_id: str | None = Field(default=None, alias="externalId")

    @property
    def type_code(self) -> str | None:
        """Get the network type code."""
        if isinstance(self.type, dict):
            return self.type.get("code")
        return self.type

    @property
    def type_name(self) -> str | None:
        """Get the network type name."""
        if isinstance(self.type, dict):
            return self.type.get("name")
        return self.type

    @property
    def cloud_id(self) -> int | None:
        """Get the cloud/zone ID."""
        if self.zone:
            return self.zone.get("id")
        return None


class Subnet(Resource):
    """Network subnet."""

    cidr: str | None = Field(default=None, description="Subnet CIDR")
    gateway: str | None = Field(default=None, description="Subnet gateway")
    network_id: int | None = Field(default=None, alias="networkId")

    # Pool info
    pool: dict[str, Any] | None = Field(default=None)

    # DHCP
    dhcp_server: bool | None = Field(default=None, alias="dhcpServer")

    active: bool = Field(default=True)
