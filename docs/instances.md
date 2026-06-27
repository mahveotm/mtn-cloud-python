# Instances

Use this guide for MTN Cloud instance provisioning and lifecycle operations.

## Before You Start

Two things must be done in the MTN Cloud Console before you can provision instances via the SDK.

### 1. Create a Resource Pool

A **Resource Pool** (also called a Project) is your isolated compute workspace.
Every instance belongs to one and the SDK requires a `resource_pool_id` at creation time.

1. Go to **Provisioning → Catalog** and select **Create Project**.
2. Fill in: Group (e.g., `MTNNG_CLOUD_AZ_1`), Cloud, a unique project name, and an optional description. Example name format: `company-abc-api-2025`.
3. Click Order. **Wait approximately 10 minutes** — the pool is not immediately available.
4. Once ready, your `resource_pool_id` (e.g., `pool-214`) appears in the provisioning context.

One tenancy can have multiple resource pools, useful for isolating dev, staging, and production.

### 2. Set Up a Security Group

Security groups act as the firewall for your VMs, controlling which inbound and outbound traffic is allowed. Without one, the instance will provision but you will not be able to SSH or RDP into it.

1. Go to **Infrastructure → Network → Security Groups** in the console.
2. Create a group. Add inbound rules:
   - SSH port 22 (TCP) for Linux VMs.
   - RDP port 3389 (TCP) for Windows VMs.
   - Restrict the source IP to your range (e.g., `200.200.113.15/32` for a single machine).
3. Note the group name (e.g., `"default"` or your custom name).

Optionally, upload an SSH key pair under **User Settings → SSH Keys** for key-based access instead of passwords.

## What Is a Resource Pool?

A resource pool is your isolated workspace where compute, storage, and network resources live, separated from other tenants and projects. It maps directly to the `resource_pool_id` parameter in `instances.create()`. IDs are tenant-specific — never copy them from documentation or another account.

## Available Zones

MTN Cloud currently has two live availability zones:

| Zone | Code | Location |
|---|---|---|
| Lagos AZ1 | `MTNNG_CLOUD_AZ_1` | Lagos Island |
| Lagos AZ2 | `MTNNG_CLOUD_AZ_2` | Lagos Island |

Lagos AZ3 (Lagos Mainland) is in progress. Each zone has independent power, cooling, and network routing.

## Discover Required IDs and Codes

Run this before creating an instance. All IDs are account-specific.

Provisioning inputs are discovered from **groups, instance types, resource pools, and service plans** — all permission-safe endpoints. (The admin-level `clouds.list()` and `plans.list()` endpoints are restricted on most tenant accounts and will raise `ForbiddenError`; you do not need them.)

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

# 1. Group — gives you the group name AND its cloud/zone IDs
group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
cloud_id = group.cloud_ids[0]
print("group:", group.id, group.name, "cloud_ids:", group.cloud_ids)

# 2. Instance type — each carries its own default_layout_id
itype = cloud.instance_types.get_by_code("MTN-CS10")
print("type:", itype.code, "layout:", itype.default_layout_id)

# 3. Resource pool — where the instance is hosted (the resource_pool_id)
for pool in cloud.instances.list_resource_pools(group="MTNNG_CLOUD_AZ_1"):
    print("pool:", pool.code, pool.name)

# 4. Service plans — available CPU/memory/storage tiers for this zone + layout
for plan in cloud.instances.list_service_plans(
    zone_id=cloud_id,
    layout_id=itype.default_layout_id,
    group_id=group.id,
):
    print("plan:", plan["id"], plan["name"])
```

The `default_layout_id` on each instance type is the correct `layout` value to use for that type. Always read it from your account rather than hardcoding a value from an example.

### Resource Pools (the `resource_pool_id`)

A resource pool is **where your instance is hosted** — you cannot create an instance without one. List them by group name (the cloud/zone is resolved for you):

```python
# List every pool available to a group
for pool in cloud.instances.list_resource_pools(group="MTNNG_CLOUD_AZ_1"):
    print(pool.code, pool.name, "(default)" if pool.is_default else "")

# Or fetch a single pool by name (or by its code)
pool = cloud.instances.get_resource_pool(
    "my-project-Marv-Osuolale",
    group="MTNNG_CLOUD_AZ_1",
)
print(pool.code)   # e.g. "pool-214" — pass this as resource_pool_id
```

`pool.code` (e.g. `"pool-214"`) is the exact value `create()` expects. When passing it to `create()`, you can use the code (`"pool-214"`), the numeric ID (`214`), or its string form (`"214"`) — they are all normalized to the code internally.

If you already know the cloud and group IDs, pass them explicitly to skip the group lookup:

```python
pools = cloud.instances.list_resource_pools(cloud_id=4, group_id=621)
```

## Provision an Instance (guided)

`provision()` is the fastest way to create an instance: it takes the names you already know and resolves the numeric IDs for you — the layout from the type code, the plan from its name, and the resource pool from its name (or auto-selects it when the group has exactly one).

```python
instance = cloud.instances.provision(
    name="app-server-01",
    type="MTN-CS10",                    # type code -> resolves the layout
    group="MTNNG_CLOUD_AZ_1",           # also used as the cloud/zone
    plan="G2S4",                        # plan name (or pass a numeric plan ID)
    resource_pool="my-project",         # pool name; omit if the group has one pool
    availability_zone="Lagos-AZ-1-fd1",
    security_group="default",
)

