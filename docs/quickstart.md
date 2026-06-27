# Quickstart

This guide takes you from zero to provisioning real resources on MTN Cloud without needing to read the full platform documentation.

## 1. Install

```bash
pip install mtn-cloud
```

## 2. Authenticate

**Get your API token** from the MTN Cloud Console:
User icon (top-right) → **User Settings** → **API Access** → copy the token.

```python
from mtn_cloud import MTNCloud

# Option A: token (recommended)
cloud = MTNCloud(token="your-api-token")

# Option B: environment variable — no code change needed per environment
# export MTN_CLOUD_TOKEN="your-api-token"
cloud = MTNCloud()

# Option C: username/password
cloud = MTNCloud(username="user@example.com", password="your-password")
# Note: organisations using Active Directory/SSO must use SubDomain\Username
# format instead of email (e.g., r"mysubdomain\john.doe").
```

## 3. Verify Connectivity

```python
user = cloud.whoami()
print(f"Connected as: {user.username} ({user.email})")
print("Ping:", cloud.ping())
```

## 4. Platform Prerequisites

The SDK manages resources that must first be set up through the MTN Cloud Console. Do these steps once per project — they take a few minutes each.

### Create a Resource Pool (required before instances)

A **Resource Pool** (also called a Project) is your isolated compute workspace.
Every instance you create via the SDK belongs to one.

1. In the console, go to **Provisioning → Catalog** and select **Create Project**.
2. Fill in: Group (e.g., `MTNNG_CLOUD_AZ_1`), Cloud, a unique project name, and an optional description.
3. Click Order. **Wait approximately 10 minutes** for provisioning to complete.
4. Your `resource_pool_id` (e.g., `pool-214`) will appear in the provisioning context once ready.

One tenancy can have multiple resource pools — useful for separating dev, staging, and production.

### Set up a security group (required before instances)

Security groups are the firewall layer for your VMs. Without one, you will not be able to SSH or RDP in after provisioning.

You can create one either in the console (**Infrastructure → Network → Security Groups**) or directly with the SDK:

```python
# Create the group
sg = cloud.security_groups.create(
    name="web-servers",
    description="SSH + HTTPS access",
)

# Allow SSH from a single machine (use 3389/tcp instead for Windows RDP)
cloud.security_groups.create_rule(
    sg.id,
    name="allow-ssh",
    direction="ingress",
    protocol="tcp",
    port_range="22",
    source_type="cidr",
    source="200.200.113.15/32",   # restrict to your IP range
)
```

The group name (e.g., `"web-servers"` or `"default"`) is passed as the `security_group` parameter when creating an instance. See the [Security Groups guide](./security-groups.md) for the full workflow.

Optionally, add an SSH key pair under **User Settings → SSH Keys** for key-based access.

### Order MTN Object Storage (required before storage)

1. Go to **Provisioning → Catalog** and select **MTN Object Storage → Order Now**.
2. The platform generates your credentials — the status shows "submitted".
3. Your **access key**, **secret key**, and **endpoint URL** arrive by email.

The Lagos endpoint is: `https://ps1csp-s3.ict.mtn.com.ng:9021`

Keep the credentials from that email — you will pass them directly into the SDK.

## 5. Discover Core Reference Data

Before creating resources, look up the valid IDs and codes for your account. These are tenant-specific and cannot be copied from documentation or other accounts. Everything below uses permission-safe endpoints — the admin-level `clouds.list()` and `plans.list()` are restricted on most tenant accounts and aren't needed.

```python
# Group — also carries the cloud/zone IDs you need
group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
cloud_id = group.cloud_ids[0]

# Instance type — carries its own default_layout_id
itype = cloud.instance_types.get_by_code("MTN-CS10")

# Resource pool — the resource_pool_id, where the instance is hosted
pools = cloud.instances.list_resource_pools(group=group.name)

# Service plans — CPU/memory/storage tiers for this zone + layout
plans = cloud.instances.list_service_plans(
    zone_id=cloud_id,
    layout_id=itype.default_layout_id,
    group_id=group.id,
)

print("group:", group.id, "cloud_id:", cloud_id)
print("layout:", itype.default_layout_id)
print("pools:", [(p.code, p.name) for p in pools[:5]])
print("plans:", [(pl["id"], pl["name"]) for pl in plans[:5]])
```

MTN Cloud currently has two live zones: **Lagos AZ1** (`MTNNG_CLOUD_AZ_1`) and **Lagos AZ2** (`MTNNG_CLOUD_AZ_2`).

## 6. Create an Instance

Replace `resource_pool_id` with the value from your project order, and `security_group` with the group you created.

```python
instance = cloud.instances.create(
    name="my-first-instance",
    cloud="MTNNG_CLOUD_AZ_1",
    type="MTN-CS10",
    group="MTNNG_CLOUD_AZ_1",
    layout=327,
    plan=6923,
    resource_pool_id=pools[0].code,     # from list_resource_pools() above
    availability_zone="Lagos-AZ-1-fd1",
    security_group="web-servers",       # the security group you created above
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

## 8. Work with Storage and Archives

Use the access key, secret key, and endpoint from the email you received after ordering MTN Object Storage.

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

# Register the storage provider with your MOS credentials
storage = cloud.storage_buckets.create_s3(
    name="my-s3-storage",
    bucket_name="my-bucket",
    access_key="your-access-key",                         # from email
    secret_key="your-secret-key",                         # from email
    endpoint="https://ps1csp-s3.ict.mtn.com.ng:9021",    # Lagos endpoint
    create_bucket=True,
)

# Create a logical archive bucket on top of the storage provider
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
from mtn_cloud import (
    MTNCloudError,
    NotFoundError,
    QuotaExceededError,
    ResourceConflictError,
    ValidationError,
)

try:
    cloud.instances.get(999999)
except NotFoundError:
    print("Instance does not exist")
except ValidationError as exc:
    print(f"Validation failed: {exc}")
except QuotaExceededError as exc:
    print(f"Quota exceeded: {exc.quota_type} ({exc.current}/{exc.limit})")
except ResourceConflictError as exc:
    print(f"Conflict: {exc}")
except MTNCloudError as exc:
    print(f"SDK/API error: {exc}")
```

## Next Step

Continue with the [Advanced Cookbook](./advanced-cookbook.md) for production-oriented patterns.
