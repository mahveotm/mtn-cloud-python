# MTN Cloud Python SDK

[![PyPI version](https://img.shields.io/pypi/v/mtn-cloud.svg)](https://pypi.org/project/mtn-cloud/)
[![Tests](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/test.yml/badge.svg)](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A community-maintained Python SDK for [MTN Cloud](https://console.cloud.mtn.ng) (Morpheus).

> **⚠️ Disclaimer:** This is an **unofficial community project** and is not affiliated with, endorsed by, or supported by MTN. This software is provided "as is", without warranty of any kind. Use at your own risk. See the [LICENSE](LICENSE) for full terms.

## Features

- 🚀 **Simple, Pythonic API** - Intuitive interface for all cloud operations
- 📦 **Typed Models** - Full Pydantic models with IDE autocomplete
- 🔄 **Automatic Retries** - Built-in retry logic with exponential backoff
- 🔐 **Flexible Auth** - Token or username/password authentication
- ⚡ **Resource Managers** - Organized access to instances, networks, volumes
- 🛡️ **Error Handling** - Specific exceptions for different error types

## Installation

```bash
pip install mtn-cloud
```


## Quick Start

```python
from mtn_cloud import MTNCloud

# Initialize with token
cloud = MTNCloud(token="your-api-token")

# Or use environment variable MTN_CLOUD_TOKEN
cloud = MTNCloud()

# Check connection
user = cloud.whoami()
print(f"Connected as: {user.username}")

# List instances
for instance in cloud.instances.list():
    print(f"{instance.name}: {instance.status} ({instance.primary_ip})")
```

## Authentication

### Using API Token (Recommended)

```python
from mtn_cloud import MTNCloud

# Pass token directly
cloud = MTNCloud(token="your-api-token")

# Or set environment variable
# export MTN_CLOUD_TOKEN="your-api-token"
cloud = MTNCloud()
```

### Using Username/Password

```python
cloud = MTNCloud(
    username="user@example.com",
    password="your-password"
)
```

### Getting Your API Token

1. Log in to [MTN Cloud Console](https://console.cloud.mtn.ng)
2. Go to **User Settings** → **API Access**
3. Generate a new access token

## Usage Examples

### Managing Instances

```python
from mtn_cloud import MTNCloud
from mtn_cloud.models import InstanceConfig, InstanceVolume, InstanceNetwork

cloud = MTNCloud(token="xxx")

# List all instances
instances = cloud.instances.list()

# Filter instances
running = cloud.instances.list(status="running")
by_name = cloud.instances.list(name="web-server")

# Get a specific instance
instance = cloud.instances.get(123)
print(f"Name: {instance.name}")
print(f"Status: {instance.status}")
print(f"IP: {instance.primary_ip}")

# Get instance by name
instance = cloud.instances.get_by_name("my-app")

# Create a new instance
instance = cloud.instances.create(
    name="web-server-01",
    cloud_id=1,
    group_id=1,
    instance_type_code="MTN-CS10",
    layout_id=327,
    plan_id=6923,
    config=InstanceConfig(
        resource_pool_id="pool-214",
        availability_zone="Lagos-AZ-1-fd1",
        security_group="default",
    ),
    volumes=[
        InstanceVolume(name="root", size=20),
    ],
    network_interfaces=[
        InstanceNetwork(network_id=298, ip_address="192.168.100.50"),
    ],
    labels=["production", "web"],
)

# Wait for instance to be running
instance = cloud.instances.wait_until_running(instance.id, timeout=300)

# Instance actions
instance.stop()
instance.start()
instance.restart()

# Or use the resource manager
cloud.instances.stop(123)
cloud.instances.start(123)

# Resize instance
cloud.instances.resize(123, plan_id=6924)

# Delete instance
cloud.instances.delete(123)

# Force delete with volume preservation
cloud.instances.delete(123, force=True, preserve_volumes=True)
```

### Working with Networks

```python
# List all networks
networks = cloud.networks.list()

# List networks for a specific cloud
networks = cloud.networks.list(cloud_id=1)

# Get network by ID
network = cloud.networks.get(298)
print(f"Network: {network.name}")
print(f"CIDR: {network.cidr}")
print(f"Gateway: {network.gateway}")

# Get network by name
network = cloud.networks.get_by_name("my-network")
```

### Managing Groups and Clouds

```python
# List groups
for group in cloud.groups.list():
    print(f"{group.name}: {group.instance_count} instances")

# Get group by name
group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")

# List clouds/zones
for c in cloud.clouds.list():
    print(f"{c.name}: {c.type_code}")

# Get cloud by name
zone = cloud.clouds.get_by_name("MTNNG_CLOUD_AZ_1")
```

### Service Plans

```python
# List all plans
plans = cloud.plans.list()

for plan in plans:
    print(f"{plan.name}: {plan.cores} cores, {plan.memory_gb}GB RAM")

# Find a plan by requirements
plan = cloud.plans.find(cores=2, memory_gb=4)
```

## Error Handling

The SDK provides specific exceptions for different error types:

```python
from mtn_cloud import (
    MTNCloud,
    MTNCloudError,
    AuthenticationError,
    NotFoundError,
    ForbiddenError,
    ValidationError,
    RateLimitError,
    TimeoutError,
)

cloud = MTNCloud(token="xxx")

try:
    instance = cloud.instances.get(99999)
except NotFoundError as e:
    print(f"Instance not found: {e}")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except ForbiddenError as e:
    print(f"Access denied: {e}")
except ValidationError as e:
    print(f"Invalid request: {e}")
    print(f"Errors: {e.errors}")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except TimeoutError as e:
    print(f"Request timed out: {e}")
except MTNCloudError as e:
    print(f"API error: {e}")
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MTN_CLOUD_TOKEN` | API access token | - |
| `MTN_CLOUD_URL` | API base URL | `https://console.cloud.mtn.ng` |
| `MTN_CLOUD_TIMEOUT` | Request timeout (seconds) | `30` |
| `MTN_CLOUD_MAX_RETRIES` | Max retry attempts | `3` |
| `MTN_CLOUD_VERIFY_SSL` | Verify SSL certs | `true` |

### Programmatic Configuration

```python
from mtn_cloud import MTNCloud, MTNCloudConfig

# Using config object
config = MTNCloudConfig(
    token="xxx",
    timeout=60,
    max_retries=5,
    debug=True,
)
cloud = MTNCloud(config=config)

# Or pass arguments directly
cloud = MTNCloud(
    token="xxx",
    timeout=60,
    verify_ssl=False,  # Not recommended for production
)
```

## Context Manager

Use as a context manager for automatic cleanup:

```python
with MTNCloud(token="xxx") as cloud:
    instances = cloud.instances.list()
    # Session is automatically closed when exiting
```

## Advanced Usage

### Waiting for Instance States

```python
# Wait for specific status
instance = cloud.instances.wait_for_status(
    instance_id=123,
    target_status="running",
    timeout=300,
    poll_interval=5,
)

# Convenience methods
instance = cloud.instances.wait_until_running(123)
instance = cloud.instances.wait_until_stopped(123)
```

### Instance Actions from Instance Object

```python
# Get instance
instance = cloud.instances.get(123)

# Actions are available directly on the instance
instance.stop()
instance.start()
instance.restart()
instance.delete()

# Refresh data from API
instance.refresh()
```

### Checking Connection

```python
# Quick connection check
if cloud.ping():
    print("Connected!")
else:
    print("Connection failed")
```

## API Reference

### MTNCloud

Main client class.

| Property | Description |
|----------|-------------|
| `instances` | Instance resource manager |
| `networks` | Network resource manager |
| `groups` | Group resource manager |
| `clouds` | Cloud/zone resource manager |
| `plans` | Service plan resource manager |

| Method | Description |
|--------|-------------|
| `whoami()` | Get current user |
| `ping()` | Check connection |
| `close()` | Close HTTP session |

### InstancesResource

| Method | Description |
|--------|-------------|
| `list(**filters)` | List instances |
| `get(id)` | Get instance by ID |
| `get_by_name(name)` | Get instance by name |
| `create(...)` | Create new instance |
| `update(id, ...)` | Update instance |
| `delete(id)` | Delete instance |
| `start(id)` | Start instance |
| `stop(id)` | Stop instance |
| `restart(id)` | Restart instance |
| `suspend(id)` | Suspend instance |
| `resize(id, plan_id)` | Resize instance |
| `wait_for_status(...)` | Wait for status |
| `wait_until_running(id)` | Wait until running |
| `wait_until_stopped(id)` | Wait until stopped |

## Development

### Setup

```bash
git clone https://github.com/mahveotm/mtn-cloud-python
cd mtn-cloud-python
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=mtn_cloud
```

### Code Quality

```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests

# Lint and auto-fix
ruff check src tests --fix

# Type checking
mypy src
```

## License

MIT License - see [LICENSE](LICENSE) for details.

This is an unofficial community project. Not affiliated with MTN.

## Author

**Marvellous Osuolale** - [GitHub](https://github.com/mahveotm)

## Links

- [MTN Cloud Console](https://console.cloud.mtn.ng)
- [Morpheus Documentation](https://docs.morpheusdata.com)
- [GitHub Repository](https://github.com/mahveotm/mtn-cloud-python)
- [PyPI Package](https://pypi.org/project/mtn-cloud/)

