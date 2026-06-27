"""Models and payload builders for MTN Cloud networking resources."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from mtn_cloud.models.base import BaseModel, Resource


class NetworkType(str, Enum):
    """Network types."""

    VLAN = "vlan"
    VXLAN = "vxlan"
    FLAT = "flat"
    GRE = "gre"
    EXTERNAL = "external"
    INTERNAL = "internal"


class NetworkVisibility(str, Enum):
    """Network visibility."""

    PRIVATE = "private"
    PUBLIC = "public"


class ResourceReference(BaseModel):
    """Common reference object used across network payloads."""

    id: int
    name: str | None = None
    code: str | None = None
    type: str | None = None


class ResourcePermission(BaseModel):
    """Group-level resource permissions."""

    all: bool | None = None
    sites: list[ResourceReference] = Field(default_factory=list)


class Network(Resource):
    """
    MTN Cloud network.

    Represents a virtual network that instances can connect to.

    Example:
        # List networks
        for network in cloud.networks.list():
            print(f"{network.name}: {network.cidr}")

        # Get specific network
        network = cloud.networks.get(123)
    """

    display_name: str | None = Field(default=None, alias="displayName")
    labels: list[str] = Field(default_factory=list)
    description: str | None = Field(default=None, description="Network description")
    code: str | None = Field(default=None, description="Network code")

    type: ResourceReference | None = Field(default=None, description="Network type info")
    type_id: int | None = Field(default=None, alias="typeId")

    ipv4_enabled: bool | None = Field(default=None, alias="ipv4Enabled")
    ipv6_enabled: bool | None = Field(default=None, alias="ipv6Enabled")
    cidr: str | None = Field(default=None, description="CIDR block")
    gateway: str | None = Field(default=None, description="Gateway IP")
    dns_primary: str | None = Field(default=None, alias="dnsPrimary")
    dns_secondary: str | None = Field(default=None, alias="dnsSecondary")
    switch_id: str | None = Field(default=None, alias="switchId")

    vlan_id: int | None = Field(default=None, alias="vlanId")

    zone: ResourceReference | None = Field(default=None, description="Zone/cloud info")
    group: ResourceReference | None = Field(default=None)
    owner: ResourceReference | None = Field(default=None)
    pool: ResourceReference | None = Field(default=None)
    zone_pool: ResourceReference | None = Field(default=None, alias="zonePool")
    network_domain: ResourceReference | None = Field(default=None, alias="networkDomain")
    network_proxy: ResourceReference | None = Field(default=None, alias="networkProxy")

    active: bool = Field(default=True, description="Whether network is active")
    visibility: str | None = Field(default=None, description="Network visibility")
    status: str | None = Field(default=None)
    allow_static_override: bool | None = Field(default=None, alias="allowStaticOverride")
    assign_public_ip: bool | None = Field(default=None, alias="assignPublicIp")
    appliance_url_proxy_bypass: bool | None = Field(default=None, alias="applianceUrlProxyBypass")
    no_proxy: str | None = Field(default=None, alias="noProxy")

    dhcp_server: bool | None = Field(default=None, alias="dhcpServer")
    dhcp_server_ipv6: bool | None = Field(default=None, alias="dhcpServerIPv6")
    search_domains: str | None = Field(default=None, alias="searchDomains")
    tenants: list[ResourceReference] = Field(default_factory=list)
    resource_permission: ResourcePermission | None = Field(default=None, alias="resourcePermission")
    config: dict[str, Any] | None = Field(default=None)

    external_id: str | None = Field(default=None, alias="externalId")

    @property
    def type_code(self) -> str | None:
        """Get the network type code."""
        if self.type:
            return self.type.code
        return None

    @property
    def type_name(self) -> str | None:
        """Get the network type name."""
        if self.type:
            return self.type.name
        return None

    @property
    def cloud_id(self) -> int | None:
        """Get the cloud/zone ID."""
        if self.zone:
            return self.zone.id
        return None


class Subnet(Resource):
    """Network subnet."""

    code: str | None = Field(default=None)
    description: str | None = Field(default=None)
    labels: list[str] = Field(default_factory=list)
    external_id: str | None = Field(default=None, alias="externalId")
    unique_id: str | None = Field(default=None, alias="uniqueId")
    address_prefix: str | None = Field(default=None, alias="addressPrefix")
    cidr: str | None = Field(default=None, description="Subnet CIDR")
    gateway: str | None = Field(default=None, description="Subnet gateway")
    netmask: str | None = Field(default=None)
    subnet_address: str | None = Field(default=None, alias="subnetAddress")
    network: ResourceReference | None = Field(default=None)
    type: ResourceReference | None = Field(default=None)

    pool: str | None = Field(default=None)

    dhcp_server: bool | None = Field(default=None, alias="dhcpServer")
    dhcp_ip: str | None = Field(default=None, alias="dhcpIp")
    dhcp_start: str | None = Field(default=None, alias="dhcpStart")
    dhcp_end: str | None = Field(default=None, alias="dhcpEnd")
    dhcp_range: str | None = Field(default=None, alias="dhcpRange")
    dns_primary: str | None = Field(default=None, alias="dnsPrimary")
    dns_secondary: str | None = Field(default=None, alias="dnsSecondary")

    search_domains: str | None = Field(default=None, alias="searchDomains")
    visibility: str | None = Field(default=None)
    assign_public_ip: bool | None = Field(default=None, alias="assignPublicIp")
    has_floating_ips: bool | None = Field(default=None, alias="hasFloatingIps")
    active: bool = Field(default=True)

    @property
    def network_id(self) -> int | None:
        """Get parent network ID."""
        if self.network:
            return self.network.id
        return None


class NetworkPoolRange(BaseModel):
    """A contiguous IP range within a network pool."""

    id: int
    start_address: str | None = Field(default=None, alias="startAddress")
    end_address: str | None = Field(default=None, alias="endAddress")
    external_id: str | None = Field(default=None, alias="externalId")
    description: str | None = Field(default=None)


class NetworkPool(Resource):
    """
    A network IP pool — a managed range of addresses for static assignment.

    Example:
        for pool in cloud.networks.list_pools():
            print(f"{pool.name}: {pool.free_count}/{pool.ip_count} free")
    """

    display_name: str | None = Field(default=None, alias="displayName")
    description: str | None = Field(default=None)
    type: ResourceReference | None = Field(default=None, description="Pool type info")
    account: ResourceReference | None = Field(default=None)
    gateway: str | None = Field(default=None)
    netmask: str | None = Field(default=None)
    subnet_address: str | None = Field(default=None, alias="subnetAddress")
    dns_domain: str | None = Field(default=None, alias="dnsDomain")
    ip_count: int | None = Field(default=None, alias="ipCount")
    free_count: int | None = Field(default=None, alias="freeCount")
    pool_enabled: bool | None = Field(default=None, alias="poolEnabled")
    ip_ranges: list[NetworkPoolRange] = Field(default_factory=list, alias="ipRanges")


class NetworkPoolIp(Resource):
    """An individual IP address tracked within a network pool."""

    network_pool_id: int | None = Field(default=None, alias="networkPoolId")
    ip_type: str | None = Field(default=None, alias="ipType")
    ip_address: str | None = Field(default=None, alias="ipAddress")
    gateway_address: str | None = Field(default=None, alias="gatewayAddress")
    interface_name: str | None = Field(default=None, alias="interfaceName")
    description: str | None = Field(default=None)
    active: bool | None = Field(default=None)
    fqdn: str | None = Field(default=None)
    hostname: str | None = Field(default=None)


class NetworkTypeInfo(Resource):
    """Network type metadata used when creating/updating networks."""

    code: str
    description: str | None = Field(default=None)
    category: str | None = Field(default=None)
    creatable: bool = Field(default=False)
    deletable: bool = Field(default=False)
    has_cidr: bool = Field(default=False, alias="hasCidr")
    has_floating_ips: bool = Field(default=False, alias="hasFloatingIps")
    option_types: list[dict[str, Any]] = Field(default_factory=list, alias="optionTypes")

    @property
    def is_openstack(self) -> bool:
        """Return True if this network type belongs to OpenStack."""
        category = (self.category or "").lower()
        code = self.code.lower()
        return "openstack" in category or "openstack" in code


class NetworkCreate(BaseModel):
    """Create network payload builder constrained to MTN OpenStack-compatible fields."""

    name: str
    cloud_id: int
    group_id: int
    type_id: int | None = None
    resource_pool_id: int | None = None
    display_name: str | None = Field(default=None, alias="displayName")
    labels: list[str] | None = None
    description: str | None = None
    cidr: str | None = None
    gateway: str | None = None
    dns_primary: str | None = Field(default=None, alias="dnsPrimary")
    dns_secondary: str | None = Field(default=None, alias="dnsSecondary")
    vlan_id: int | None = Field(default=None, alias="vlanId")
    switch_id: str | None = Field(default=None, alias="switchId")
    pool_id: int | None = None
    allow_static_override: bool | None = Field(default=None, alias="allowStaticOverride")
    assign_public_ip: bool | None = Field(default=None, alias="assignPublicIp")
    active: bool | None = None
    dhcp_server: bool | None = Field(default=None, alias="dhcpServer")
    network_domain_id: int | None = None
    search_domains: str | None = Field(default=None, alias="searchDomains")
    network_proxy_id: int | None = None
    appliance_url_proxy_bypass: bool | None = Field(default=None, alias="applianceUrlProxyBypass")
    no_proxy: str | None = Field(default=None, alias="noProxy")
    visibility: NetworkVisibility | None = None
    tenant_ids: list[int] | None = None
    resource_permission_all: bool | None = None
    resource_permission_site_ids: list[int] | None = None

    def to_api_payload(self) -> dict[str, Any]:
        """Convert model to Morpheus API create payload."""
        network: dict[str, Any] = {
            "name": self.name,
            "site": {"id": self.group_id},
            "zone": {"id": self.cloud_id},
        }

        if self.type_id is not None:
            network["type"] = {"id": self.type_id}
        if self.resource_pool_id is not None:
            network["zonePool"] = {"id": self.resource_pool_id}
        if self.display_name is not None:
            network["displayName"] = self.display_name
        if self.labels is not None:
            network["labels"] = self.labels
        if self.description is not None:
            network["description"] = self.description
        if self.cidr is not None:
            network["cidr"] = self.cidr
        if self.gateway is not None:
            network["gateway"] = self.gateway
        if self.dns_primary is not None:
            network["dnsPrimary"] = self.dns_primary
        if self.dns_secondary is not None:
            network["dnsSecondary"] = self.dns_secondary
        if self.vlan_id is not None:
            network["vlanId"] = self.vlan_id
        if self.switch_id is not None:
            network["switchId"] = self.switch_id
        if self.pool_id is not None:
            network["pool"] = self.pool_id
        if self.allow_static_override is not None:
            network["allowStaticOverride"] = self.allow_static_override
        if self.assign_public_ip is not None:
            network["assignPublicIp"] = self.assign_public_ip
        if self.active is not None:
            network["active"] = self.active
        if self.dhcp_server is not None:
            network["dhcpServer"] = self.dhcp_server
        if self.network_domain_id is not None:
            network["networkDomain"] = {"id": self.network_domain_id}
        if self.search_domains is not None:
            network["searchDomains"] = self.search_domains
        if self.network_proxy_id is not None:
            network["networkProxy"] = {"id": self.network_proxy_id}
        if self.appliance_url_proxy_bypass is not None:
            network["applianceUrlProxyBypass"] = self.appliance_url_proxy_bypass
        if self.no_proxy is not None:
            network["noProxy"] = self.no_proxy
        if self.visibility is not None:
            network["visibility"] = (
                self.visibility if isinstance(self.visibility, str) else self.visibility.value
            )
        if self.tenant_ids is not None:
            network["tenants"] = [{"id": tenant_id} for tenant_id in self.tenant_ids]
        if (
            self.resource_permission_all is not None
            or self.resource_permission_site_ids is not None
        ):
            resource_permission: dict[str, Any] = {}
            if self.resource_permission_all is not None:
                resource_permission["all"] = self.resource_permission_all
            if self.resource_permission_site_ids is not None:
                resource_permission["sites"] = self.resource_permission_site_ids
            network["resourcePermission"] = resource_permission

        return {"network": network}


class NetworkUpdate(BaseModel):
    """Update network payload builder constrained to MTN OpenStack-compatible fields."""

    display_name: str | None = Field(default=None, alias="displayName")
    labels: list[str] | None = None
    description: str | None = None
    cidr: str | None = None
    gateway: str | None = None
    dns_primary: str | None = Field(default=None, alias="dnsPrimary")
    dns_secondary: str | None = Field(default=None, alias="dnsSecondary")
    vlan_id: int | None = Field(default=None, alias="vlanId")
    switch_id: str | None = Field(default=None, alias="switchId")
    pool_id: int | None = None
    allow_static_override: bool | None = Field(default=None, alias="allowStaticOverride")
    assign_public_ip: bool | None = Field(default=None, alias="assignPublicIp")
    active: bool | None = None
    dhcp_server: bool | None = Field(default=None, alias="dhcpServer")
    network_domain_id: int | None = None
    search_domains: str | None = Field(default=None, alias="searchDomains")
    network_proxy_id: int | None = None
    appliance_url_proxy_bypass: bool | None = Field(default=None, alias="applianceUrlProxyBypass")
    no_proxy: str | None = Field(default=None, alias="noProxy")
    visibility: NetworkVisibility | None = None
    tenant_ids: list[int] | None = None
    resource_permission_all: bool | None = None
    resource_permission_site_ids: list[int] | None = None

    def to_api_payload(self) -> dict[str, Any]:
        """Convert model to Morpheus API update payload."""
        network: dict[str, Any] = {}

        if self.display_name is not None:
            network["displayName"] = self.display_name
        if self.labels is not None:
            network["labels"] = self.labels
        if self.description is not None:
            network["description"] = self.description
        if self.cidr is not None:
            network["cidr"] = self.cidr
        if self.gateway is not None:
            network["gateway"] = self.gateway
        if self.dns_primary is not None:
            network["dnsPrimary"] = self.dns_primary
        if self.dns_secondary is not None:
            network["dnsSecondary"] = self.dns_secondary
        if self.vlan_id is not None:
            network["vlanId"] = self.vlan_id
        if self.switch_id is not None:
            network["switchId"] = self.switch_id
        if self.pool_id is not None:
            network["pool"] = self.pool_id
        if self.allow_static_override is not None:
            network["allowStaticOverride"] = self.allow_static_override
        if self.assign_public_ip is not None:
            network["assignPublicIp"] = self.assign_public_ip
        if self.active is not None:
            network["active"] = self.active
        if self.dhcp_server is not None:
            network["dhcpServer"] = self.dhcp_server
        if self.network_domain_id is not None:
            network["networkDomain"] = {"id": self.network_domain_id}
        if self.search_domains is not None:
            network["searchDomains"] = self.search_domains
        if self.network_proxy_id is not None:
            network["networkProxy"] = {"id": self.network_proxy_id}
        if self.appliance_url_proxy_bypass is not None:
            network["applianceUrlProxyBypass"] = self.appliance_url_proxy_bypass
        if self.no_proxy is not None:
            network["noProxy"] = self.no_proxy
        if self.visibility is not None:
            network["visibility"] = (
                self.visibility if isinstance(self.visibility, str) else self.visibility.value
            )
        if self.tenant_ids is not None:
            network["tenants"] = [{"id": tenant_id} for tenant_id in self.tenant_ids]
        if (
            self.resource_permission_all is not None
            or self.resource_permission_site_ids is not None
        ):
            permissions: dict[str, Any] = {}
            if self.resource_permission_all is not None:
                permissions["all"] = self.resource_permission_all
            if self.resource_permission_site_ids is not None:
                permissions["sites"] = [
                    {"id": site_id} for site_id in self.resource_permission_site_ids
                ]
            network["resourcePermissions"] = permissions

        return {"network": network}
