# Resource: `cloud.security_groups` (`SecurityGroupsResource`)

### `list(max_results=None, offset=0, phrase=None, name=None, **filters) -> list[SecurityGroup]`

- Endpoint: `GET /api/security-groups`
- Parameters:
    - Shared list args (see [API Reference](./index.md#shared-list-query-arguments))
    - `name`: filter by name
- Returns: `list[SecurityGroup]` — each includes its embedded `rules` list
- Raises: common API exceptions

### `get(security_group_id: int) -> SecurityGroup`

- Endpoint: `GET /api/security-groups/{security_group_id}`
- Returns: `SecurityGroup` with all rules populated
- Raises: common API exceptions

### `get_by_name(name: str) -> SecurityGroup`

- Endpoint sequence:
    - `GET /api/security-groups?name=<name>&max=1`
- Parameters:
    - `name`: security group name
- Returns: `SecurityGroup`
- Raises:
    - common API exceptions
    - `NotFoundError` when no group matches

### `create(name: str, *, description=None) -> SecurityGroup`

- Endpoint: `POST /api/security-groups`
- Parameters:
    - `name`: group name
    - `description`: optional description
- Returns: created `SecurityGroup`
- Raises: common API exceptions

### `update(security_group_id: int, *, name=None, description=None) -> SecurityGroup`

- Endpoint: `PUT /api/security-groups/{security_group_id}`
- Parameters:
    - `name`: replacement name
    - `description`: replacement description
- Returns: updated `SecurityGroup`
- Raises: common API exceptions

### `delete(security_group_id: int) -> bool`

- Endpoint: `DELETE /api/security-groups/{security_group_id}`
- Returns: `True` on success
- Raises: common API exceptions

---

## Rule management

### `list_rules(security_group_id: int) -> list[SecurityGroupRule]`

- Endpoint sequence:
    - `GET /api/security-groups/{security_group_id}` (rules embedded in response)
- Returns: `list[SecurityGroupRule]`
- Raises: common API exceptions

### `create_rule(security_group_id: int, *, name=None, direction="ingress", policy="accept", protocol=None, port_range=None, destination_port_range=None, source_type="all", source=None, destination_type="instance", destination=None, ethertype=None, priority=None, enabled=None) -> SecurityGroupRule`

- Endpoint: `POST /api/security-groups/{security_group_id}/rules`
- Parameters:
    - `direction`: `"ingress"` or `"egress"`
    - `policy`: `"accept"` or `"deny"`
    - `protocol`: `"tcp"`, `"udp"`, `"icmp"`, or `"any"`
    - `port_range`: source port or range, e.g. `"22"` or `"8000-9000"`
    - `destination_port_range`: destination port or range
    - `source_type`: `"cidr"`, `"group"`, `"instance"`, or `"all"`
    - `source`: CIDR string (required when `source_type="cidr"`)
    - `destination_type`: `"cidr"`, `"group"`, `"instance"`, or `"all"`
    - `destination`: destination CIDR or reference
    - `ethertype`: `"IPv4"` or `"IPv6"`
    - `priority`: integer — lower value = higher priority
    - `enabled`: whether rule is active
- Returns: `SecurityGroupRule`
- Raises: common API exceptions

### `update_rule(security_group_id: int, rule_id: int, *, name=None, direction=None, policy=None, protocol=None, port_range=None, destination_port_range=None, source_type=None, source=None, destination_type=None, destination=None, ethertype=None, priority=None, enabled=None) -> SecurityGroupRule`

- Endpoint: `PUT /api/security-groups/{security_group_id}/rules/{rule_id}`
- Parameters: same as `create_rule`, all optional
- Returns: updated `SecurityGroupRule`
- Raises: common API exceptions

### `delete_rule(security_group_id: int, rule_id: int) -> bool`

- Endpoint: `DELETE /api/security-groups/{security_group_id}/rules/{rule_id}`
- Returns: `True` on success
- Raises: common API exceptions
