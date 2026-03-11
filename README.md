# MTN Cloud Python SDK

[![PyPI version](https://badge.fury.io/py/mtn-cloud.svg)](https://badge.fury.io/py/mtn-cloud)
[![Tests](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/test.yml/badge.svg)](https://github.com/mahveotm/mtn-cloud-python/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python SDK for [MTN Cloud](https://console.cloud.mtn.ng) (Morpheus).

> **⚠️ Disclaimer:** Unofficial community project. Not affiliated with MTN Nigeria.

## Features

- 🚀 **Simple, Pythonic API** - Intuitive interface for all cloud operations
- 📦 **Typed Models** - Full Pydantic models with IDE autocomplete
- 🔄 **Automatic Retries** - Built-in retry logic with exponential backoff
- 🔐 **Flexible Auth** - Token or username/password authentication
- ⚡ **Resource Managers** - Organized access to instances, networks, groups
- 🛡️ **Error Handling** - Specific exceptions for different error types

## Installation

```bash
pip install mtn-cloud
```

## Quick Start

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

# Check connection
user = cloud.whoami()
print(f"Connected as: {user.username}")

# List instances
for instance in cloud.instances.list():
    print(f"{instance.name}: {instance.status} ({instance.primary_ip})")
```

## Authentication

```python
# Using token (recommended)
cloud = MTNCloud(token="your-api-token")

# Or via environment variable
# export MTN_CLOUD_TOKEN="your-api-token"
cloud = MTNCloud()

# Using username/password
cloud = MTNCloud(username="user@example.com", password="your-password")
```

**Getting your API token:** MTN Cloud Console → User Icon (top right) → User Settings → API Access

## Reference Data

### Groups

```python
groups = cloud.groups.list()
for group in groups:
    print(f"{group.name} (ID: {group.id})")

group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
```

| Name | ID |
|------|-----|
| MTNNG_CLOUD_AZ_1 | 621 |

### Instance Types

```python
instance_types = cloud.instance_types.list()
for it in instance_types:
    print(f"{it.code}: {it.name} (Layout ID: {it.default_layout_id})")

# Get by code
centos = cloud.instance_types.get_by_code("MTN-CS10")
print(f"Layout ID: {centos.default_layout_id}")

# List by category
os_types = cloud.instance_types.list_os()
db_types = cloud.instance_types.list_databases()
web_types = cloud.instance_types.list_web()
app_types = cloud.instance_types.list_apps()
```

<details>
<summary><strong>View all instance types</strong></summary>

| Category | Code | Name | Layout ID |
|----------|------|------|-----------|
| OS | MTN-CS10 | CentOS Stream 10 | 327 |
| OS | MTN-CS9 | CentOS Stream 9 | 394 |
| OS | MTN-U24.04LTS | Ubuntu Server 24.04.3LTS | 309 |
| OS | MTN-U22.04LTS | Ubuntu Server 22.04.5LTS | 325 |
| OS | MTN-D12 | Debian 12 | 283 |
| OS | MTN-D13 | Debian 13 | 330 |
| OS | MTN-RL9 | Rocky Linux 9.6 | 395 |
| OS | MTN-RL10 | Rocky Linux 10 | 397 |
| OS | MTN-F42 | Fedora 42 | 392 |
| OS | MTN-F43 | Fedora 43 | 393 |
| OS | MTN-WINSVR2019 | Windows Server 2019 (BYOL) | 300 |
| OS | MTN-WINSVR2022 | Windows Server 2022 (BYOL) | 301 |
| Database | MTN-MySQL01 | MySQL Single-Node | 375 |
| Database | MTN-Postgres01 | PostgreSQL Single-Node | 333 |
| Web | MTN-APACHEWS | Apache Web Server | 372 |
| Web | MTN-NGINXWS | Nginx Web Server | 374 |
| Apps | MTN-LAMP01 | LAMP Stack Server | 379 |
| Apps | MTN-LEMP01 | LEMP Stack Server | 380 |
| Apps | MK8S-M | Kubernetes Master | 386 |
| Apps | MK8S-W | Kubernetes Worker | 387 |
| Network | MTN-WGVPN-01 | WireGuard SSL VPN | 364 |

</details>

### Service Plans

> **Note:** The Service Plans API is restricted. Use the reference below.

**Naming Convention:**
- `G{cores}S{ram}` - General Purpose (e.g., G2S4 = 2 cores, 4GB RAM)
- `Ge{cores}{tier}{ram}` - General Enterprise (e.g., Ge32M64 = 32 cores, 64GB RAM)
- Tiers: `S` (Standard), `M` (Medium), `L` (Large)

<details>
<summary><strong>View all service plans</strong></summary>

| Plan | ID | Cores | RAM (GB) | Category |
|------|-----|-------|----------|----------|
| G1S1 | 6772 | 1 | 1 | General |
| G1S2 | 6773 | 1 | 2 | General |
| G1S4 | 6774 | 1 | 4 | General |
| G2S2 | 6775 | 2 | 2 | General |
| G2S4 | 6776 | 2 | 4 | General |
| G2S8 | 6777 | 2 | 8 | General |
| G2S16 | 6778 | 2 | 16 | General |
| G4S4 | 6779 | 4 | 4 | General |
| G4S8 | 6780 | 4 | 8 | General |
| G4S16 | 6781 | 4 | 16 | General |
| G4S32 | 6782 | 4 | 32 | General |
| G8S8 | 6783 | 8 | 8 | General |
| G8S16 | 6784 | 8 | 16 | General |
| G8S32 | 6785 | 8 | 32 | General |
| G8S64 | 6786 | 8 | 64 | General |
| Ge16S16 | 6787 | 16 | 16 | Enterprise |
| Ge16S32 | 6788 | 16 | 32 | Enterprise |
| Ge16S48 | 6789 | 16 | 48 | Enterprise |
| Ge16S64 | 6790 | 16 | 64 | Enterprise |
| Ge32M32 | 6791 | 32 | 32 | Enterprise |
| Ge32M64 | 6792 | 32 | 64 | Enterprise |
| Ge32M72 | 6793 | 32 | 72 | Enterprise |
| Ge32M128 | 6794 | 32 | 128 | Enterprise |
| Ge64L64 | 6795 | 64 | 64 | Enterprise |
| Ge64L128 | 6796 | 64 | 128 | Enterprise |
| Ge64L256 | 6797 | 64 | 256 | Enterprise |
| Ge64L384 | 6798 | 64 | 384 | Enterprise |
| Ge96L128 | 6799 | 96 | 128 | Enterprise |
| Ge96L256 | 6800 | 96 | 256 | Enterprise |
| Ge96L384 | 6801 | 96 | 384 | Enterprise |

</details>

### Networks

```python
# List networks (optionally by cloud/zone id)
networks = cloud.networks.list()
for network in networks:
    print(f"{network.name} (ID: {network.id})")

network = cloud.networks.get(298)
print(f"Network: {network.name}")
print(f"CIDR: {network.cidr}")
print(f"Gateway: {network.gateway}")

network = cloud.networks.get_by_name("my-network")

# Discover network type IDs for OpenStack
network_types = cloud.networks.list_types(openstack_only=True)
for nt in network_types:
    print(nt.id, nt.code, nt.name)

# Create network (OpenStack-focused fields)
new_network = cloud.networks.create(
    name="mtn-prod-net",
    cloud_id=1,          # /api/zones/{id}
    group_id=621,        # /api/groups/{id}
    type_id=network_types[0].id,
    cidr="192.168.50.0/24",
    gateway="192.168.50.1",
    dns_primary="8.8.8.8",
    dhcp_server=True,
    visibility="private",
)

# Update network
updated = cloud.networks.update(
    new_network.id,
    description="Production network",
    allow_static_override=True,
)

# List subnets under a network
subnets = cloud.networks.list_subnets(new_network.id)

# Delete network
cloud.networks.delete(new_network.id)
```

### OpenStack Network Config Examples

```python
# Example 1: Tenant-private network with DHCP and DNS
private_net = cloud.networks.create(
    name="tenant-a-private",
    cloud_id=1,
    group_id=621,
    type_id=network_types[0].id,
    cidr="10.42.10.0/24",
    gateway="10.42.10.1",
    dns_primary="8.8.8.8",
    dns_secondary="1.1.1.1",
    dhcp_server=True,
    allow_static_override=False,
    assign_public_ip=False,
    visibility="private",
)

# Example 2: Shared network with controlled group access
shared_net = cloud.networks.create(
    name="shared-services-net",
    cloud_id=1,
    group_id=621,
    type_id=network_types[0].id,
    cidr="10.42.20.0/24",
    gateway="10.42.20.1",
    visibility="public",
    resource_permission_all=False,
    resource_permission_site_ids=[621],  # Group IDs allowed to use it
)

# Example 3: Update network routing/security options
cloud.networks.update(
    private_net.id,
    no_proxy="169.254.169.254,10.0.0.0/8",
    appliance_url_proxy_bypass=True,
    search_domains="svc.internal.example",
)
```

## Creating an Instance

```python
from mtn_cloud import MTNCloud
from mtn_cloud.models import InstanceVolume, InstanceNetwork

cloud = MTNCloud(token="your-api-token")

instance = cloud.instances.create(
    name="my-server",
    cloud="MTNNG_CLOUD_AZ_1",
    type="MTN-CS10",                     # Instance type code
    group="MTNNG_CLOUD_AZ_1",            # Group name (resolved to ID automatically)
    layout=327,                          # Layout ID for MTN-CS10
    plan=6775,                           # Service plan ID (G2S2: 2 cores, 2GB RAM)
    resource_pool_id="pool-214",
    availability_zone="Lagos-AZ-1-fd1",
    security_group="default",
    os_external_network_id="public-network-01",
    volumes=[
        InstanceVolume(
            name="root",
            size=20,                     # Size in GB
            storage_type=11,
            datastore_id="auto",
        ),
    ],
    network_interfaces=[
        InstanceNetwork(
            network_id="network-298",
            ip_address="192.168.100.50",  # Optional: static IP
        ),
    ],
    labels=["production", "web"],
)

print(f"Instance created: {instance.name} (ID: {instance.id})")

# Wait for instance to be running
instance = cloud.instances.wait_until_running(instance.id, timeout=300)
print(f"Instance is now: {instance.status}")
print(f"IP Address: {instance.primary_ip}")
```

### Configuration Values

| Parameter | Example | Description |
|-----------|---------|-------------|
| `cloud` | `"MTNNG_CLOUD_AZ_1"` | Cloud/Zone name |
| `resource_pool_id` | `"pool-214"` | Resource pool identifier |
| `availability_zone` | `"Lagos-AZ-1-fd1"` | Availability zone |
| `security_group` | `"default"` | Security group (default always exists) |
| `os_external_network_id` | `"public-network-01"` | External network for floating IP |
| `storage_type` | `11` | Storage type ID |

---

## Managing Instances

```python
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

# Instance actions
instance.stop()
instance.start()
instance.restart()

# Or use the resource manager
cloud.instances.stop(123)
cloud.instances.start(123)

# Resize instance
cloud.instances.resize(123, plan_id=6776)  # Upgrade to G2S4

# Delete instance
cloud.instances.delete(123)

# Force delete with volume preservation
cloud.instances.delete(123, force=True, preserve_volumes=True)
```

---

## Working with Instance Types

```python
# List all instance types
instance_types = cloud.instance_types.list()
for it in instance_types:
    print(f"{it.code}: {it.name} (Layout ID: {it.default_layout_id})")

# Get instance type by code
centos = cloud.instance_types.get_by_code("MTN-CS10")
print(f"ID: {centos.id}")
print(f"Name: {centos.name}")
print(f"Code: {centos.code}")
print(f"Description: {centos.description}")
print(f"Default Layout ID: {centos.default_layout_id}")

# Access layouts
for layout in centos.layouts:
    print(f"  Layout: {layout.id} - {layout.name}")
```

---

## Error Handling

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
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except TimeoutError as e:
    print(f"Request timed out: {e}")
except MTNCloudError as e:
    print(f"API error: {e}")
```

---

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

config = MTNCloudConfig(
    token="your-token",
    timeout=60,
    max_retries=5,
    verify_ssl=True,
)

cloud = MTNCloud(config=config)
```

---

## Testing and Coverage

```bash
# Run tests
pytest -v

# Run tests with coverage (terminal + XML + HTML reports)
pytest -v --cov=mtn_cloud --cov-report=term-missing --cov-report=xml:coverage/coverage.xml --cov-report=html:coverage/html
```

In CI (`.github/workflows/test.yml`), coverage is generated during tests, uploaded as an artifact, and summarized in the GitHub Actions job summary for the `ubuntu-latest` + `3.12` run.

---

## API Limitations

| Endpoint | Status | Workaround |
|----------|--------|------------|
| `/api/service-plans` | ❌ Blocked | See [Service Plans](#service-plans) |
| `/api/zones` (Clouds) | ❌ Blocked | Use `MTNNG_CLOUD_AZ_1` |

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

This is an unofficial community project. Not affiliated with MTN.

## Links

- [MTN Cloud Console](https://console.cloud.mtn.ng)
- [Morpheus API Documentation](https://apidocs.morpheusdata.com/)
- [GitHub Repository](https://github.com/mahveotm/mtn-cloud-python)
- [PyPI Package](https://pypi.org/project/mtn-cloud/)
