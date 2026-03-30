# Client: `MTNCloud`

### `MTNCloud(token=None, username=None, password=None, url=None, timeout=None, verify_ssl=True, config=None)`

Creates an SDK client and lazy-loads resource managers.

- Endpoint: None (constructor does not make API calls)
- Parameters:
    - `token`: API bearer token (recommended)
    - `username`, `password`: OAuth password-grant alternative
    - `url`: MTN Cloud base console URL, no `/api` needed
    - `timeout`: request timeout in seconds
    - `verify_ssl`: enable/disable TLS certificate validation
    - `config`: explicit `MTNCloudConfig` object (overrides other args)
- Returns: `MTNCloud`
- Raises:
    - `pydantic.ValidationError` if config values violate `MTNCloudConfig` constraints

### `whoami() -> User`

- Endpoint: `GET /api/whoami`
- Parameters: none
- Returns: `User`
- Raises: common API exceptions

### `ping() -> bool`

Connectivity/auth convenience check.

- Endpoint sequence:
    - `GET /api/whoami` (via `whoami()`)
- Parameters: none
- Returns:
    - `True` if request succeeds
    - `False` for any exception
- Raises: none (exceptions are swallowed and converted to `False`)

### `close() -> None`

- Endpoint: None
- Parameters: none
- Returns: `None`
- Raises: none

