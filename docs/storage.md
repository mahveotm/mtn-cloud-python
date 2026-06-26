# Storage

Use this guide for MTN Object Storage onboarding and all SDK storage and archive operations.

## Before You Start: Order MTN Object Storage

MTN Object Storage (MOS) is ordered separately from compute resources. You must do this in the console once before any storage SDK calls will work.

1. Go to **Provisioning → Catalog** and select **MTN Object Storage**.
2. Click **Order Now**. The status shows "submitted" while credentials are generated.
3. Your **access key**, **secret key**, and **endpoint URL** arrive by email.

The Lagos endpoint is: `https://ps1csp-s3.ict.mtn.com.ng:9021`

Keep the email — these credentials are passed directly into the SDK for every storage call.

## Storage vs Archive: How the SDK Models This

MTN Object Storage is S3-compatible. The SDK splits management into two layers:

| Resource | SDK manager | What it represents |
|---|---|---|
| Storage provider | `cloud.storage_buckets` | The connection to MOS — credentials, endpoint, backing bucket |
| Archive bucket | `cloud.archive_buckets` | A logical file container linked to a storage provider |

File operations (upload, download, list, copy, delete) all go through the archive bucket layer.
You create the storage provider once, then create one or more archive buckets on top of it.

## Pricing (As Shared by MTN Cloud)

| Period | Rate |
|---|---|
| Per hour | ₦0.07 per GB |
| Per day | ₦2 per GB |
| Per month | ₦50 per GB |

Confirm current pricing in the Catalog before budgeting.

## Create a Storage Provider and Archive Bucket

Pass the credentials from your MOS email directly. `create_bucket=True` tells the platform to create the backing bucket and enable path-style access — both are required for MOS to work.

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

storage = cloud.storage_buckets.create_s3(
    name="my-s3-storage",
    bucket_name="my-app-objects",
    access_key="your-access-key",                         # from email
    secret_key="your-secret-key",                         # from email
    endpoint="https://ps1csp-s3.ict.mtn.com.ng:9021",    # Lagos endpoint from email
    create_bucket=True,                                   # required for MOS
)

archive = cloud.archive_buckets.create(
    name="my-app-archives",
    storage_provider_id=storage.id,
    visibility="private",
)

print(storage.id, archive.id)
```

## Upload and List Files

Filenames cannot contain spaces, dots at the start, or special characters (`\ / : * ? " < > | # % & + ' ; = ^`).

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
    full_tree=True,     # include subdirectories
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

For a safe preflight-before-upload pattern, see [Advanced Cookbook](./advanced-cookbook.md#pattern-safe-bulk-upload-with-preflight).

## Download a File

Returns raw bytes when no `local_path` is given, or writes to disk and returns the path.

```python
# Return bytes
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
    destination_filename="report-backup.csv",   # optional rename
)
```

## Delete a File

Files are deleted by numeric ID, available on the `ArchiveFile` model returned by `list_files` or `upload_file`.

```python
files = cloud.archive_buckets.list_files(
    bucket_name=archive.name,
    remote_path="/imports/",
)
for f in files:
    print(f.id, f.name)
    cloud.archive_buckets.delete_file(f.id)
```

## Retention Policy

Set a retention policy on the storage provider to automatically clean up old objects:

```python
storage = cloud.storage_buckets.create_s3(
    name="my-s3-storage",
    bucket_name="my-app-objects",
    access_key="your-access-key",
    secret_key="your-secret-key",
    endpoint="https://ps1csp-s3.ict.mtn.com.ng:9021",
    create_bucket=True,
    retention_policy_type="delete",     # "backup", "delete", or "none" (default)
    retention_policy_days=30,           # remove objects older than 30 days
)
```

## Regenerating Credentials

If your MOS secret key is compromised, regenerate it from **Provisioning → Catalog → MTN Object Storage**. The platform sends new credentials to all tenancy users by email and automatically revalidates linked storage buckets. Access keys are not changed during regeneration.

After regenerating, update your SDK calls (or env vars) with the new secret key.
