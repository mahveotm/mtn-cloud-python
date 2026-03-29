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

For deeper patterns, see [storage usage.md](../storage%20usage.md).
