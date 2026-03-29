# MTN Cloud Python SDK

[![PyPI version](https://badge.fury.io/py/mtn-cloud.svg)](https://badge.fury.io/py/mtn-cloud)
[![Tests](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/test.yml/badge.svg)](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/test.yml)
[![Docs](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/docs.yml/badge.svg)](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/docs.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Modern Python SDK for [MTN Cloud](https://console.cloud.mtn.ng) (Morpheus) with typed models, clear resource managers, and practical workflows for compute, networking, storage, and archives.

Docs: [mahveotm.github.io/mtn-cloud-python](https://mahveotm.github.io/mtn-cloud-python/)

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

- [Docs Index](docs/index.md)
- [Quickstart](docs/quickstart.md)
- [Instances](docs/instances.md)
- [Networking](docs/networking.md)
- [Storage](docs/storage.md)
- [Advanced Cookbook](docs/advanced-cookbook.md)
- [API Overview](docs/api-overview.md)
- [Docstring Style Standard](docs/docstring-style.md)

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

Use these lookups before provisioning so your scripts stay deterministic.

```python
# Groups (sites)
groups = cloud.groups.list()
for group in groups[:5]:
    print(group.id, group.name)

# Clouds/zones
clouds = cloud.clouds.list_openstack()
for c in clouds[:5]:
    print(c.id, c.name, c.type_code)

# Instance types
types = cloud.instance_types.list_os()
for t in types[:5]:
    print(t.code, t.name, t.default_layout_id)

# Service plans
plans = cloud.plans.list()
for p in plans[:5]:
    print(p.id, p.name, p.cores, p.memory_gb)
```

### 2. Create an Instance

```python
instance = cloud.instances.create(
    name="my-server",
    cloud="MTNNG_CLOUD_AZ_1",
    type="MTN-CS10",
    group="MTNNG_CLOUD_AZ_1",
    layout=327,
    plan=6776,
    labels=["production", "web"],
)

print(f"Created: {instance.id} {instance.name} ({instance.status})")
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
# List networks
networks = cloud.networks.list(cloud_id=1)
for n in networks[:5]:
    print(n.id, n.name, n.cidr)

# Create an OpenStack-focused network
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

# Update and list subnets
cloud.networks.update(new_network.id, description="Production network")
subnets = cloud.networks.list_subnets(new_network.id)
print(f"Subnets: {len(subnets)}")
```

### 5. Work with Storage and Archives

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
    RateLimitError,
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
| `MTN_CLOUD_URL` | API base URL | `https://console.cloud.mtn.ng` |
| `MTN_CLOUD_TIMEOUT` | Request timeout in seconds | `30` |
| `MTN_CLOUD_MAX_RETRIES` | Maximum retry attempts | `3` |
| `MTN_CLOUD_RETRY_DELAY` | Retry backoff factor | `1.0` |
| `MTN_CLOUD_VERIFY_SSL` | Enable SSL verification | `true` |

Programmatic configuration:

```python
from mtn_cloud import MTNCloud, MTNCloudConfig

config = MTNCloudConfig(
    token="your-token",
    timeout=60,
    max_retries=5,
    retry_delay=1.5,
    verify_ssl=True,
)

cloud = MTNCloud(config=config)
```

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
- [Morpheus API Documentation](https://apidocs.morpheusdata.com/)
- [GitHub Repository](https://github.com/mahveotm/mtn-cloud-python)
- [PyPI Package](https://pypi.org/project/mtn-cloud/)
