# Security Groups

Use this guide to manage MTN Cloud security groups and their firewall rules via the SDK.

## What Security Groups Do

Security groups are the firewall layer for MTN Cloud instances. They control which traffic is allowed to reach your VMs (inbound/ingress) and leave them (outbound/egress). Without the right rules, your instance will provision but you will not be able to SSH, RDP, or reach it over any port.

Every instance gets a security group at provisioning time. You can create and configure groups before creating instances, then reference them by name in `instances.create()`.

## List and Inspect

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

# List all security groups
for sg in cloud.security_groups.list():
    print(f"{sg.id}  {sg.name}  ({len(sg.rules)} rules)")

# Get a specific group with its rules
sg = cloud.security_groups.get(583)
for rule in sg.rules:
    print(f"  {rule.direction}  {rule.protocol}  port={rule.port_range}  policy={rule.policy}")

# Find by name
sg = cloud.security_groups.get_by_name("default")
```

## Create a Security Group

```python
sg = cloud.security_groups.create(
    name="web-servers",
    description="HTTP, HTTPS, and SSH access",
)
print(sg.id, sg.name)
```

## Add Rules

Rules are always added after creating the group. The most common pattern is ingress rules for the ports your application uses.

```python
# Allow SSH from anywhere (narrow this to your IP range in production)
cloud.security_groups.create_rule(
    sg.id,
    name="allow-ssh",
    direction="ingress",
    protocol="tcp",
    port_range="22",
)

# Allow HTTPS from anywhere
cloud.security_groups.create_rule(
    sg.id,
    name="allow-https",
    direction="ingress",
    protocol="tcp",
    port_range="443",
)

# Allow HTTP from anywhere
cloud.security_groups.create_rule(
    sg.id,
    name="allow-http",
    direction="ingress",
    protocol="tcp",
    port_range="80",
)

# Allow RDP (Windows VMs)
cloud.security_groups.create_rule(
    sg.id,
    name="allow-rdp",
    direction="ingress",
    protocol="tcp",
    port_range="3389",
)
```

### Restrict by Source IP

To limit access to a specific CIDR range, set `source_type="cidr"` and pass `source`:

```python
cloud.security_groups.create_rule(
    sg.id,
    name="allow-ssh-corp",
    direction="ingress",
    protocol="tcp",
    port_range="22",
    source_type="cidr",
    source="200.200.113.0/24",   # your office/VPN range
)
```

### Port Ranges

`port_range` accepts a single port (`"22"`) or a range (`"8000-9000"`).

## Update a Group

```python
cloud.security_groups.update(sg.id, description="Updated description")
```

## Remove a Rule

```python
sg = cloud.security_groups.get(sg.id)   # fetch current rules
rule_to_remove = sg.rules[0]
cloud.security_groups.delete_rule(sg.id, rule_to_remove.id)
```

## Delete a Security Group

Deleting a group that is still attached to a running instance will fail. Detach or delete the instance first.

```python
cloud.security_groups.delete(sg.id)
```

## Use a Security Group When Provisioning

Pass the group name in `instances.create()`:

```python
instance = cloud.instances.create(
    name="app-server-01",
    cloud="MTNNG_CLOUD_AZ_1",
    type="MTN-CS10",
    group="MTNNG_CLOUD_AZ_1",
    layout=327,
    plan=6776,
    resource_pool_id="pool-214",
    security_group="web-servers",    # name of the group you created
)
```

## Common Pitfalls

- **Group name vs ID.** `instances.create()` takes the group **name** (`security_group="web-servers"`). Other methods in this resource take the numeric **ID**.
- **No rules = no access.** An empty security group blocks all inbound traffic. Always add at least one ingress rule for the port you need.
- **Deleting a group in use.** The delete call will be rejected by the API if the group is still attached to an active instance.
