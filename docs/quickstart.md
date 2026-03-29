# Quickstart

This guide helps you go from zero to useful operations quickly.

## 1. Install

```bash
pip install mtn-cloud
```

## 2. Authenticate

Choose one method.

```python
from mtn_cloud import MTNCloud

# Option A: token (recommended)
cloud = MTNCloud(token="your-api-token")

# Option B: environment variable
# export MTN_CLOUD_TOKEN="your-api-token"
cloud = MTNCloud()

# Option C: username/password
cloud = MTNCloud(username="user@example.com", password="your-password")
```

## 3. Verify Connectivity

```python
user = cloud.whoami()
print(f"Connected as: {user.username} ({user.email})")
print("Ping:", cloud.ping())
```

## 4. Understand Platform Prerequisites

- For instances, order a project from `Provisioning -> Catalog`.
- For storage, order MTN Object Storage from the same Catalog section.

Then read:
- [Instances](./instances.md)
- [Networking](./networking.md)
- [Storage](./storage.md)

## 5. Discover Core Reference Data

Before creating resources, discover your valid IDs and codes.

```python
groups = cloud.groups.list()
clouds = cloud.clouds.list_openstack()
instance_types = cloud.instance_types.list_os()
plans = cloud.plans.list()

print("Groups:", [(g.id, g.name) for g in groups[:5]])
print("Clouds:", [(c.id, c.name) for c in clouds[:5]])
print("Instance types:", [(t.code, t.default_layout_id) for t in instance_types[:5]])
print("Plans:", [(p.id, p.name, p.cores, p.memory_gb) for p in plans[:5]])
```

## 6. Create an Instance

```python
instance = cloud.instances.create(
    name="my-first-instance",
    cloud="MTNNG_CLOUD_AZ_1",
    type="MTN-CS10",
    group="MTNNG_CLOUD_AZ_1",
    layout=327,
    plan=6923,
)

print(instance.id, instance.name, instance.status, instance.primary_ip)
```

## 7. Operate an Instance

```python
instance = cloud.instances.get(instance.id)
instance.stop()
instance.start()
instance.refresh()
print(instance.status)
```

## 8. Work with Storage + Archives

```python
# Create storage provider (S3-compatible)
storage = cloud.storage_buckets.create_s3(
    name="my-s3-storage",
    bucket_name="my-bucket",
    access_key="AKIA...",
    secret_key="...",
    endpoint="https://s3.example.com",
)

# Create archive bucket attached to that storage provider
archive = cloud.archive_buckets.create(
    name="my-archive-bucket",
    storage_provider_id=storage.id,
    visibility="private",
)

# Upload a file
uploaded = cloud.archive_buckets.upload_file(
    bucket_name=archive.name,
    remote_path="/",
    local_path="./README.md",
)
print(uploaded.id, uploaded.name)
```

## 9. Minimal Error Handling

```python
from mtn_cloud import MTNCloudError, NotFoundError, ValidationError

try:
    cloud.instances.get(999999)
except NotFoundError:
    print("Instance does not exist")
except ValidationError as exc:
    print(f"Validation failed: {exc}")
except MTNCloudError as exc:
    print(f"SDK/API error: {exc}")
```

## Next Step

Continue with the [Advanced Cookbook](./advanced-cookbook.md) for production-oriented patterns.
