# Networking

Use this guide for creating and managing MTN Cloud networks via the SDK.

## Before You Start

- Ensure you already have a project context (resource pool) from:
  `Provisioning -> Catalog`.
- Use `list_types(openstack_only=True)` first to discover valid network type IDs.

## What You Can Do

- List and filter networks.
- Create and update networks (OpenStack-focused fields).
- List network subnets.
- Work with floating IPs.

## List and Create Networks

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

networks = cloud.networks.list(cloud_id=1)
for network in networks[:5]:
    print(network.id, network.name, network.cidr)

network_types = cloud.networks.list_types(openstack_only=True)

new_network = cloud.networks.create(
    name="mtn-prod-net",
    cloud_id=1,
    group_id=621,
    type_id=network_types[0].id,
    cidr="10.42.10.0/24",
    gateway="10.42.10.1",
    dns_primary="8.8.8.8",
    visibility="private",
    dhcp_server=True,
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

## Floating IP Operations

```python
ips = cloud.networks.list_floating_ips(cloud_id=1)
for ip in ips[:5]:
    print(ip.id, ip.ip_address, ip.ip_status)

allocated = cloud.networks.allocate_floating_ip(
    network_server_id=5,
    floating_ip_pool_id=1,
)
print(allocated.id, allocated.ip_address)
```

## Delete a Network

```python
cloud.networks.delete(new_network.id)
```

## Notes

- Many networking fields are provider-specific; OpenStack-compatible fields are
  prioritized in this SDK.
- Always discover and validate IDs in the current tenant before provisioning.

