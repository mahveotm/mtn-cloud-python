# Resource: `cloud.storage_buckets` (`StorageBucketsResource`)

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

