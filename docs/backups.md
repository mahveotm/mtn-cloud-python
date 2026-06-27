# Backups

Use this guide to list, inspect, and trigger backup jobs via the SDK.

## How Backups Work on MTN Cloud

Backups are configured and scheduled through the MTN Cloud Console under **Backups**. The SDK gives you read and execution access — you can list configured backups, inspect their last run status, retrieve execution results, and trigger an immediate run. Creating new backup configurations is done in the console.

Two distinct objects exist in the API:
- **Backup** — a configuration attached to a specific instance or server.
- **Backup Job** — a schedule (cron expression + retention policy) that groups one or more backups.

## List Backups

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

backups = cloud.backups.list()
for b in backups:
    print(f"{b.id}  {b.name}  last_run={b.last_run}  status={b.last_status}")
```

## Get a Backup

```python
backup = cloud.backups.get(42)
print(backup.name, backup.enabled, backup.retention_count)
```

## Execute a Backup Immediately

Triggers an out-of-schedule run. Useful before a major change.

```python
result = cloud.backups.execute(backup_id=42)
print(result)
```

## Get Execution Results

Returns the history of runs for a specific backup — each with size, duration, and status.

```python
results = cloud.backups.list_results(backup_id=42)
for r in results:
    print(f"  {r.start_date}  status={r.status}  size={r.size_in_mb} MB  duration={r.duration_millis} ms")
```

## Backup Jobs

Backup jobs are the scheduling layer. A single job can cover multiple backups.

```python
# List jobs
jobs = cloud.backups.list_jobs()
for job in jobs:
    print(f"{job.id}  {job.name}  cron={job.cron_expression}  last_status={job.last_status}")

# Get a specific job
job = cloud.backups.get_job(job_id=10)

# Execute a job immediately
cloud.backups.execute_job(job_id=10)
```

## Delete a Backup Configuration

Deletes the backup configuration but does not delete existing backup result data.

```python
cloud.backups.delete(backup_id=42)
```

## Notes

- Backup **configuration** (creating new backup jobs, attaching them to instances) is done in the MTN Cloud Console under **Backups → Jobs**.
- Backup **results** and **executions** are accessible via the SDK.
- `b.instance_id` and `b.server_id` are convenience properties that extract IDs from the nested `instance`/`server` dict.
