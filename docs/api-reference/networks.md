# Resource: `cloud.networks` (`NetworksResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, cloud_id=None, **filters) -> list[Network]`

- Endpoint: `GET /api/networks`
- Parameters:
    - Shared list args
    - `name`: network name filter
    - `cloud_id`: mapped to query `zoneId`
- Returns: `list[Network]`
- Raises: common API exceptions

### `get(network_id: int) -> Network`

- Endpoint: `GET /api/networks/{network_id}`
- Returns: `Network`
- Raises: common API exceptions

### `get_by_name(name: str, cloud_id: int | None = None) -> Network`

- Endpoint sequence:
    - `GET /api/networks?name=<name>&max=1`
    - Adds `zoneId=<cloud_id>` when provided
- Returns: `Network`
- Raises:
    - common API exceptions
    - `NotFoundError` when no match

### `list_by_cloud(cloud_id: int) -> list[Network]`

- Endpoint: `GET /api/networks?zoneId=<cloud_id>`
- Returns: `list[Network]`
- Raises: common API exceptions

### `create(name: str, *, cloud_id: int, group_id: int, type_id=None, display_name=None, labels=None, description=None, cidr=None, gateway=None, dns_primary=None, dns_secondary=None, vlan_id=None, switch_id=None, pool_id=None, allow_static_override=None, assign_public_ip=None, active=None, dhcp_server=None, network_domain_id=None, search_domains=None, network_proxy_id=None, appliance_url_proxy_bypass=None, no_proxy=None, visibility=None, tenant_ids=None, resource_permission_all=None, resource_permission_site_ids=None) -> Network`

- Endpoint: `POST /api/networks`
- Parameters:
    - Required:
        - `name`: network name
        - `cloud_id`: cloud/zone ID
        - `group_id`: group/site ID
    - Common optional network config:
        - `type_id`, `display_name`, `labels`, `description`, `cidr`, `gateway`
        - `dns_primary`, `dns_secondary`, `vlan_id`, `switch_id`, `pool_id`
        - `allow_static_override`, `assign_public_ip`, `active`, `dhcp_server`
        - `network_domain_id`, `search_domains`, `network_proxy_id`
        - `appliance_url_proxy_bypass`, `no_proxy`, `visibility`
        - `tenant_ids`, `resource_permission_all`, `resource_permission_site_ids`
- Returns: `Network`
- Raises: common API exceptions

### `update(network_id: int, *, display_name=None, labels=None, description=None, cidr=None, gateway=None, dns_primary=None, dns_secondary=None, vlan_id=None, switch_id=None, pool_id=None, allow_static_override=None, assign_public_ip=None, active=None, dhcp_server=None, network_domain_id=None, search_domains=None, network_proxy_id=None, appliance_url_proxy_bypass=None, no_proxy=None, visibility=None, tenant_ids=None, resource_permission_all=None, resource_permission_site_ids=None) -> Network`

- Endpoint: `PUT /api/networks/{network_id}`
- Parameters:
    - `network_id`: target network ID
    - Optional fields mirror `create(...)` (except required create-only identifiers)
- Returns: `Network`
- Raises: common API exceptions

### `delete(network_id: int) -> bool`

- Endpoint: `DELETE /api/networks/{network_id}`
- Returns: `True`
- Raises: common API exceptions

### `list_subnets(network_id: int) -> list[Subnet]`

- Endpoint: `GET /api/networks/{network_id}/subnets`
- Returns: `list[Subnet]`
- Raises: common API exceptions

### `list_types(name=None, code=None, phrase=None, openstack_only=False) -> list[NetworkTypeInfo]`

- Endpoint: `GET /api/network-types`
- Parameters:
    - `name`: exact name filter
    - `code`: exact code filter
    - `phrase`: phrase filter
    - `openstack_only`: client-side filter on returned `is_openstack`
- Returns: `list[NetworkTypeInfo]`
- Raises: common API exceptions

### `get_type(type_id: int) -> NetworkTypeInfo`

- Endpoint: `GET /api/network-types/{type_id}`
- Returns: `NetworkTypeInfo`
- Raises: common API exceptions

### `list_pools(max_results=None, offset=0, phrase=None) -> list[NetworkPool]`

- Endpoint: `GET /api/networks/pools`
- Parameters:
    - `max_results`: maps to query `max`
    - `offset`: pagination offset
    - `phrase`: search phrase
- Returns: `list[NetworkPool]` (each includes its `ip_ranges`, `ip_count`, `free_count`)
- Raises: common API exceptions

### `get_pool(pool_id: int) -> NetworkPool`

- Endpoint: `GET /api/networks/pools/{pool_id}`
- Returns: `NetworkPool`
- Raises: common API exceptions

### `list_pool_ips(pool_id: int, *, max_results=None, phrase=None, ip_address=None, hostname=None) -> list[NetworkPoolIp]`

- Endpoint: `GET /api/networks/pools/{pool_id}/ips`
- Parameters:
    - `max_results`: maps to query `max`
    - `phrase`: partial match on `ipAddress` or `hostname`
    - `ip_address`: exact IP match
    - `hostname`: exact hostname match
- Returns: `list[NetworkPoolIp]`
- Raises: common API exceptions

> **Note:** Standalone floating-IP endpoints (`/api/networks/floating-ips`) are restricted (HTTP 403) on MTN Cloud tenant accounts and are not exposed by the SDK. Assign external/public connectivity at provisioning time via the instance's `os_external_network_id` instead.

