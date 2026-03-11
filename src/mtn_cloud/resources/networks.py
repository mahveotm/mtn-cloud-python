"""
Networks Resource
=================

Resource manager for MTN Cloud networks.
"""

from __future__ import annotations

from typing import Any

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.models.network import (
    Network,
    NetworkCreate,
    NetworkFloatingIP,
    NetworkTypeInfo,
    NetworkUpdate,
    Subnet,
)
from mtn_cloud.resources.base import BaseResource


class NetworksResource(BaseResource[Network]):
    """
    Manage MTN Cloud networks.

    Example:
        ```python
        # List networks
        networks = cloud.networks.list()

        # List networks for a specific cloud
        networks = cloud.networks.list(cloud_id=1)

        # Get network
        network = cloud.networks.get(123)
        ```
    """

    _path = "/networks"
    _model = Network
    _name = "network"
    _list_key = "networks"
    _item_key = "network"

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        name: str | None = None,
        cloud_id: int | None = None,
        **filters: Any,
    ) -> list[Network]:
        """
        List networks.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            sort: Field to sort by
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            name: Filter by name
            cloud_id: Filter by cloud/zone ID
            **filters: Additional filters

        Returns:
            List of networks
        """
        if name:
            filters["name"] = name
        if cloud_id:
            filters["zoneId"] = cloud_id

        return super().list(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        )

    def get(self, network_id: int) -> Network:
        """
        Get a network by ID.

        Args:
            network_id: Network ID

        Returns:
            Network object

        Raises:
            NotFoundError: If network not found
        """
        return super().get(network_id)

    def get_by_name(self, name: str, cloud_id: int | None = None) -> Network:
        """
        Get a network by name.

        Args:
            name: Network name
            cloud_id: Optional cloud ID to narrow search

        Returns:
            Network object

        Raises:
            NotFoundError: If network not found
        """
        networks = self.list(name=name, cloud_id=cloud_id, max_results=1)
        if not networks:
            raise NotFoundError(
                resource_type="Network",
                message=f"Network with name '{name}' not found",
            )
        return networks[0]

    def list_by_cloud(self, cloud_id: int) -> list[Network]:
        """
        List all networks in a specific cloud.

        Args:
            cloud_id: Cloud/zone ID

        Returns:
            List of networks in the cloud
        """
        return self.list(cloud_id=cloud_id)

    def create(
        self,
        name: str,
        *,
        cloud_id: int,
        group_id: int,
        type_id: int | None = None,
        display_name: str | None = None,
        labels: list[str] | None = None,
        description: str | None = None,
        cidr: str | None = None,
        gateway: str | None = None,
        dns_primary: str | None = None,
        dns_secondary: str | None = None,
        vlan_id: int | None = None,
        switch_id: str | None = None,
        pool_id: int | None = None,
        allow_static_override: bool | None = None,
        assign_public_ip: bool | None = None,
        active: bool | None = None,
        dhcp_server: bool | None = None,
        network_domain_id: int | None = None,
        search_domains: str | None = None,
        network_proxy_id: int | None = None,
        appliance_url_proxy_bypass: bool | None = None,
        no_proxy: str | None = None,
        visibility: str | None = None,
        tenant_ids: list[int] | None = None,
        resource_permission_all: bool | None = None,
        resource_permission_site_ids: list[int] | None = None,
    ) -> Network:
        """
        Create a network using MTN OpenStack-compatible fields.

        Notes:
            - Non-OpenStack provider-specific `config` variants are intentionally excluded.
            - Use integer IDs for cloud/group/type to keep payload typing uniform.
        """
        create_model = NetworkCreate(
            name=name,
            cloud_id=cloud_id,
            group_id=group_id,
            type_id=type_id,
            display_name=display_name,
            labels=labels,
            description=description,
            cidr=cidr,
            gateway=gateway,
            dns_primary=dns_primary,
            dns_secondary=dns_secondary,
            vlan_id=vlan_id,
            switch_id=switch_id,
            pool_id=pool_id,
            allow_static_override=allow_static_override,
            assign_public_ip=assign_public_ip,
            active=active,
            dhcp_server=dhcp_server,
            network_domain_id=network_domain_id,
            search_domains=search_domains,
            network_proxy_id=network_proxy_id,
            appliance_url_proxy_bypass=appliance_url_proxy_bypass,
            no_proxy=no_proxy,
            visibility=visibility,
            tenant_ids=tenant_ids,
            resource_permission_all=resource_permission_all,
            resource_permission_site_ids=resource_permission_site_ids,
        )
        payload = create_model.to_api_payload()
        return self._create(payload)

    def update(
        self,
        network_id: int,
        *,
        display_name: str | None = None,
        labels: list[str] | None = None,
        description: str | None = None,
        cidr: str | None = None,
        gateway: str | None = None,
        dns_primary: str | None = None,
        dns_secondary: str | None = None,
        vlan_id: int | None = None,
        switch_id: str | None = None,
        pool_id: int | None = None,
        allow_static_override: bool | None = None,
        assign_public_ip: bool | None = None,
        active: bool | None = None,
        dhcp_server: bool | None = None,
        network_domain_id: int | None = None,
        search_domains: str | None = None,
        network_proxy_id: int | None = None,
        appliance_url_proxy_bypass: bool | None = None,
        no_proxy: str | None = None,
        visibility: str | None = None,
        tenant_ids: list[int] | None = None,
        resource_permission_all: bool | None = None,
        resource_permission_site_ids: list[int] | None = None,
    ) -> Network:
        """
        Update a network using MTN OpenStack-compatible fields.

        Notes:
            - Non-OpenStack provider-specific `config` variants are intentionally excluded.
        """
        update_model = NetworkUpdate(
            display_name=display_name,
            labels=labels,
            description=description,
            cidr=cidr,
            gateway=gateway,
            dns_primary=dns_primary,
            dns_secondary=dns_secondary,
            vlan_id=vlan_id,
            switch_id=switch_id,
            pool_id=pool_id,
            allow_static_override=allow_static_override,
            assign_public_ip=assign_public_ip,
            active=active,
            dhcp_server=dhcp_server,
            network_domain_id=network_domain_id,
            search_domains=search_domains,
            network_proxy_id=network_proxy_id,
            appliance_url_proxy_bypass=appliance_url_proxy_bypass,
            no_proxy=no_proxy,
            visibility=visibility,
            tenant_ids=tenant_ids,
            resource_permission_all=resource_permission_all,
            resource_permission_site_ids=resource_permission_site_ids,
        )
        payload = update_model.to_api_payload()
        return self._update(network_id, payload)

    def delete(self, network_id: int) -> bool:
        """Delete a network by ID."""
        return self._delete(network_id)

    def list_subnets(self, network_id: int) -> list[Subnet]:
        """
        List all subnets for a network.

        Args:
            network_id: Network ID

        Returns:
            List of subnets under the specified network
        """
        path = f"{self._path}/{network_id}/subnets"
        response = self._http.get(path)
        subnets = response.get("subnets", [])
        return [Subnet.model_validate(subnet) for subnet in subnets]

    def list_types(
        self,
        name: str | None = None,
        code: str | None = None,
        phrase: str | None = None,
        openstack_only: bool = False,
    ) -> list[NetworkTypeInfo]:
        """
        List network types.

        Args:
            name: Optional exact name filter
            code: Optional exact code filter
            phrase: Optional phrase filter
            openstack_only: Return only network types tagged for OpenStack
        """
        params: dict[str, Any] = {}
        if name:
            params["name"] = name
        if code:
            params["code"] = code
        if phrase:
            params["phrase"] = phrase

        response = self._http.get("/network-types", params=params)
        types = [NetworkTypeInfo.model_validate(item) for item in response.get("networkTypes", [])]
        if openstack_only:
            return [network_type for network_type in types if network_type.is_openstack]
        return types

    def get_type(self, type_id: int) -> NetworkTypeInfo:
        """
        Get a network type by ID.

        Args:
            type_id: Network type ID
        """
        response = self._http.get(f"/network-types/{type_id}")
        item = response.get("networkType", response)
        return NetworkTypeInfo.model_validate(item)

    def list_floating_ips(
        self,
        *,
        phrase: str | None = None,
        ip_address: str | None = None,
        ip_status: str | None = None,
        cloud_id: int | None = None,
        server_id: int | None = None,
    ) -> list[NetworkFloatingIP]:
        """
        List floating IPs.

        This endpoint is primarily useful for OpenStack-based MTN Cloud zones.
        """
        params: dict[str, Any] = {}
        if phrase:
            params["phrase"] = phrase
        if ip_address:
            params["ipAddress"] = ip_address
        if ip_status:
            params["ipStatus"] = ip_status
        if cloud_id:
            params["zoneId"] = cloud_id
        if server_id:
            params["serverId"] = server_id

        response = self._http.get(f"{self._path}/floating-ips", params=params)
        items = response.get("networkFloatingIps", [])
        return [NetworkFloatingIP.model_validate(item) for item in items]

    def get_floating_ip(self, floating_ip_id: int) -> NetworkFloatingIP:
        """Get a floating IP by ID."""
        response = self._http.get(f"{self._path}/floating-ips/{floating_ip_id}")
        item = response.get("networkFloatingIp", response)
        return NetworkFloatingIP.model_validate(item)

    def allocate_floating_ip(
        self,
        *,
        network_server_id: int,
        floating_ip_pool_id: int,
    ) -> NetworkFloatingIP:
        """
        Allocate a floating IP.

        Args:
            network_server_id: Network server ID
            floating_ip_pool_id: Floating IP pool ID
        """
        payload = {
            "networkServerId": network_server_id,
            "floatingIpPoolId": floating_ip_pool_id,
        }
        response = self._http.post(f"{self._path}/floating-ips", json=payload)
        item = response.get("networkFloatingIp", response)
        return NetworkFloatingIP.model_validate(item)

    def release_floating_ip(self, floating_ip_id: int) -> bool:
        """Release a floating IP by ID."""
        self._http.put(f"{self._path}/floating-ips/{floating_ip_id}/release")
        return True
