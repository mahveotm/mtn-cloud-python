# Networking

Use this guide for creating and managing MTN Cloud networks via the SDK.

## Before You Start

- You need an existing Resource Pool (Project). Create one from **Provisioning → Catalog → Create Project** if you haven't already.
- MTN Cloud networking runs on OpenStack Neutron. Networks you create are private by default — VMs get private IPs automatically. Public connectivity can be configured through an MTN router with a public network gateway, or through the instance's external network (`os_external_network_id`) at provisioning time. Router gateways and instance public IP assignment are separate operations.
- Use `list_types(openstack_only=True)` to discover the valid network type IDs for your account.

## Typical Networking Flow

1. Create a network (with CIDR, gateway, DHCP).
2. Provision instances on your network.
3. For public access, set `os_external_network_id` when creating the instance (see the [Instances guide](./instances.md)).

## Discover Reference Data

The `cloud_id` (zone) comes from the group — the admin-level `clouds.list()` endpoint is restricted on most tenant accounts and isn't needed.

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
cloud_id = group.cloud_ids[0]
network_types = cloud.networks.list_types(openstack_only=True)

print("group:", group.id, "cloud_id:", cloud_id)
print([(t.id, t.name) for t in network_types[:5]])
```

## Create a Network

An OpenStack network requires an OpenStack `type_id` and a `resource_pool_id` (the numeric pool ID — the network is created inside that resource pool). Pick a private network type and a pool:

```python
networks = cloud.networks.list(cloud_id=cloud_id)
for network in networks[:5]:
    print(network.id, network.name, network.cidr)

net_type = next(t for t in network_types if t.code == "openstackPrivate")
pool = cloud.instances.get_resource_pool("my-project", group=group.name)

new_network = cloud.networks.create(
    name="mtn-prod-net",
    cloud_id=cloud_id,                  # from group.cloud_ids[0]
    group_id=group.id,                  # from groups.get_by_name(...)
    type_id=net_type.id,                # an OpenStack type from list_types(openstack_only=True)
    resource_pool_id=pool.id,           # numeric pool ID from get_resource_pool(...)
    cidr="10.42.10.0/24",
    gateway="10.42.10.1",
    dns_primary="8.8.8.8",
)

print(new_network.id, new_network.name)
```

## Update and Inspect

```python
updated = cloud.networks.update(
    new_network.id,
    description="Production network",
    allow_static_override=True,
)

subnets = cloud.networks.list_subnets(updated.id)
print(f"Subnets: {len(subnets)}")
```

## Delete a Network

```python
cloud.networks.delete(new_network.id)
```

## Create an MTN Router

Use an existing resource pool, a public network, and an internal network in that
pool. Discover their IDs instead of copying them from the console. Resource pools
(projects) are distinct from the network IP pools described below.

```python
from mtn_cloud import MTNCloud

with MTNCloud() as cloud:  # Reads MTN_CLOUD_TOKEN
    group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
    if len(group.cloud_ids) != 1:
        raise ValueError("Select a cloud explicitly for this group.")
    cloud_id = group.cloud_ids[0]

    pool = cloud.instances.get_resource_pool(
        "my-project", group_id=group.id, cloud_id=cloud_id
    )
    public = cloud.networks.get_by_name("public-network-01", cloud_id=cloud_id)
    internal = cloud.networks.get_by_name("app-net", cloud_id=cloud_id)
    internal = cloud.networks.get(internal.id)
    if internal.zone_pool is None or internal.zone_pool.id != pool.id:
        raise ValueError("The internal network must belong to the selected resource pool.")
    subnets = cloud.networks.list_subnets(internal.id)

    router = cloud.routers.create(
        name="app-router",
        group_id=group.id,
        cloud_id=cloud_id,
        resource_pool_id=pool.id,
        external_network_id=public.id,
        internal_subnet_ids=[subnet.id for subnet in subnets],
    )
    print("Submitted router:", router.id)
    router = cloud.routers.wait_until_ready(router.id)
    print(router.id, router.status, router.external_ip)

    # When no longer needed:
    # cloud.routers.delete(router.id)
    # cloud.routers.wait_until_deleted(router.id)
```

This attaches all subnets returned for the internal network. To attach only one,
select it explicitly by name or CIDR. The IDs must be Morpheus subnet IDs, not
network IDs or OpenStack UUIDs. At least one subnet is required.

Only MTN's `neutronRouter` type is supported for creation and deletion. The SDK
selects the type automatically. `create()` submits provisioning and reads the
initial router record; use `wait_until_ready()` to confirm that it succeeded.
Both wait methods default to a five-minute timeout and five-second polling.

A provisioning failure raises `MTNCloudError`; waiting too long raises the SDK's
`TimeoutError`. These errors include the router ID in `error.response["router_id"]`.
A failed initial read after creation also preserves the ID there. Inspect or delete
that router explicitly; the SDK does not automatically remove failed routers.
Deleting a router leaves its existing networks and resource pool intact.

See the [Routers API reference](./api-reference/routers.md) for method details.

## Network Pools

Network pools are managed ranges of IP addresses used for static assignment. Inspect them and the individual addresses they track:

```python
# List pools with usage counts
for pool in cloud.networks.list_pools():
    print(pool.id, pool.name, f"{pool.free_count}/{pool.ip_count} free")
    for r in pool.ip_ranges:
        print("   range:", r.start_address, "-", r.end_address)

# Inspect a single pool and the addresses in use
pool = cloud.networks.get_pool(9)
for ip in cloud.networks.list_pool_ips(pool.id):
    print(ip.ip_address, ip.ip_type, ip.hostname)
```

## Notes

- Many networking fields are OpenStack-specific. The SDK exposes the fields most relevant to MTN Cloud's environment.
- Always discover and validate IDs (`cloud_id`, `group_id`, `type_id`) for your own account — they are tenant-specific and differ between environments.
- Security groups (firewall rules) are separate from network configuration. Manage them via `cloud.security_groups` — see the [Security Groups guide](./security-groups.md).
