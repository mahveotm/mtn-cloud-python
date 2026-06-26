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

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

groups = cloud.groups.list()
clouds = cloud.clouds.list_openstack()
types = cloud.instance_types.list_os()
plans = cloud.plans.list()

print([(g.id, g.name) for g in groups[:5]])
print([(c.id, c.name) for c in clouds[:5]])
print([(t.code, t.default_layout_id) for t in types[:5]])
print([(p.id, p.name) for p in plans[:5]])
```

The `default_layout_id` on each instance type is the correct `layout` value to use for that type. Always read it from your account rather than hardcoding a value from an example.

## Create an Instance

```python
instance = cloud.instances.create(
    name="app-server-01",
    cloud="MTNNG_CLOUD_AZ_1",
    type="MTN-CS10",
    group="MTNNG_CLOUD_AZ_1",
    layout=327,                         # use default_layout_id from your type lookup
    plan=6776,                          # use plan ID from your plans lookup
    resource_pool_id="pool-214",        # from your project order
    availability_zone="Lagos-AZ-1-fd1",
    security_group="default",           # security group name from the console
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

## Common Pitfalls

- **Resource pool not ready.** The SDK call will fail if you run it before the ~10 minute provisioning window completes. Wait and retry.
- **Security group blocks all access.** The instance provisions successfully but SSH/RDP fails. Set up inbound rules in the console before creating the instance.
- **Hardcoded IDs from examples.** Group, layout, and plan IDs are tenant-specific. Always look them up from your own account with `list()` calls.
- **Wrong layout for the instance type.** Each type has a `default_layout_id`. Use it — passing a layout ID from a different type will fail.
- **Windows password expiry.** The default Windows VM password expires after 42 days. Update it in both the OS and in the MTN Cloud console (User Settings) to keep them in sync.
