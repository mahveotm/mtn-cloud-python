# Networking

Use this guide for creating and managing MTN Cloud networks via the SDK.

## Before You Start

- You need an existing Resource Pool (Project). Create one from **Provisioning → Catalog → Create Project** if you haven't already.
- MTN Cloud networking runs on OpenStack Neutron. Networks you create are private by default — VMs get private IPs automatically. Public internet access requires a floating IP and a router.
- Use `list_types(openstack_only=True)` to discover the valid network type IDs for your account.

## Typical Networking Flow

For internet-accessible VMs the full flow is:

1. Create a network (with CIDR, gateway, DHCP).
2. Create a Neutron router with the external network attached.
3. Attach your network to the router.
4. Provision instances on your network.
5. Allocate and assign a floating IP for public access.

## Discover Reference Data

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

groups = cloud.groups.list()
clouds = cloud.clouds.list_openstack()
network_types = cloud.networks.list_types(openstack_only=True)

print([(g.id, g.name) for g in groups[:5]])
print([(c.id, c.name) for c in clouds[:5]])
print([(t.id, t.name) for t in network_types[:5]])
```

## Create a Network

```python
networks = cloud.networks.list(cloud_id=1)
for network in networks[:5]:
    print(network.id, network.name, network.cidr)

new_network = cloud.networks.create(
    name="mtn-prod-net",
    cloud_id=1,                         # from clouds.list_openstack()
    group_id=621,                       # from groups.list()
    type_id=network_types[0].id,        # from list_types(openstack_only=True)
    cidr="10.42.10.0/24",
    gateway="10.42.10.1",
    dns_primary="8.8.8.8",
    visibility="private",
    dhcp_server=True,                   # enables automatic IP assignment
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

## Floating IP Operations

Floating IPs provide public internet access to a VM. They are allocated from a pool and can be reassigned between instances without changing the private IP.

```python
# List available floating IPs
ips = cloud.networks.list_floating_ips(cloud_id=1)
for ip in ips[:5]:
    print(ip.id, ip.ip_address, ip.ip_status)

# Allocate a new floating IP
allocated = cloud.networks.allocate_floating_ip(
    network_server_id=5,
    floating_ip_pool_id=1,
)
print(allocated.id, allocated.ip_address)
```

## Notes

- Many networking fields are OpenStack-specific. The SDK exposes the fields most relevant to MTN Cloud's environment.
- Always discover and validate IDs (`cloud_id`, `group_id`, `type_id`) for your own account — they are tenant-specific and differ between environments.
- Security groups (firewall rules) are separate from network configuration. Manage them in **Infrastructure → Network → Security Groups** in the console.
