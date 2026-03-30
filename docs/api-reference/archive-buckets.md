# Resource: `cloud.archive_buckets` (`ArchiveBucketsResource`)

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

