# API Overview

This page summarizes the public SDK surface.

For endpoint-by-endpoint signatures, parameters, return types, and raised exceptions, see [API Reference](./api-reference/index.md).

## Entry Point

```python
from mtn_cloud import MTNCloud
```

`MTNCloud` exposes lazily-initialized resource managers:
- `instances`
- `instance_types`
- `networks`
- `clouds`
- `groups`
- `plans`
- `storage_buckets`
- `archive_buckets`
- `security_groups`
- `backups`
- `virtual_images`

## Authentication Options

- `MTNCloud(token="...")`
- `MTNCloud(username="...", password="...")`
- `MTNCloud()` with `MTN_CLOUD_TOKEN` env var

## Common Read Operations

```python
cloud.whoami()
cloud.instances.list()
cloud.instances.get(123)
cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
cloud.instance_types.get_by_code("MTN-CS10")
```

## Common Write Operations

```python
# Discover the resource pool an instance will be hosted in
pool = cloud.instances.get_resource_pool("my-project", group="MTNNG_CLOUD_AZ_1")

cloud.instances.create(..., resource_pool_id=pool.code)
cloud.instances.update(instance_id=123, name="new-name")
cloud.instances.delete(123)

cloud.instances.create_snapshot(123, "pre-upgrade")
cloud.instances.revert_snapshot(123, snapshot_id=456)

cloud.networks.create(...)
cloud.networks.update(298, description="updated")
cloud.networks.delete(298)

cloud.storage_buckets.create_s3(...)
cloud.archive_buckets.create(...)
cloud.archive_buckets.upload_file(...)

cloud.security_groups.create(name="web-servers")
cloud.security_groups.create_rule(sg_id, direction="ingress", protocol="tcp", port_range="22")

cloud.backups.execute(backup_id=42)
```

## Exception Hierarchy

Base:
- `MTNCloudError`

Specialized:
- `AuthenticationError` — 401, bad/expired token or missing credentials
- `ForbiddenError` — 403, insufficient permissions
- `NotFoundError` — 404, resource does not exist
- `ValidationError` — 400, invalid input; carries `.errors` list
- `QuotaExceededError` — 402, limit reached; carries `.quota_type`, `.current`, `.limit`
- `ResourceConflictError` — 409, duplicate or invalid state transition
- `RateLimitError` — 429, too many requests; carries `.retry_after`
- `ServerError` — 5xx backend failures
- `TimeoutError` — request timeout; carries `.timeout`

Catch specific exceptions first, then fall back to `MTNCloudError`.

## Response Models

Resource methods return typed Pydantic models, for example:
- `Instance`
- `Cloud`
- `Group`
- `ServicePlan`
- `StorageBucket`
- `ArchiveBucket`
- `ArchiveFile`
- `SecurityGroup`, `SecurityGroupRule`
- `Snapshot`
- `ResourcePool`
- `Backup`, `BackupJob`, `BackupResult`
- `VirtualImage`

## Naming Conventions

- `*_id` means numeric MTN Cloud resource ID.
- `bucket_name` in archive methods means archive bucket name.
- `remote_path` means path inside archive storage.
- `local_path` / `local_directory` refer to local filesystem paths.
