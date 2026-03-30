# API Reference

This page documents the public SDK surface in endpoint-first format.

## Conventions

- Base URL: `https://console.cloud.mtn.ng` by default (configurable via `MTN_CLOUD_URL`).
- API prefix: the SDK automatically appends `/api`.
- Endpoint examples below are shown as relative API paths, e.g. `GET /api/instances`.
- All resource managers are accessed from a client instance:

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="...")
```

## Common Exceptions

All HTTP-backed methods may raise these exceptions based on API response or transport errors:

| Exception | When it is raised |
|---|---|
| `AuthenticationError` | `401` or missing/invalid credentials |
| `ForbiddenError` | `403` insufficient permission |
| `NotFoundError` | `404` resource not found |
| `ValidationError` | `400` invalid input/payload |
| `RateLimitError` | `429` too many requests |
| `ServerError` | `5xx` backend failure |
| `TimeoutError` | request timeout |
| `MTNCloudError` | connection errors, unknown status codes, generic request failures |

Method-specific local exceptions (for example `FileNotFoundError`) are documented per method.

## Shared `list(...)` Query Arguments

Most resource managers implement a `list(...)` variant with these common query controls:

| Argument | API Query Key | Notes |
|---|---|---|
| `max_results` | `max` | Maximum returned rows |
| `offset` | `offset` | Pagination offset |
| `sort` | `sort` | Sort field |
| `direction` | `direction` | `asc` or `desc` |
| `phrase` | `phrase` | API-side search phrase |
| `**filters` | passthrough | Extra endpoint-specific filters |

## Shared Inherited Helper

Every resource manager (`instances`, `networks`, `plans`, etc.) inherits:

### `resource.exists(resource_id: int) -> bool`

- Endpoint sequence:
  - `GET /api/<resource-path>/{resource_id}`
- Returns:
  - `True` if found
  - `False` only when `NotFoundError` occurs
- Raises:
  - Any non-`NotFoundError` common API exception

## Client: `MTNCloud`

### `MTNCloud(token=None, username=None, password=None, url=None, timeout=None, verify_ssl=True, config=None)`

Creates an SDK client and lazy-loads resource managers.

- Endpoint: None (constructor does not make API calls)
- Parameters:
  - `token`: API bearer token (recommended)
  - `username`, `password`: OAuth password-grant alternative
  - `url`: MTN Cloud base console URL, no `/api` needed
  - `timeout`: request timeout in seconds
  - `verify_ssl`: enable/disable TLS certificate validation
  - `config`: explicit `MTNCloudConfig` object (overrides other args)
- Returns: `MTNCloud`
- Raises:
  - `pydantic.ValidationError` if config values violate `MTNCloudConfig` constraints

### `whoami() -> User`

- Endpoint: `GET /api/whoami`
- Parameters: none
- Returns: `User`
- Raises: common API exceptions

### `ping() -> bool`

Connectivity/auth convenience check.

- Endpoint sequence:
  - `GET /api/whoami` (via `whoami()`)
- Parameters: none
- Returns:
  - `True` if request succeeds
  - `False` for any exception
- Raises: none (exceptions are swallowed and converted to `False`)

### `close() -> None`

- Endpoint: None
- Parameters: none
- Returns: `None`
- Raises: none

## Resource: `cloud.instances` (`InstancesResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, status=None, cloud_id=None, group_id=None, labels=None, **filters) -> list[Instance]`

- Endpoint: `GET /api/instances`
- Parameters:
  - Shared list args (see section above)
  - `name`: exact name filter
  - `status`: status filter
  - `cloud_id`: mapped to query `zoneId`
  - `group_id`: mapped to query `siteId`
  - `labels`: list mapped to comma-delimited query `labels`
- Returns: `list[Instance]`
- Raises: common API exceptions

### `get(instance_id: int) -> Instance`

- Endpoint: `GET /api/instances/{instance_id}`
- Parameters:
  - `instance_id`: instance numeric ID
- Returns: `Instance`
- Raises: common API exceptions

### `get_by_name(name: str) -> Instance`

- Endpoint sequence:
  - `GET /api/instances?name=<name>&max=1`
- Parameters:
  - `name`: instance name
- Returns: `Instance`
- Raises:
  - common API exceptions
  - `NotFoundError` when no instance matches

### `create(name: str, *, cloud: str, type: str, group: str, layout: int, plan: int, description=None, environment=None, labels=None, tags=None, copies=1, layout_size=1, resource_pool_id=None, availability_zone=None, security_group="default", os_external_network_id=None, create_user=True, workflow_id=None, shutdown_days=None, expire_days=None, create_backup=None, security_groups=None, ports=None, volumes=None, network_interfaces=None, options=None) -> Instance`

- Endpoint sequence:
  - `GET /api/groups?name=<group>&max=1` (resolve group name to `group_id`)
  - `POST /api/instances`
- Parameters:
  - Required core fields:
    - `name`: new instance name
    - `cloud`: cloud/zone name (example: `MTNNG_CLOUD_AZ_1`)
    - `type`: instance type code (example: `MTN-CS10`)
    - `group`: group/site name (resolved to ID)
    - `layout`: layout ID
    - `plan`: service plan ID
  - Optional metadata:
    - `description`, `environment`, `labels`, `tags`
  - Optional sizing/provisioning:
    - `copies`, `layout_size`
  - Optional MTN/OpenStack-specific provisioning:
    - `resource_pool_id`, `availability_zone`, `security_group`, `os_external_network_id`, `create_user`
  - Optional automation:
    - `workflow_id`, `shutdown_days`, `expire_days`, `create_backup`
  - Optional networking/storage details:
    - `security_groups`, `ports`, `volumes`, `network_interfaces`, `options`
- Returns: `Instance`
- Raises:
  - common API exceptions
  - `NotFoundError` when `group` cannot be resolved

### `update(instance_id: int, name=None, description=None, labels=None) -> Instance`

- Endpoint: `PUT /api/instances/{instance_id}`
- Parameters:
  - `instance_id`: target instance ID
  - `name`: replacement name
  - `description`: replacement description
  - `labels`: replacement labels list
- Returns: `Instance`
- Raises: common API exceptions

### `delete(instance_id: int, preserve_volumes=False, force=False) -> bool`

- Endpoint: `DELETE /api/instances/{instance_id}`
- Parameters:
  - `instance_id`: target instance ID
  - `preserve_volumes`: adds query `preserveVolumes=on`
  - `force`: adds query `force=on`
- Returns: `True` on successful deletion request
- Raises: common API exceptions

### `start(instance_id: int) -> Instance`

- Endpoint sequence:
  - `PUT /api/instances/{instance_id}/start`
  - `GET /api/instances/{instance_id}`
- Returns: refreshed `Instance`
- Raises: common API exceptions

### `stop(instance_id: int) -> Instance`

- Endpoint sequence:
  - `PUT /api/instances/{instance_id}/stop`
  - `GET /api/instances/{instance_id}`
- Returns: refreshed `Instance`
- Raises: common API exceptions

### `restart(instance_id: int) -> Instance`

- Endpoint sequence:
  - `PUT /api/instances/{instance_id}/restart`
  - `GET /api/instances/{instance_id}`
- Returns: refreshed `Instance`
- Raises: common API exceptions

### `suspend(instance_id: int) -> Instance`

- Endpoint sequence:
  - `PUT /api/instances/{instance_id}/suspend`
  - `GET /api/instances/{instance_id}`
- Returns: refreshed `Instance`
- Raises: common API exceptions

### `resize(instance_id: int, plan_id: int) -> Instance`

- Endpoint sequence:
  - `PUT /api/instances/{instance_id}/resize`
  - `GET /api/instances/{instance_id}`
- Parameters:
  - `plan_id`: new service plan ID
- Returns: resized `Instance`
- Raises: common API exceptions

### `wait_for_status(instance_id: int, target_status: str, timeout: int = 300, poll_interval: int = 5) -> Instance`

Client-side polling helper.

- Endpoint sequence:
  - repeated `GET /api/instances/{instance_id}` until target status or timeout
- Parameters:
  - `target_status`: desired status string (`running`, `stopped`, etc.)
  - `timeout`: max wait in seconds
  - `poll_interval`: sleep interval between polls
- Returns: `Instance` once target status matches
- Raises:
  - common API exceptions from internal `get`
  - `TimeoutError` when timeout is exceeded
  - `RuntimeError` if instance enters `failed` state

### `wait_until_running(instance_id: int, timeout: int = 300) -> Instance`

- Endpoint behavior: same as `wait_for_status(..., target_status="running")`
- Returns: `Instance`
- Raises: same as `wait_for_status`

### `wait_until_stopped(instance_id: int, timeout: int = 300) -> Instance`

- Endpoint behavior: same as `wait_for_status(..., target_status="stopped")`
- Returns: `Instance`
- Raises: same as `wait_for_status`

### `get_console(instance_id: int) -> dict[str, Any]`

- Endpoint: `GET /api/instances/{instance_id}/console`
- Returns: raw console payload (`url`, credentials, metadata)
- Raises: common API exceptions

### `get_history(instance_id: int, max_results: int | None = None) -> list[dict[str, Any]]`

- Endpoint: `GET /api/instances/{instance_id}/history`
- Parameters:
  - `max_results`: maps to query `max`
- Returns: list from response key `processes`
- Raises: common API exceptions

## Resource: `cloud.instance_types` (`InstanceTypesResource`)

### `list(max_results=None, offset=0, sort="name", direction="asc", phrase=None, name=None, code=None, category=None, featured=None, **filters) -> list[InstanceType]`

- Endpoint: `GET /api/instance-types`
- Parameters:
  - Shared list args
  - `name`: name filter
  - `code`: code filter
  - `category`: category filter (`os`, `sql`, `web`, `apps`, etc.)
  - `featured`: feature flag filter
- Returns: `list[InstanceType]`
- Raises: common API exceptions

### `get(instance_type_id: int) -> InstanceType`

- Endpoint: `GET /api/instance-types/{instance_type_id}`
- Returns: `InstanceType`
- Raises: common API exceptions

### `get_by_code(code: str) -> InstanceType`

- Endpoint sequence:
  - `GET /api/instance-types?code=<code>&max=1`
- Returns: `InstanceType`
- Raises:
  - common API exceptions
  - `NotFoundError` when no match

### `get_by_name(name: str) -> InstanceType`

- Endpoint sequence:
  - `GET /api/instance-types?name=<name>&max=1`
- Returns: `InstanceType`
- Raises:
  - common API exceptions
  - `NotFoundError` when no match

### `list_os() -> list[InstanceType]`

- Endpoint: `GET /api/instance-types?category=os`
- Returns: OS instance types
- Raises: common API exceptions

### `list_databases() -> list[InstanceType]`

- Endpoint: `GET /api/instance-types?category=sql`
- Returns: database instance types
- Raises: common API exceptions

### `list_web() -> list[InstanceType]`

- Endpoint: `GET /api/instance-types?category=web`
- Returns: web instance types
- Raises: common API exceptions

### `list_apps() -> list[InstanceType]`

- Endpoint: `GET /api/instance-types?category=apps`
- Returns: app instance types
- Raises: common API exceptions

## Resource: `cloud.networks` (`NetworksResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, cloud_id=None, **filters) -> list[Network]`

- Endpoint: `GET /api/networks`
- Parameters:
  - Shared list args
  - `name`: network name filter
  - `cloud_id`: mapped to query `zoneId`
- Returns: `list[Network]`
- Raises: common API exceptions

### `get(network_id: int) -> Network`

- Endpoint: `GET /api/networks/{network_id}`
- Returns: `Network`
- Raises: common API exceptions

### `get_by_name(name: str, cloud_id: int | None = None) -> Network`

- Endpoint sequence:
  - `GET /api/networks?name=<name>&max=1`
  - Adds `zoneId=<cloud_id>` when provided
- Returns: `Network`
- Raises:
  - common API exceptions
  - `NotFoundError` when no match

### `list_by_cloud(cloud_id: int) -> list[Network]`

- Endpoint: `GET /api/networks?zoneId=<cloud_id>`
- Returns: `list[Network]`
- Raises: common API exceptions

### `create(name: str, *, cloud_id: int, group_id: int, type_id=None, display_name=None, labels=None, description=None, cidr=None, gateway=None, dns_primary=None, dns_secondary=None, vlan_id=None, switch_id=None, pool_id=None, allow_static_override=None, assign_public_ip=None, active=None, dhcp_server=None, network_domain_id=None, search_domains=None, network_proxy_id=None, appliance_url_proxy_bypass=None, no_proxy=None, visibility=None, tenant_ids=None, resource_permission_all=None, resource_permission_site_ids=None) -> Network`

- Endpoint: `POST /api/networks`
- Parameters:
  - Required:
    - `name`: network name
    - `cloud_id`: cloud/zone ID
    - `group_id`: group/site ID
  - Common optional network config:
    - `type_id`, `display_name`, `labels`, `description`, `cidr`, `gateway`
    - `dns_primary`, `dns_secondary`, `vlan_id`, `switch_id`, `pool_id`
    - `allow_static_override`, `assign_public_ip`, `active`, `dhcp_server`
    - `network_domain_id`, `search_domains`, `network_proxy_id`
    - `appliance_url_proxy_bypass`, `no_proxy`, `visibility`
    - `tenant_ids`, `resource_permission_all`, `resource_permission_site_ids`
- Returns: `Network`
- Raises: common API exceptions

### `update(network_id: int, *, display_name=None, labels=None, description=None, cidr=None, gateway=None, dns_primary=None, dns_secondary=None, vlan_id=None, switch_id=None, pool_id=None, allow_static_override=None, assign_public_ip=None, active=None, dhcp_server=None, network_domain_id=None, search_domains=None, network_proxy_id=None, appliance_url_proxy_bypass=None, no_proxy=None, visibility=None, tenant_ids=None, resource_permission_all=None, resource_permission_site_ids=None) -> Network`

- Endpoint: `PUT /api/networks/{network_id}`
- Parameters:
  - `network_id`: target network ID
  - Optional fields mirror `create(...)` (except required create-only identifiers)
- Returns: `Network`
- Raises: common API exceptions

### `delete(network_id: int) -> bool`

- Endpoint: `DELETE /api/networks/{network_id}`
- Returns: `True`
- Raises: common API exceptions

### `list_subnets(network_id: int) -> list[Subnet]`

- Endpoint: `GET /api/networks/{network_id}/subnets`
- Returns: `list[Subnet]`
- Raises: common API exceptions

### `list_types(name=None, code=None, phrase=None, openstack_only=False) -> list[NetworkTypeInfo]`

- Endpoint: `GET /api/network-types`
- Parameters:
  - `name`: exact name filter
  - `code`: exact code filter
  - `phrase`: phrase filter
  - `openstack_only`: client-side filter on returned `is_openstack`
- Returns: `list[NetworkTypeInfo]`
- Raises: common API exceptions

### `get_type(type_id: int) -> NetworkTypeInfo`

- Endpoint: `GET /api/network-types/{type_id}`
- Returns: `NetworkTypeInfo`
- Raises: common API exceptions

### `list_floating_ips(*, phrase=None, ip_address=None, ip_status=None, cloud_id=None, server_id=None) -> list[NetworkFloatingIP]`

- Endpoint: `GET /api/networks/floating-ips`
- Parameters:
  - `phrase`: search phrase
  - `ip_address`: exact IP match
  - `ip_status`: provider status value
  - `cloud_id`: mapped to `zoneId`
  - `server_id`: mapped to `serverId`
- Returns: `list[NetworkFloatingIP]`
- Raises: common API exceptions

### `get_floating_ip(floating_ip_id: int) -> NetworkFloatingIP`

- Endpoint: `GET /api/networks/floating-ips/{floating_ip_id}`
- Returns: `NetworkFloatingIP`
- Raises: common API exceptions

### `allocate_floating_ip(*, network_server_id: int, floating_ip_pool_id: int) -> NetworkFloatingIP`

- Endpoint: `POST /api/networks/floating-ips`
- Parameters:
  - `network_server_id`: backend network server ID
  - `floating_ip_pool_id`: floating IP pool ID
- Returns: `NetworkFloatingIP`
- Raises: common API exceptions

### `release_floating_ip(floating_ip_id: int) -> bool`

- Endpoint: `PUT /api/networks/floating-ips/{floating_ip_id}/release`
- Returns: `True`
- Raises: common API exceptions

## Resource: `cloud.clouds` (`CloudsResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, group_id=None, type_code=None, **filters) -> list[Cloud]`

- Endpoint: `GET /api/zones`
- Parameters:
  - Shared list args
  - `name`: cloud/zone name filter
  - `group_id`: mapped to `groupId`
  - `type_code`: mapped to `type` (example: `openstack`)
- Returns: `list[Cloud]`
- Raises: common API exceptions

### `list_openstack(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, group_id=None, **filters) -> list[Cloud]`

- Endpoint: `GET /api/zones?type=openstack`
- Returns: OpenStack-only clouds
- Raises: common API exceptions

### `get(cloud_id: int) -> Cloud`

- Endpoint: `GET /api/zones/{cloud_id}`
- Returns: `Cloud`
- Raises: common API exceptions

### `get_by_name(name: str) -> Cloud`

- Endpoint sequence:
  - `GET /api/zones?name=<name>&max=1`
- Returns: `Cloud`
- Raises:
  - common API exceptions
  - `NotFoundError` when no match

### `list_by_group(group_id: int) -> list[Cloud]`

- Endpoint: `GET /api/zones?groupId=<group_id>`
- Returns: `list[Cloud]`
- Raises: common API exceptions

## Resource: `cloud.groups` (`GroupsResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, **filters) -> list[Group]`

- Endpoint: `GET /api/groups`
- Parameters:
  - Shared list args
  - `name`: group name filter
- Returns: `list[Group]`
- Raises: common API exceptions

### `get(group_id: int) -> Group`

- Endpoint: `GET /api/groups/{group_id}`
- Returns: `Group`
- Raises: common API exceptions

### `get_by_name(name: str) -> Group`

- Endpoint sequence:
  - `GET /api/groups?name=<name>&max=1`
- Returns: `Group`
- Raises:
  - common API exceptions
  - `NotFoundError` when no match

## Resource: `cloud.plans` (`PlansResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, **filters) -> list[ServicePlan]`

- Endpoint: `GET /api/service-plans`
- Parameters:
  - Shared list args
  - `name`: plan name filter
- Returns: `list[ServicePlan]`
- Raises: common API exceptions

### `get(plan_id: int) -> ServicePlan`

- Endpoint: `GET /api/service-plans/{plan_id}`
- Returns: `ServicePlan`
- Raises: common API exceptions

### `get_by_name(name: str) -> ServicePlan`

- Endpoint sequence:
  - `GET /api/service-plans?name=<name>&max=1`
- Returns: `ServicePlan`
- Raises:
  - common API exceptions
  - `NotFoundError` when no match

### `find(cores=None, memory_gb=None, storage_gb=None) -> ServicePlan | None`

Client-side selector for first plan meeting minimum requirements.

- Endpoint sequence:
  - `GET /api/service-plans`
- Parameters:
  - `cores`: minimum CPU cores
  - `memory_gb`: minimum memory in GB
  - `storage_gb`: minimum storage in GB
- Returns:
  - `ServicePlan` first match
  - `None` if no plan satisfies constraints
- Raises: common API exceptions

## Resource: `cloud.storage_buckets` (`StorageBucketsResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, **filters) -> list[StorageBucket]`

- Endpoint: `GET /api/storage-buckets`
- Parameters:
  - Shared list args
  - `name`: storage bucket name filter
- Returns: `list[StorageBucket]`
- Raises: common API exceptions

### `get(storage_bucket_id: int) -> StorageBucket`

- Endpoint: `GET /api/storage-buckets/{storage_bucket_id}`
- Returns: `StorageBucket`
- Raises: common API exceptions

### `get_by_name(name: str) -> StorageBucket`

- Endpoint sequence:
  - `GET /api/storage-buckets?name=<name>&max=1`
- Returns: `StorageBucket`
- Raises:
  - common API exceptions
  - `NotFoundError` when no match

### `create(name: str, *, bucket_name: str, access_key: str, secret_key: str, endpoint: str, storage_server=None, default_backup_target=None, copy_to_store=None, default_deployment_target=None, default_virtual_image_target=None, retention_policy_type="none", retention_policy_days=None, retention_provider=None, create_bucket=True) -> StorageBucket`

- Endpoint: `POST /api/storage-buckets`
- Parameters:
  - Required:
    - `name`: storage bucket object name
    - `bucket_name`: underlying S3 bucket/container name
    - `access_key`, `secret_key`, `endpoint`: provider credentials/endpoint
  - Optional target/default flags:
    - `default_backup_target`, `copy_to_store`, `default_deployment_target`, `default_virtual_image_target`
  - Optional retention behavior:
    - `retention_policy_type`: `backup`, `delete`, or `none`
    - `retention_policy_days`, `retention_provider`
  - `storage_server`: optional storage server ID
  - `create_bucket`: create target bucket when missing
- Returns: `StorageBucket`
- Raises: common API exceptions

### `create_s3(name: str, *, bucket_name: str, access_key: str, secret_key: str, endpoint: str, storage_server=None, create_bucket=True, default_backup_target=None, copy_to_store=None, default_deployment_target=None, default_virtual_image_target=None) -> StorageBucket`

Convenience wrapper for S3-backed create.

- Endpoint behavior: forwards to `create(...)` then `POST /api/storage-buckets`
- Returns: `StorageBucket`
- Raises: same as `create`

### `update(storage_bucket_id: int, *, name=None, bucket_name=None, config=None, default_backup_target=None, copy_to_store=None, default_deployment_target=None, default_virtual_image_target=None, retention_policy_type=None, retention_policy_days=None, retention_provider=None, create_bucket=None) -> StorageBucket`

- Endpoint: `PUT /api/storage-buckets/{storage_bucket_id}`
- Parameters:
  - `storage_bucket_id`: target ID
  - Optional updates for name/bucket/config/defaults/retention
- Returns: `StorageBucket`
- Raises: common API exceptions

### `delete(storage_bucket_id: int, *, remove_resources: bool = False) -> bool`

- Endpoint: `DELETE /api/storage-buckets/{storage_bucket_id}`
- Parameters:
  - `remove_resources`: when `True`, sends `removeResources=true`
- Returns: `True`
- Raises: common API exceptions

## Resource: `cloud.archive_buckets` (`ArchiveBucketsResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, **filters) -> list[ArchiveBucket]`

- Endpoint: `GET /api/archives/buckets`
- Parameters:
  - Shared list args
  - `name`: archive bucket name filter
- Returns: `list[ArchiveBucket]`
- Raises: common API exceptions

### `get(archive_bucket_id: int) -> ArchiveBucket`

- Endpoint: `GET /api/archives/buckets/{archive_bucket_id}`
- Returns: `ArchiveBucket`
- Raises: common API exceptions

### `get_by_name(name: str) -> ArchiveBucket`

- Endpoint sequence:
  - `GET /api/archives/buckets?name=<name>&max=1`
- Returns: `ArchiveBucket`
- Raises:
  - common API exceptions
  - `NotFoundError` when no match

### `create(name: str, *, storage_provider_id: int, description=None, visibility="private", is_public=False, account_id=None) -> ArchiveBucket`

- Endpoint: `POST /api/archives/buckets`
- Parameters:
  - `name`: globally unique archive bucket name
  - `storage_provider_id`: linked storage bucket/provider ID
  - `description`: optional description
  - `visibility`: `private` or `public`
  - `is_public`: enable anonymous public URL support
  - `account_id`: optional tenant account override
- Returns: `ArchiveBucket`
- Raises: common API exceptions

### `update(archive_bucket_id: int, *, name=None, description=None, visibility=None, is_public=None, account_id=None) -> ArchiveBucket`

- Endpoint: `PUT /api/archives/buckets/{archive_bucket_id}`
- Returns: `ArchiveBucket`
- Raises: common API exceptions

### `delete(archive_bucket_id: int) -> bool`

- Endpoint: `DELETE /api/archives/buckets/{archive_bucket_id}`
- Returns: `True`
- Raises: common API exceptions

### `list_files(*, bucket_name: str, remote_path: str | None = None, name: str | None = None, phrase: str | None = None, full_tree: bool | None = None) -> list[ArchiveFile]`

- Endpoint: `GET /api/archives/buckets/{bucket_name}/files/{remote_path}`
- Parameters:
  - `bucket_name`: archive bucket name (not storage provider name)
  - `remote_path`: archive path to list (defaults to `/`)
  - `name`: exact file name filter
  - `phrase`: wildcard phrase filter
  - `full_tree`: include nested paths
- Returns: `list[ArchiveFile]`
- Raises: common API exceptions

### `upload_file(*, bucket_name: str, remote_path: str, local_path: str | Path, filename: str | None = None) -> ArchiveFile`

- Endpoint: `POST /api/archives/buckets/{bucket_name}/files/{remote_path}` (multipart)
- Parameters:
  - `bucket_name`: destination archive bucket name
  - `remote_path`: destination directory path
  - `local_path`: local file path to upload
  - `filename`: optional destination filename override
- Returns: `ArchiveFile`
- Raises:
  - common API exceptions
  - `FileNotFoundError` if `local_path` does not exist
  - `ValueError` for invalid filename (empty, hidden name, spaces, unsupported chars)
  - `NotFoundError` with enriched message when destination bucket/path does not exist

### `upload_directory(*, bucket_name: str, remote_path: str, local_directory: str | Path, recursive: bool = True, dry_run: bool = False, strict: bool = False) -> ArchiveDirectoryUploadResult`

Bulk upload helper with preflight classification.

- Endpoint behavior:
  - Local preflight scan/validation
  - Multiple `POST /api/archives/buckets/{bucket_name}/files/{destination_remote_path}` calls for eligible files
- Parameters:
  - `bucket_name`: destination archive bucket
  - `remote_path`: base destination directory
  - `local_directory`: source directory
  - `recursive`: include nested files
  - `dry_run`: only preflight, no uploads
  - `strict`: abort upload phase if preflight has skipped files
- Returns: `ArchiveDirectoryUploadResult` with `scanned`, `eligible`, `skipped`, `uploaded`, `failed`, plus per-file details
- Raises:
  - `FileNotFoundError` if `local_directory` does not exist
  - `NotADirectoryError` if `local_directory` is not a directory
  - Other exceptions are generally captured into `failed_files`/`skipped_files` entries instead of being raised

### `download_file(*, bucket_name: str, remote_path: str, local_path: str | Path | None = None) -> bytes | Path`

- Endpoint: `GET /api/archives/download/{bucket_name}/{remote_path}`
- Parameters:
  - `local_path`: optional save target; when omitted returns bytes in memory
- Returns:
  - `bytes` when `local_path` is `None`
  - `Path` when written to disk
- Raises:
  - common API exceptions
  - filesystem exceptions if writing to `local_path` fails

### `copy_file(*, source_bucket_name: str, source_path: str, destination_bucket_name: str, destination_path: str | None = None, destination_filename: str | None = None) -> ArchiveFile`

Copy helper implemented as download + upload.

- Endpoint sequence:
  - `GET /api/archives/download/{source_bucket_name}/{source_path}`
  - `POST /api/archives/buckets/{destination_bucket_name}/files/{destination_path or "/"}`
- Returns: copied `ArchiveFile`
- Raises:
  - common API exceptions
  - any local/file validation exceptions from `download_file(...)` or `upload_file(...)`

### `get_file(archive_file_id: int) -> ArchiveFile`

- Endpoint: `GET /api/archives/files/{archive_file_id}`
- Returns: `ArchiveFile`
- Raises: common API exceptions

### `delete_file(archive_file_id: int) -> bool`

- Endpoint: `DELETE /api/archives/files/{archive_file_id}`
- Returns: `True`
- Raises: common API exceptions

## References

- MTN Cloud Console: <https://console.cloud.mtn.ng>
- MTN Cloud Guide: <https://cloud.mtn.ng/documentation>
- Morpheus API Docs: <https://apidocs.morpheusdata.com/>
- SDK Source: <https://github.com/mahveotm/mtn-cloud-python>
