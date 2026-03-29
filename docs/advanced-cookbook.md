# Advanced Cookbook

Production-friendly patterns for robust automation.

## Configure a Resilient Client

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(
    token="your-api-token",
    timeout=45,
    # Retry values are controlled through MTNCloudConfig defaults:
    # max_retries=3, retry_delay=1.0
)
```

Use environment variables for deployment:

```bash
export MTN_CLOUD_TOKEN="..."
export MTN_CLOUD_TIMEOUT="45"
export MTN_CLOUD_MAX_RETRIES="5"
export MTN_CLOUD_RETRY_DELAY="1.5"
```

## Pattern: Idempotent "Get or Create"

```python
from mtn_cloud import NotFoundError

def get_or_create_archive_bucket(cloud, name: str, storage_provider_id: int):
    try:
        return cloud.archive_buckets.get_by_name(name)
    except NotFoundError:
        return cloud.archive_buckets.create(
            name=name,
            storage_provider_id=storage_provider_id,
            visibility="private",
        )
```

## Pattern: Controlled Pagination

```python
def list_all_instances(cloud, page_size: int = 100):
    offset = 0
    all_items = []

    while True:
        page = cloud.instances.list(max_results=page_size, offset=offset)
        if not page:
            break
        all_items.extend(page)
        if len(page) < page_size:
            break
        offset += page_size

    return all_items
```

## Pattern: Safe Bulk Upload with Preflight

Use `dry_run=True` first, then enforce strict checks.

```python
preview = cloud.archive_buckets.upload_directory(
    bucket_name="my-archive",
    remote_path="/imports/",
    local_directory="./data",
    recursive=True,
    dry_run=True,
)

if preview.skipped_count > 0:
    for skipped in preview.skipped_files[:20]:
        print("SKIP:", skipped.local_path, skipped.reason)
    raise RuntimeError("Fix skipped files before uploading")

result = cloud.archive_buckets.upload_directory(
    bucket_name="my-archive",
    remote_path="/imports/",
    local_directory="./data",
    recursive=True,
    strict=True,
)

print(
    f"uploaded={result.uploaded_count} "
    f"failed={result.failed_count} "
    f"skipped={result.skipped_count}"
)
```

## Pattern: Explicit Error Branching

```python
from mtn_cloud import (
    AuthenticationError,
    MTNCloudError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

try:
    cloud.networks.create(
        name="prod-net",
        cloud_id=1,
        group_id=621,
        type_id=8,
        cidr="10.42.10.0/24",
    )
except AuthenticationError:
    # Token missing/expired.
    raise
except RateLimitError as exc:
    # Use retry_after where available.
    print(f"Rate limited. retry_after={exc.retry_after}")
    raise
except ValidationError as exc:
    print("Validation issue:", exc)
    raise
except NotFoundError as exc:
    print("Referenced resource not found:", exc)
    raise
except MTNCloudError as exc:
    print("Generic SDK/API failure:", exc)
    raise
```

## Pattern: Context Manager for Long Scripts

```python
from mtn_cloud import MTNCloud

with MTNCloud(token="your-api-token") as cloud:
    for instance in cloud.instances.list(max_results=20):
        print(instance.id, instance.name, instance.status)
```

## Pattern: Deterministic Selection Logic

Pick explicit templates and plans instead of "first result" in production.

```python
target_type = cloud.instance_types.get_by_code("MTN-U24.04LTS")
target_plan = cloud.plans.get_by_name("G2S4")

instance = cloud.instances.create(
    name="api-worker-01",
    cloud="MTNNG_CLOUD_AZ_1",
    type=target_type.code,
    group="MTNNG_CLOUD_AZ_1",
    layout=target_type.default_layout_id,
    plan=target_plan.id,
)
```

## Pattern: Structured Logging Around SDK Calls

```python
import logging

logger = logging.getLogger("infra.provision")

logger.info("creating-instance name=%s cloud=%s type=%s", "api-worker-01", "MTNNG_CLOUD_AZ_1", "MTN-U24.04LTS")
instance = cloud.instances.create(
    name="api-worker-01",
    cloud="MTNNG_CLOUD_AZ_1",
    type="MTN-U24.04LTS",
    group="MTNNG_CLOUD_AZ_1",
    layout=309,
    plan=6776,
)
logger.info("instance-created id=%s status=%s", instance.id, instance.status)
```

