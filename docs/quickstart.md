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

1. Go to **Infrastructure → Network → Security Groups** and create a group.
2. Add an inbound rule: SSH port 22 (TCP) for Linux VMs, or RDP port 3389 (TCP) for Windows VMs.
3. Restrict the source to your IP range, e.g., `200.200.113.15/32` for a single machine.

The group name (e.g., `"default"`) is passed as the `security_group` parameter when creating an instance.

Optionally, add an SSH key pair under **User Settings → SSH Keys** for key-based access.

### Order MTN Object Storage (required before storage)

1. Go to **Provisioning → Catalog** and select **MTN Object Storage → Order Now**.
2. The platform generates your credentials — the status shows "submitted".
3. Your **access key**, **secret key**, and **endpoint URL** arrive by email.

The Lagos endpoint is: `https://ps1csp-s3.ict.mtn.com.ng:9021`

Keep the credentials from that email — you will pass them directly into the SDK.

## 5. Discover Core Reference Data

Before creating resources, look up the valid IDs and codes for your account. These are tenant-specific and cannot be copied from documentation or other accounts.

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
    resource_pool_id="pool-214",        # from your project order
    availability_zone="Lagos-AZ-1-fd1",
    security_group="default",           # security group name from the console
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
