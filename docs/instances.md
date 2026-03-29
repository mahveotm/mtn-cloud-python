# Instances

Use this guide for MTN Cloud instance provisioning and lifecycle operations.

## Before You Start

To work with instances, first order a project in:
`Provisioning -> Catalog`.

Ordering a project gives you the workspace context needed for provisioning,
including a resource pool.

## What Is a Resource Pool?

A resource pool is your isolated workspace on MTN Cloud where your compute,
storage, and network resources live.

In SDK terms, this maps to `resource_pool_id` used during instance creation.

## Typical Instance Flow

1. Authenticate.
2. Discover reference data (`group`, `cloud`, `instance type`, `plan`).
3. Create the instance.
4. Perform lifecycle actions (start, stop, restart, resize, delete).

## Create an Instance

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

instance = cloud.instances.create(
    name="app-server-01",
    cloud="MTNNG_CLOUD_AZ_1",
    type="MTN-CS10",
    group="MTNNG_CLOUD_AZ_1",
    layout=327,
    plan=6776,
    resource_pool_id="pool-214",   # from your project order context
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
instance.refresh()

cloud.instances.resize(instance.id, plan_id=6780)
```

## Discover Required IDs and Codes

```python
groups = cloud.groups.list()
clouds = cloud.clouds.list_openstack()
types = cloud.instance_types.list_os()
plans = cloud.plans.list()

print([(g.id, g.name) for g in groups[:5]])
print([(c.id, c.name) for c in clouds[:5]])
print([(t.code, t.default_layout_id) for t in types[:5]])
print([(p.id, p.name) for p in plans[:5]])
```

## Common Pitfalls

- Missing project/resource pool context in your account.
- Using hardcoded IDs from another tenant/environment.
- Creating before discovering valid `layout` and `plan` for your selected type.

