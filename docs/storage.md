# Storage

Use this guide for MTN Object Storage onboarding and SDK storage/archive flows.

## Before You Start

To use storage APIs, first order **MTN Object Storage** from:
`Provisioning -> Catalog`.

After ordering, your credentials are sent by email:
- Access key
- Secret key
- Endpoint URL

You will use these values when creating your storage provider in the SDK.
MTN Object Storage on this platform is hosted in Lagos.

## MTN Object Storage

MTN Object Storage is a scalable, secure, and highly available service on the
MTN Cloud Platform for storing and accessing data.

## Pricing (As Shared by MTN Cloud)

- `₦0.07` per GB per hour
- `₦2` per GB per day
- `₦50` per GB per month

Confirm current pricing in the Catalog before budgeting or automation rollouts.

## Storage vs Archive in the SDK

- `cloud.storage_buckets`: provider configuration (endpoint, keys, backing bucket)
- `cloud.archive_buckets`: logical file container linked to a storage provider
- File operations (upload/list/download/copy/delete) happen through archive APIs

## Create Storage Provider and Archive Bucket

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

storage = cloud.storage_buckets.create_s3(
    name="my-s3-storage",
    bucket_name="my-app-objects",
    access_key="your-access-key",          # from email
    secret_key="your-secret-key",          # from email
    endpoint="https://your-endpoint",      # from email
    create_bucket=True,
)

archive = cloud.archive_buckets.create(
    name="my-app-archives",
    storage_provider_id=storage.id,
    visibility="private",
)

print(storage.id, archive.id)
```

## Upload and List Files

```python
uploaded = cloud.archive_buckets.upload_file(
    bucket_name=archive.name,
    remote_path="/",
    local_path="./backup.sql",
)
print(uploaded.id, uploaded.name)

files = cloud.archive_buckets.list_files(
    bucket_name=archive.name,
    remote_path="/",
    full_tree=True,
)
print(f"Files: {len(files)}")
```

## Bulk Upload (Directory)

```python
summary = cloud.archive_buckets.upload_directory(
    bucket_name=archive.name,
    remote_path="/imports/",
    local_directory="./reports",
    recursive=True,
    dry_run=False,
    strict=False,
)

print(
    f"scanned={summary.scanned_count} "
    f"uploaded={summary.uploaded_count} "
    f"failed={summary.failed_count} "
    f"skipped={summary.skipped_count}"
)
```

For deeper patterns, see [Advanced Cookbook](./advanced-cookbook.md#pattern-safe-bulk-upload-with-preflight).

## Download a File

`download_file` returns raw bytes when no `local_path` is given, or writes the file and returns the path when one is provided.

```python
# Return bytes directly
content = cloud.archive_buckets.download_file(
    bucket_name=archive.name,
    remote_path="/imports/report.csv",
)
print(f"Downloaded {len(content)} byte(s)")

# Save to disk
saved_path = cloud.archive_buckets.download_file(
    bucket_name=archive.name,
    remote_path="/imports/report.csv",
    local_path="./downloads/report.csv",
)
print(f"Saved to {saved_path}")
```

## Copy a File Between Buckets

Downloads from the source and re-uploads to the destination. Source and destination may be the same bucket.

```python
cloud.archive_buckets.copy_file(
    source_bucket_name="my-app-archives",
    source_path="/imports/report.csv",
    destination_bucket_name="my-backup-archives",
    destination_path="/backups/",
    destination_filename="report-2026-06-26.csv",  # optional rename
)
```

## Delete a File

Files are deleted by their numeric ID, which is available on the `ArchiveFile` model returned by `list_files` or `upload_file`.

```python
files = cloud.archive_buckets.list_files(
    bucket_name=archive.name,
    remote_path="/imports/",
)
for f in files:
    print(f.id, f.name)
    cloud.archive_buckets.delete_file(f.id)
```

## Retention Policy on Storage Buckets

When creating a storage bucket you can set a retention policy that controls how old objects are handled:

```python
storage = cloud.storage_buckets.create_s3(
    name="my-s3-storage",
    bucket_name="my-app-objects",
    access_key="your-access-key",
    secret_key="your-secret-key",
    endpoint="https://your-endpoint",
    create_bucket=True,
    retention_policy_type="delete",   # "backup", "delete", or "none" (default)
    retention_policy_days=30,         # delete objects older than 30 days
)
```
