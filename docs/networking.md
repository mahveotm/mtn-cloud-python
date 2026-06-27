# Networking

Use this guide for creating and managing MTN Cloud networks via the SDK.

## Before You Start

- You need an existing Resource Pool (Project). Create one from **Provisioning → Catalog → Create Project** if you haven't already.
- MTN Cloud networking runs on OpenStack Neutron. Networks you create are private by default — VMs get private IPs automatically. Public internet access is configured at provisioning time via the instance's external network (`os_external_network_id`), not through a standalone floating-IP API.
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
