# Resource: `cloud.clouds` (`CloudsResource`)

### `list(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, group_id=None, type_code=None, **filters) -> list[Cloud]`

- Endpoint: `GET /api/zones`
- Parameters:
    - Shared list args
    - `name`: cloud/zone name filter
    - `group_id`: mapped to `groupId`
    - `type_code`: mapped to `type` (example: `openstack`)
- Returns: `list[Cloud]`
- Raises: common API exceptions

### `list_openstack(max_results=None, offset=0, sort=None, direction=None, phrase=None, name=None, group_id=None, **filters) -> list[Cloud]`

- Endpoint: `GET /api/zones?type=openstack`
- Returns: OpenStack-only clouds
- Raises: common API exceptions

### `get(cloud_id: int) -> Cloud`

- Endpoint: `GET /api/zones/{cloud_id}`
- Returns: `Cloud`
- Raises: common API exceptions

### `get_by_name(name: str) -> Cloud`

- Endpoint sequence:
    - `GET /api/zones?name=<name>&max=1`
- Returns: `Cloud`
- Raises:
    - common API exceptions
    - `NotFoundError` when no match

### `list_by_group(group_id: int) -> list[Cloud]`

- Endpoint: `GET /api/zones?groupId=<group_id>`
- Returns: `list[Cloud]`
- Raises: common API exceptions

