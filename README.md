# MTN Cloud Python SDK

[![PyPI version](https://badge.fury.io/py/mtn-cloud.svg)](https://badge.fury.io/py/mtn-cloud)
[![Tests](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/test.yml/badge.svg)](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/test.yml)
[![Docs](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/docs.yml/badge.svg)](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/docs.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Modern Python SDK for [MTN Cloud](https://console.cloud.mtn.ng) with typed models, clear resource managers, and practical workflows for compute, networking, storage, archives, security groups, backups, and more.

Docs: [mtn-cloud-python](https://mahveotm.github.io/mtn-cloud-python/)

> **Disclaimer:** Unofficial community project. Not affiliated with MTN Nigeria.

## Why You'll Like It

- Simple Pythonic API across core MTN Cloud resources
- Typed Pydantic models with IDE autocomplete
- Built-in retry behavior and timeout controls
- Token or username/password authentication
- Structured exceptions for better error handling
- Examples for real-world automation scripts

## Installation

```bash
pip install mtn-cloud
```

## Documentation

- [Docs Index](https://mahveotm.github.io/mtn-cloud-python/)
- [Quickstart](https://mahveotm.github.io/mtn-cloud-python/quickstart/)
- [Instances](https://mahveotm.github.io/mtn-cloud-python/instances/)
- [Networking](https://mahveotm.github.io/mtn-cloud-python/networking/)
- [Storage](https://mahveotm.github.io/mtn-cloud-python/storage/)
- [Security Groups](https://mahveotm.github.io/mtn-cloud-python/security-groups/)
- [Backups](https://mahveotm.github.io/mtn-cloud-python/backups/)
- [Virtual Images](https://mahveotm.github.io/mtn-cloud-python/virtual-images/)
- [Advanced Cookbook](https://mahveotm.github.io/mtn-cloud-python/advanced-cookbook/)
- [API Overview](https://mahveotm.github.io/mtn-cloud-python/api-overview/)
- [API Reference](https://mahveotm.github.io/mtn-cloud-python/api-reference/)

## Quick Start

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

# Verify auth and connectivity
user = cloud.whoami()
print(f"Connected as: {user.username}")
print("Ping:", cloud.ping())

# List a few running instances
running = cloud.instances.list(status="running", max_results=5)
for instance in running:
    print(instance.id, instance.name, instance.status, instance.primary_ip)
```

## Authentication

```python
from mtn_cloud import MTNCloud

# Option 1: token (recommended)
cloud = MTNCloud(token="your-api-token")

# Option 2: environment variable
# export MTN_CLOUD_TOKEN="your-api-token"
cloud = MTNCloud()

# Option 3: username/password
cloud = MTNCloud(username="user@example.com", password="your-password")
```

Get your API token from MTN Cloud Console:
User Icon (top-right) -> User Settings -> API Access.

## What You Can Do

### 1. Discover Reference Data

Use these lookups before provisioning so your scripts stay deterministic. They all use permission-safe endpoints (the admin-level `clouds`/`plans` endpoints are restricted on most tenant accounts — you don't need them).

```python
# Groups (sites) — also carry the cloud/zone IDs you need
group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
print(group.id, group.name, group.cloud_ids)

# Instance types — each carries its own default_layout_id
itype = cloud.instance_types.get_by_code("MTN-CS10")
print(itype.code, itype.default_layout_id)

# Resource pools — where the instance is hosted (the resource_pool_id)
for pool in cloud.instances.list_resource_pools(group="MTNNG_CLOUD_AZ_1"):
    print(pool.code, pool.name)

# Service plans — CPU/memory/storage tiers for this zone + layout
for plan in cloud.instances.list_service_plans(
    zone_id=group.cloud_ids[0],
    layout_id=itype.default_layout_id,
    group_id=group.id,
):
    print(plan["id"], plan["name"])
```

A **resource pool is required** to create an instance — it's where the VM is hosted. `provision()` (below) discovers it for you; or fetch one yourself with `cloud.instances.get_resource_pool("my-project", group="MTNNG_CLOUD_AZ_1")`.

### 2. Create an Instance

The guided `provision()` resolves layout, plan, and resource pool from names — the fastest path:

```python
instance = cloud.instances.provision(
    name="web-01",
    type="MTN-CS10",                # type code
    group="MTNNG_CLOUD_AZ_1",       # also used as the cloud/zone
    plan="G2S4",                    # plan name (or numeric id)
    resource_pool="my-project",     # pool name; auto-selected if the group has only one
)
print(instance.id, instance.status, instance.primary_ip)
```

For full control over every ID, use `create()` directly:

```python
instance = cloud.instances.create(
    name="web-01",
    cloud="MTNNG_CLOUD_AZ_1",
    type="MTN-CS10",
    group="MTNNG_CLOUD_AZ_1",
    layout=327,
    plan=6776,
    resource_pool_id="pool-214",    # or the numeric ID 214
    labels=["production", "web"],
)
```

### 3. Manage an Instance

```python
instance = cloud.instances.get(123)
print(instance.name, instance.status, instance.primary_ip)

# Action methods from model
instance.stop()
instance.start()
instance.restart()
instance.refresh()

# Or from resource manager
cloud.instances.resize(123, plan_id=6780)
cloud.instances.delete(123, force=True, preserve_volumes=True)
```

### 4. Work with Networks

```python
group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")

# List networks
networks = cloud.networks.list(cloud_id=group.cloud_ids[0])
for n in networks[:5]:
    print(n.id, n.name, n.cidr)

# Create an OpenStack network (needs an OpenStack type + a resource pool)
net_type = next(
    t for t in cloud.networks.list_types(openstack_only=True)
    if t.code == "openstackPrivate"
)
pool = cloud.instances.get_resource_pool("my-project", group=group.name)

new_network = cloud.networks.create(
    name="mtn-prod-net",
    cloud_id=group.cloud_ids[0],
    group_id=group.id,
    type_id=net_type.id,
    resource_pool_id=pool.id,
    cidr="10.42.10.0/24",
    gateway="10.42.10.1",
    dns_primary="8.8.8.8",
)

# Inspect subnets
subnets = cloud.networks.list_subnets(new_network.id)
print(f"Subnets: {len(subnets)}")
```

### 5. Manage Security Groups

```python
# Create a security group and add rules
sg = cloud.security_groups.create(
    name="web-servers",
    description="HTTP, HTTPS, and SSH access",
)

cloud.security_groups.create_rule(
    sg.id,
    name="allow-ssh",
    direction="ingress",
    protocol="tcp",
    port_range="22",
)

cloud.security_groups.create_rule(
    sg.id,
    name="allow-https",
    direction="ingress",
    protocol="tcp",
    port_range="443",
)

# Use the security group when provisioning
instance = cloud.instances.create(
    name="app-server-01",
    cloud="MTNNG_CLOUD_AZ_1",
    type="MTN-CS10",
    group="MTNNG_CLOUD_AZ_1",
    layout=327,
    plan=6776,
    resource_pool_id="pool-214",
    security_group="web-servers",
)
```

### 6. Snapshot Instances

```python
# Create a snapshot before a risky operation
snap = cloud.instances.create_snapshot(
    instance_id=instance.id,
    name="pre-upgrade",
)

# Revert if something goes wrong (stop the instance first)
cloud.instances.stop(instance.id)
cloud.instances.wait_until_stopped(instance.id)
cloud.instances.revert_snapshot(instance.id, snapshot_id=snap.id)
```

### 7. Work with Backups

```python
# List configured backups and their status
for backup in cloud.backups.list():
    print(f"{backup.name}: last_run={backup.last_run} status={backup.last_status}")

# Trigger an immediate backup run
cloud.backups.execute(backup_id=42)

# Check execution history
for result in cloud.backups.list_results(backup_id=42):
    print(f"{result.start_date}: {result.status} ({result.size_in_mb} MB)")

# List and execute backup jobs (schedules)
for job in cloud.backups.list_jobs():
    print(f"{job.name}: cron={job.cron_expression}")
```

### 8. Work with Storage and Archives

```python
# Create S3-compatible storage provider
storage = cloud.storage_buckets.create_s3(
    name="my-s3-storage",
    bucket_name="my-app-objects",
    access_key="your-access-key",
    secret_key="your-secret-key",
    endpoint="https://ps1csp-s3.ict.mtn.com.ng:9021",
    create_bucket=True,
)

# Create archive bucket linked to storage provider
archive = cloud.archive_buckets.create(
    name="my-app-archives",
    storage_provider_id=storage.id,
    visibility="private",
)

# Upload one file
uploaded = cloud.archive_buckets.upload_file(
    bucket_name=archive.name,
    remote_path="/",
    local_path="./backup.sql",
)
print(uploaded.id, uploaded.name)

# Upload a directory (preserves local folder structure)
summary = cloud.archive_buckets.upload_directory(
    bucket_name=archive.name,
    remote_path="/imports/",
    local_directory="./reports",
    recursive=True,
)
print(
    f"scanned={summary.scanned_count} "
    f"uploaded={summary.uploaded_count} "
    f"failed={summary.failed_count} "
    f"skipped={summary.skipped_count}"
)

# List and download
files = cloud.archive_buckets.list_files(bucket_name=archive.name, remote_path="/", full_tree=True)
if files:
    content = cloud.archive_buckets.download_file(
        bucket_name=archive.name,
        remote_path=files[0].file_path or files[0].name,
    )
    print(f"Downloaded {len(content)} byte(s)")
```

Storage vs archive model:
- `cloud.storage_buckets`: provider configuration (endpoint, credentials, backing bucket)
- `cloud.archive_buckets`: logical file container attached to a provider
- file operations happen through archive APIs


## Error Handling

```python
from mtn_cloud import (
    AuthenticationError,
    MTNCloudError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    ResourceConflictError,
    ValidationError,
)

try:
    cloud.instances.get(999999)
except NotFoundError:
    print("Resource not found")
except AuthenticationError:
    print("Authentication failed")
except ValidationError as exc:
    print(f"Validation error: {exc}")
except QuotaExceededError as exc:
    print(f"Quota exceeded: {exc.quota_type} ({exc.current}/{exc.limit})")
except ResourceConflictError as exc:
    print(f"Conflict: {exc}")
except RateLimitError as exc:
    print(f"Rate limited, retry_after={exc.retry_after}")
except MTNCloudError as exc:
    print(f"SDK/API error: {exc}")
```

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MTN_CLOUD_TOKEN` | API access token | - |
| `MTN_CLOUD_USERNAME` | Login username (alternative to token) | - |
| `MTN_CLOUD_PASSWORD` | Login password (alternative to token) | - |
| `MTN_CLOUD_URL` | API base URL | `https://console.cloud.mtn.ng` |
| `MTN_CLOUD_TIMEOUT` | Request timeout in seconds | `30` |
| `MTN_CLOUD_MAX_RETRIES` | Maximum retry attempts | `3` |
| `MTN_CLOUD_RETRY_DELAY` | Retry backoff factor | `1.0` |
| `MTN_CLOUD_VERIFY_SSL` | Enable SSL verification | `true` |
| `MTN_CLOUD_USER_AGENT` | Application identity appended to the SDK user agent | - |
| `MTN_CLOUD_DEBUG` | Enable bounded, secret-redacted HTTP debug logs | `false` |

Programmatic configuration:

```python
from mtn_cloud import MTNCloud, MTNCloudConfig

config = MTNCloudConfig(
    token="your-token",
    timeout=60,
    max_retries=5,
    retry_delay=1.5,
    verify_ssl=True,
    user_agent="my-automation/1.0",  # appended after the required SDK identity
)

cloud = MTNCloud(config=config)
```

Tokens and passwords are stored as masked Pydantic secret values, and debug
logging recursively redacts credential-shaped fields. The transport retries
transient failures only for safe read methods (`GET`, `HEAD`, and `OPTIONS`);
create, update, action, and delete requests are never status-retried automatically.

The default `mtn-cloud-python/<version>` user-agent prefix is required by the
MTN Cloud API edge. A configured `user_agent` is treated as an application
suffix so the SDK identity is preserved.

## Examples

| Script | What it demonstrates |
|--------|-----------------------|
| `examples/basic_usage.py` | Auth, connectivity, resource listing |
| `examples/create_instance.py` | End-to-end instance creation scaffold |
| `examples/storage_archive_s3.py` | Storage provider + archive bucket + file ops |
| `examples/list_storage_buckets.py` | Storage bucket and archive bucket discovery |
| `examples/upload_archive_directory.py` | Bulk archive upload from local directory |
| `examples/copy_archive_file.py` | Archive file copy between buckets |

## API Notes

- Some endpoints can be tenant-restricted in specific MTN Cloud environments.
- Build scripts to discover IDs dynamically (`list` + `get_by_name`) before create/update operations.

## Contributing

Contributions are welcome. Open an issue or submit a PR.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Links

- [MTN Cloud Console](https://console.cloud.mtn.ng)
- [MTN Cloud Guide](https://cloud.mtn.ng/documentation)
- [Morpheus API Documentation (supplementary)](https://apidocs.morpheusdata.com/)
- [GitHub Repository](https://github.com/mahveotm/mtn-cloud-python)
- [PyPI Package](https://pypi.org/project/mtn-cloud/)