# wait=True by default, so the instance is already running here
print(instance.id, instance.name, instance.status, instance.primary_ip)
```

If a name can't be resolved, the error tells you what's available (e.g. the valid plan names, or the pools to choose from). Set `wait=False` to return immediately, or `dry_run=True` to get the resolved config back without creating anything:

```python
config = cloud.instances.provision(
    name="app-server-01", type="MTN-CS10", group="MTNNG_CLOUD_AZ_1",
    plan="G2S4", resource_pool="my-project", dry_run=True,
)
# {"layout": 327, "plan": 6776, "resource_pool_id": "pool-214", ...}
```

Any extra keyword (labels, tags, volumes, network_interfaces, ports, …) passes straight through to `create()`.

## Create an Instance (explicit)

When you want full control over each ID, call `create()` directly. Resolve the inputs yourself first (see [Discover Required IDs](#discover-required-ids-and-codes)):

```python
pool = cloud.instances.get_resource_pool("my-project", group="MTNNG_CLOUD_AZ_1")

instance = cloud.instances.create(
    name="app-server-01",
    cloud="MTNNG_CLOUD_AZ_1",
    type="MTN-CS10",
    group="MTNNG_CLOUD_AZ_1",
    layout=327,                         # use default_layout_id from your type lookup
    plan=6776,                          # use a plan ID from list_service_plans()
    resource_pool_id=pool.code,         # e.g. "pool-214" (or pass 214 directly)
    availability_zone="Lagos-AZ-1-fd1",
    security_group="default",
)

print(instance.id, instance.name, instance.status, instance.primary_ip)
```

## Operate an Instance

```python
instance = cloud.instances.get(instance.id)

instance.stop()
instance.start()
instance.restart()
instance.suspend()   # suspends billing — resume with start()
instance.refresh()   # re-fetches latest state from API in-place

cloud.instances.resize(instance.id, plan_id=6780)
```

## Delete an Instance

```python
# Default: deletes the instance and its volumes
cloud.instances.delete(instance.id)

# Keep volumes after deleting the instance
cloud.instances.delete(instance.id, preserve_volumes=True)

# Force-delete a stuck or failed instance
cloud.instances.delete(instance.id, force=True)
```

## Wait for a Status

Use these helpers after triggering an action so your script blocks until the instance reaches the expected state. They poll every 5 seconds and raise `TimeoutError` if the timeout is exceeded.

```python
cloud.instances.stop(instance.id)
cloud.instances.wait_until_stopped(instance.id, timeout=120)

cloud.instances.start(instance.id)
cloud.instances.wait_until_running(instance.id, timeout=300)

# Wait for any specific status string
cloud.instances.wait_for_status(instance.id, "suspended", timeout=120)
```

## Snapshots

Snapshots capture the disk state of an instance at a point in time. Stop the instance before snapshotting to guarantee consistency.

```python
# Create a snapshot
snap = cloud.instances.create_snapshot(
    instance_id=123,
    name="pre-upgrade",
    description="State before OS upgrade",
)
print(snap.id, snap.name, snap.status)

# List all snapshots for an instance
snaps = cloud.instances.list_snapshots(instance_id=123)
for s in snaps:
    print(s.id, s.name, s.snapshot_created)

# Revert to a snapshot (instance must be stopped)
cloud.instances.stop(123)
cloud.instances.wait_until_stopped(123)
cloud.instances.revert_snapshot(instance_id=123, snapshot_id=snap.id)

# Delete a snapshot
cloud.instances.delete_snapshot(instance_id=123, snapshot_id=snap.id)
```

## Common Pitfalls

- **Resource pool not ready.** The SDK call will fail if you run it before the ~10 minute provisioning window completes. Wait and retry.
- **Security group blocks all access.** The instance provisions successfully but SSH/RDP fails. Set up inbound rules in the console before creating the instance.
- **Hardcoded IDs from examples.** Group, layout, and plan IDs are tenant-specific. Always look them up from your own account with `list()` calls.
- **Wrong layout for the instance type.** Each type has a `default_layout_id`. Use it — passing a layout ID from a different type will fail.
- **Windows password expiry.** The default Windows VM password expires after 42 days. Update it in both the OS and in the MTN Cloud console (User Settings) to keep them in sync.
