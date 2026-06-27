# Recipes

Three complete, real-world workflows. Each assumes an authenticated client:

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")
```

For isolated patterns (retries, pagination, idempotency), see the [Advanced Cookbook](./advanced-cookbook.md).

## Provision a Linux VM with SSH

Discover the inputs, open SSH in a security group, provision, and wait until it's reachable.

```python
group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
itype = cloud.instance_types.get_by_code("MTN-CS10")
pool = cloud.instances.get_resource_pool("my-project", group=group.name)
plans = cloud.instances.list_service_plans(
    zone_id=group.cloud_ids[0], layout_id=itype.default_layout_id, group_id=group.id,
)

sg = cloud.security_groups.create(name="linux-ssh", description="SSH access")
cloud.security_groups.create_rule(
    sg.id, name="allow-ssh", direction="ingress", protocol="tcp",
    port_range="22", source_type="cidr", source="200.200.113.15/32",
)

instance = cloud.instances.create(
    name="linux-web-01",
    cloud=group.name,
    type=itype.code,
    group=group.name,
    layout=itype.default_layout_id,
    plan=plans[0]["id"],
    resource_pool_id=pool.code,
    availability_zone="Lagos-AZ-1-fd1",
    security_group=sg.name,
    create_user=True,
)
instance = cloud.instances.wait_until_running(instance.id, timeout=600)
print("ready:", instance.primary_ip)
```

SSH **keys** are uploaded once in the console (**User Settings → SSH Keys**); the SDK controls the firewall rule and user creation. Then: `ssh <your-user>@<instance.primary_ip>`.

## Back up a folder to MTN Object Storage

Register the provider and bucket idempotently, preview with a dry run, then upload.

```python
from mtn_cloud import NotFoundError

try:
    storage = cloud.storage_buckets.get_by_name("my-s3-storage")
except NotFoundError:
    storage = cloud.storage_buckets.create_s3(
        name="my-s3-storage",
        bucket_name="my-app-objects",
        access_key="your-access-key",                      # from MOS email
        secret_key="your-secret-key",                      # from MOS email
        endpoint="https://ps1csp-s3.ict.mtn.com.ng:9021",
        create_bucket=True,
    )

try:
    archive = cloud.archive_buckets.get_by_name("my-app-archives")
except NotFoundError:
    archive = cloud.archive_buckets.create(
        name="my-app-archives", storage_provider_id=storage.id, visibility="private",
    )

preview = cloud.archive_buckets.upload_directory(
    bucket_name=archive.name, remote_path="/backups/",
    local_directory="./data", recursive=True, dry_run=True,
)
if preview.skipped_count:
    raise RuntimeError(f"{preview.skipped_count} files would be skipped")

result = cloud.archive_buckets.upload_directory(
    bucket_name=archive.name, remote_path="/backups/",
    local_directory="./data", recursive=True, strict=True,
)
print(f"uploaded={result.uploaded_count} failed={result.failed_count}")
```

## Tear down demo resources

Delete in dependency order — instances first, then the firewall and network they used. Deletes are best-effort so one failure doesn't block the rest.

```python
from mtn_cloud import MTNCloudError

def cleanup(manager, items, label):
    for item in items:
        if (item.name or "").startswith("demo-"):
            try:
                manager.delete(item.id)
                print("deleted", label, item.id)
            except MTNCloudError as exc:
                print("skip", label, item.id, exc)

cleanup(cloud.instances, cloud.instances.list(max_results=100), "instance")
cleanup(cloud.security_groups, cloud.security_groups.list(), "security-group")
cleanup(cloud.networks, cloud.networks.list(), "network")
```

A network or security group can't be deleted while an instance still references it — always remove instances first and let them finish.
