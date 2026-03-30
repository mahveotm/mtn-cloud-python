# Resource: `cloud.plans` (`PlansResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, **filters) -> list[ServicePlan]`

- Endpoint: `GET /api/service-plans`
- Parameters:
    - Shared list args
    - `name`: plan name filter
- Returns: `list[ServicePlan]`
- Raises: common API exceptions

### `get(plan_id: int) -> ServicePlan`

- Endpoint: `GET /api/service-plans/{plan_id}`
- Returns: `ServicePlan`
- Raises: common API exceptions

### `get_by_name(name: str) -> ServicePlan`

- Endpoint sequence:
    - `GET /api/service-plans?name=<name>&max=1`
- Returns: `ServicePlan`
- Raises:
    - common API exceptions
    - `NotFoundError` when no match

### `find(cores=None, memory_gb=None, storage_gb=None) -> ServicePlan | None`

Client-side selector for first plan meeting minimum requirements.

- Endpoint sequence:
    - `GET /api/service-plans`
- Parameters:
    - `cores`: minimum CPU cores
    - `memory_gb`: minimum memory in GB
    - `storage_gb`: minimum storage in GB
- Returns:
    - `ServicePlan` first match
    - `None` if no plan satisfies constraints
- Raises: common API exceptions

