# Resource: `cloud.instances` (`InstancesResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, status=None, cloud_id=None, group_id=None, labels=None, **filters) -> list[Instance]`

- Endpoint: `GET /api/instances`
- Parameters:
    - Shared list args (see [API Reference](./index.md#shared-list-query-arguments))
    - `name`: exact name filter
    - `status`: status filter
    - `cloud_id`: mapped to query `zoneId`
    - `group_id`: mapped to query `siteId`
    - `labels`: list mapped to comma-delimited query `labels`
- Returns: `list[Instance]`
- Raises: common API exceptions

### `get(instance_id: int) -> Instance`

- Endpoint: `GET /api/instances/{instance_id}`
- Parameters:
    - `instance_id`: instance numeric ID
- Returns: `Instance`
- Raises: common API exceptions

### `get_by_name(name: str) -> Instance`

- Endpoint sequence:
    - `GET /api/instances?name=<name>&max=1`
- Parameters:
    - `name`: instance name
- Returns: `Instance`
- Raises:
    - common API exceptions
    - `NotFoundError` when no instance matches

### `create(name: str, *, cloud: str, type: str, group: str, layout: int, plan: int, description=None, environment=None, labels=None, tags=None, copies=1, layout_size=1, resource_pool_id=None, availability_zone=None, security_group="default", os_external_network_id=None, create_user=True, workflow_id=None, shutdown_days=None, expire_days=None, create_backup=None, security_groups=None, ports=None, volumes=None, network_interfaces=None, options=None) -> Instance`

- Endpoint sequence:
    - `GET /api/groups?name=<group>&max=1` (resolve group name to `group_id`)
    - `POST /api/instances`
- Parameters:
    - Required core fields:
        - `name`: new instance name
        - `cloud`: cloud/zone name (example: `MTNNG_CLOUD_AZ_1`)
        - `type`: instance type code (example: `MTN-CS10`)
        - `group`: group/site name (resolved to ID)
        - `layout`: layout ID
        - `plan`: service plan ID
    - Optional metadata:
        - `description`, `environment`, `labels`, `tags`
    - Optional sizing/provisioning:
        - `copies`, `layout_size`
    - Optional MTN/OpenStack-specific provisioning:
        - `resource_pool_id`, `availability_zone`, `security_group`, `os_external_network_id`, `create_user`
    - Optional automation:
        - `workflow_id`, `shutdown_days`, `expire_days`, `create_backup`
    - Optional networking/storage details:
        - `security_groups`, `ports`, `volumes`, `network_interfaces`, `options`
- Returns: `Instance`
- Raises:
    - common API exceptions
    - `NotFoundError` when `group` cannot be resolved

### `update(instance_id: int, name=None, description=None, labels=None) -> Instance`

- Endpoint: `PUT /api/instances/{instance_id}`
- Parameters:
    - `instance_id`: target instance ID
    - `name`: replacement name
    - `description`: replacement description
    - `labels`: replacement labels list
- Returns: `Instance`
- Raises: common API exceptions

### `delete(instance_id: int, preserve_volumes=False, force=False) -> bool`

- Endpoint: `DELETE /api/instances/{instance_id}`
- Parameters:
    - `instance_id`: target instance ID
    - `preserve_volumes`: adds query `preserveVolumes=on`
    - `force`: adds query `force=on`
- Returns: `True` on successful deletion request
- Raises: common API exceptions

### `start(instance_id: int) -> Instance`

- Endpoint sequence:
    - `PUT /api/instances/{instance_id}/start`
    - `GET /api/instances/{instance_id}`
- Returns: refreshed `Instance`
- Raises: common API exceptions

### `stop(instance_id: int) -> Instance`

- Endpoint sequence:
    - `PUT /api/instances/{instance_id}/stop`
    - `GET /api/instances/{instance_id}`
- Returns: refreshed `Instance`
- Raises: common API exceptions

### `restart(instance_id: int) -> Instance`

- Endpoint sequence:
    - `PUT /api/instances/{instance_id}/restart`
    - `GET /api/instances/{instance_id}`
- Returns: refreshed `Instance`
- Raises: common API exceptions

### `suspend(instance_id: int) -> Instance`

- Endpoint sequence:
    - `PUT /api/instances/{instance_id}/suspend`
    - `GET /api/instances/{instance_id}`
- Returns: refreshed `Instance`
- Raises: common API exceptions

### `resize(instance_id: int, plan_id: int) -> Instance`

- Endpoint sequence:
    - `PUT /api/instances/{instance_id}/resize`
    - `GET /api/instances/{instance_id}`
- Parameters:
    - `plan_id`: new service plan ID
- Returns: resized `Instance`
- Raises: common API exceptions

### `wait_for_status(instance_id: int, target_status: str, timeout: int = 300, poll_interval: int = 5) -> Instance`

Client-side polling helper.

- Endpoint sequence:
    - repeated `GET /api/instances/{instance_id}` until target status or timeout
- Parameters:
    - `target_status`: desired status string (`running`, `stopped`, etc.)
    - `timeout`: max wait in seconds
    - `poll_interval`: sleep interval between polls
- Returns: `Instance` once target status matches
- Raises:
    - common API exceptions from internal `get`
    - `TimeoutError` when timeout is exceeded
    - `RuntimeError` if instance enters `failed` state

### `wait_until_running(instance_id: int, timeout: int = 300) -> Instance`

- Endpoint behavior: same as `wait_for_status(..., target_status="running")`
- Returns: `Instance`
- Raises: same as `wait_for_status`

### `wait_until_stopped(instance_id: int, timeout: int = 300) -> Instance`

- Endpoint behavior: same as `wait_for_status(..., target_status="stopped")`
- Returns: `Instance`
- Raises: same as `wait_for_status`

### `get_console(instance_id: int) -> dict[str, Any]`

- Endpoint: `GET /api/instances/{instance_id}/console`
- Returns: raw console payload (`url`, credentials, metadata)
- Raises: common API exceptions

### `get_history(instance_id: int, max_results: int | None = None) -> list[dict[str, Any]]`

- Endpoint: `GET /api/instances/{instance_id}/history`
- Parameters:
    - `max_results`: maps to query `max`
- Returns: list from response key `processes`
- Raises: common API exceptions

