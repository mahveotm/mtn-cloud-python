# Resource: `cloud.groups` (`GroupsResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, **filters) -> list[Group]`

- Endpoint: `GET /api/groups`
- Parameters:
    - Shared list args
    - `name`: group name filter
- Returns: `list[Group]`
- Raises: common API exceptions

### `get(group_id: int) -> Group`

- Endpoint: `GET /api/groups/{group_id}`
- Returns: `Group`
- Raises: common API exceptions

### `get_by_name(name: str) -> Group`

- Endpoint sequence:
    - `GET /api/groups?name=<name>&max=1`
- Returns: `Group`
- Raises:
    - common API exceptions
    - `NotFoundError` when no match

