# Resource: `cloud.instance_types` (`InstanceTypesResource`)

### `list(max_results=None, offset=0, sort="name", direction="asc", phrase=None, name=None, code=None, category=None, featured=None, **filters) -> list[InstanceType]`

- Endpoint: `GET /api/instance-types`
- Parameters:
    - Shared list args
    - `name`: name filter
    - `code`: code filter
    - `category`: category filter (`os`, `sql`, `web`, `apps`, etc.)
    - `featured`: feature flag filter
- Returns: `list[InstanceType]`
- Raises: common API exceptions

### `get(instance_type_id: int) -> InstanceType`

- Endpoint: `GET /api/instance-types/{instance_type_id}`
- Returns: `InstanceType`
- Raises: common API exceptions

### `get_by_code(code: str) -> InstanceType`

- Endpoint sequence:
    - `GET /api/instance-types?code=<code>&max=1`
- Returns: `InstanceType`
- Raises:
    - common API exceptions
    - `NotFoundError` when no match

### `get_by_name(name: str) -> InstanceType`

- Endpoint sequence:
    - `GET /api/instance-types?name=<name>&max=1`
- Returns: `InstanceType`
- Raises:
    - common API exceptions
    - `NotFoundError` when no match

### `list_os() -> list[InstanceType]`

- Endpoint: `GET /api/instance-types?category=os`
- Returns: OS instance types
- Raises: common API exceptions

### `list_databases() -> list[InstanceType]`

- Endpoint: `GET /api/instance-types?category=sql`
- Returns: database instance types
- Raises: common API exceptions

### `list_web() -> list[InstanceType]`

- Endpoint: `GET /api/instance-types?category=web`
- Returns: web instance types
- Raises: common API exceptions

### `list_apps() -> list[InstanceType]`

- Endpoint: `GET /api/instance-types?category=apps`
- Returns: app instance types
- Raises: common API exceptions

