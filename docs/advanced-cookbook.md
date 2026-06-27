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
# Iterate page-by-page
for page in cloud.instances.paginate(page_size=100, status="running"):
    print("page-size:", len(page))
    for instance in page:
        print(instance.id, instance.name)

# Or flatten all items directly
all_running = list(cloud.instances.iter_all(page_size=100, status="running"))
print("total:", len(all_running))
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
    QuotaExceededError,
    RateLimitError,
    ResourceConflictError,
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
except QuotaExceededError as exc:
    # Account limit reached for this resource type.
    print(f"Quota exceeded: {exc.quota_type} ({exc.current}/{exc.limit})")
    raise
except ResourceConflictError as exc:
    # Resource already exists or is in an incompatible state.
    print(f"Conflict: {exc}")
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
group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
target_type = cloud.instance_types.get_by_code("MTN-U24.04LTS")

plans = cloud.instances.list_service_plans(
    zone_id=group.cloud_ids[0],
    layout_id=target_type.default_layout_id,
    group_id=group.id,
)
target_plan = next(p for p in plans if p["name"] == "G2S4")

pool = cloud.instances.get_resource_pool("my-project", group=group.name)

instance = cloud.instances.create(
    name="api-worker-01",
    cloud="MTNNG_CLOUD_AZ_1",
    type=target_type.code,
    group="MTNNG_CLOUD_AZ_1",
    layout=target_type.default_layout_id,
    plan=target_plan["id"],
    resource_pool_id=pool.code,
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
    resource_pool_id="pool-214",
)
logger.info("instance-created id=%s status=%s", instance.id, instance.status)
```
