# Routers: `cloud.routers`

Access via `cloud.routers`. List and get inspect router records. Creation and
deletion support only MTN's `neutronRouter` type; the type is resolved automatically.

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, **filters) -> list[Router]`

- Endpoint: `GET /api/networks/routers`
- Parameters: shared list query arguments; see [API conventions](./index.md).
- Returns: router records visible to the account, including their type and status.
- Raises: common API exceptions.

### `get(resource_id: int) -> Router`

- Endpoint: `GET /api/networks/routers/{id}`
- Parameters: numeric Morpheus router ID.
- Returns: `Router`, including `status`, `type`, `site`, `zone`, `interfaces`,
  `external_network`, `external_ip`, and `external_id` when available.
- Raises: `NotFoundError` when absent; common API exceptions.

### `create(name: str, *, group_id: int, cloud_id: int, resource_pool_id: int, internal_subnet_ids: list[int], external_network_id: int | None = None, enabled: bool = True) -> Router`

- Endpoint: `POST /api/networks/routers`, followed by a router read.
- Parameters:
    - `name`: nonempty router name.
    - `group_id`, `cloud_id`: group and its selected cloud.
    - `resource_pool_id`: numeric project ID from `instances.get_resource_pool(...).id`.
    - `internal_subnet_ids`: nonempty list of positive Morpheus subnet IDs from
      `networks.list_subnets(...)`. Subnets must belong to the selected project.
    - `external_network_id`: optional public network ID from `networks.get_by_name(...).id`.
    - `enabled`: whether the router is enabled; defaults to `True`.
- Returns: initial `Router` record. Provisioning may still be in progress.
- Raises: Pydantic `ValidationError` for invalid inputs; `ValueError` when the MTN
  router type is unavailable; common API exceptions. A failed read after successful
  submission raises `MTNCloudError` with `response["router_id"]` for cleanup.

Call `wait_until_ready(router.id)` to confirm backend readiness.

### `delete(router_id: int) -> bool`

- Endpoints: reads the router to check its type, then `DELETE /api/networks/routers/{id}`.
- Returns: `True` when deletion is submitted or the router is already absent.
- Raises: `ValueError` for a non-MTN router; common API exceptions.

Call `wait_until_deleted(router_id)` to confirm removal. Existing networks and
resource pools are not deleted.

### `wait_until_ready(router_id: int, timeout: float = 300, poll_interval: float = 5) -> Router`

- Endpoint: polls `GET /api/networks/routers/{id}`.
- Parameters: router ID and positive timeout/poll interval in seconds.
- Returns: router with status `ok`, `available`, or `active`.
- Raises: `MTNCloudError` for `failed`/`error` status, SDK `TimeoutError` on timeout,
  `ValueError` for invalid timing or a non-MTN router, and common API exceptions.
  Provisioning failure and polling timeout errors include `response["router_id"]`.

### `wait_until_deleted(router_id: int, timeout: float = 300, poll_interval: float = 5) -> bool`

- Endpoint: polls `GET /api/networks/routers/{id}` until it returns 404.
- Returns: `True` after removal.
- Raises: SDK `TimeoutError` with `response["router_id"]`, `ValueError` for invalid
  timing, and common API exceptions. Authorization and server errors are not
  treated as successful deletion.

See the [Networking guide](../networking.md#create-an-mtn-router) for a complete example.
