# Resource: `cloud.backups` (`BackupsResource`)

### `list(max_results=None, offset=0, phrase=None, **filters) -> list[Backup]`

- Endpoint: `GET /api/backups`
- Parameters:
    - Shared list args (see [API Reference](./index.md#shared-list-query-arguments))
- Returns: `list[Backup]`
- Raises: common API exceptions

### `get(backup_id: int) -> Backup`

- Endpoint: `GET /api/backups/{backup_id}`
- Returns: `Backup`
- Raises: common API exceptions

### `execute(backup_id: int) -> dict[str, Any]`

- Endpoint: `POST /api/backups/{backup_id}/execute`
- Triggers an immediate out-of-schedule backup run
- Returns: raw execution status response
- Raises: common API exceptions

### `list_results(backup_id: int, max_results=None) -> list[BackupResult]`

- Endpoint: `GET /api/backups/{backup_id}/results`
- Parameters:
    - `max_results`: maps to query `max`
- Returns: `list[BackupResult]` — each result carries `status`, `size_in_mb`, `duration_millis`, `start_date`, `end_date`
- Raises: common API exceptions

### `delete(backup_id: int) -> bool`

- Endpoint: `DELETE /api/backups/{backup_id}`
- Returns: `True` on success
- Raises: common API exceptions

---

## Job management

### `list_jobs(max_results=None, offset=0) -> list[BackupJob]`

- Endpoint: `GET /api/backups/jobs`
- Returns: `list[BackupJob]`
- Raises: common API exceptions

### `get_job(job_id: int) -> BackupJob`

- Endpoint: `GET /api/backups/jobs/{job_id}`
- Returns: `BackupJob`
- Raises: common API exceptions

### `execute_job(job_id: int) -> dict[str, Any]`

- Endpoint: `POST /api/backups/jobs/{job_id}/execute`
- Triggers an immediate run of all backups under the job
- Returns: raw execution status response
- Raises: common API exceptions
