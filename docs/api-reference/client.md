# Client: `MTNCloud`

### `MTNCloud(token=None, username=None, password=None, url=None, timeout=None, verify_ssl=None, config=None)`

Creates an SDK client and lazy-loads resource managers.

- Endpoint: None (constructor does not make API calls)
- Parameters:
    - `token`: API bearer token (recommended)
    - `username`, `password`: OAuth password-grant alternative
    - `url`: MTN Cloud base console URL, no `/api` needed
    - `timeout`: request timeout in seconds
    - `verify_ssl`: enable/disable TLS certificate validation; when omitted,
      `MTN_CLOUD_VERIFY_SSL` or the configuration default is used
    - `config`: explicit `MTNCloudConfig` object (overrides other args)
- Returns: `MTNCloud`
- Raises:
    - `pydantic.ValidationError` if config values violate `MTNCloudConfig` constraints

Tokens and passwords are stored as masked secret values. Use
`config.get_token_value()` or `config.get_password_value()` only when an explicit
integration needs the underlying value; normal SDK usage never needs to reveal
them.

The transport:

- preserves the `mtn-cloud-python/<version>` user-agent identity required by the
  MTN API edge;
- recursively redacts secrets from debug logs and raised error response payloads;
- retries 429 and transient 5xx responses only for `GET`, `HEAD`, and `OPTIONS`;
- does not automatically status-retry `POST`, `PUT`, `PATCH`, or `DELETE` calls;
- handles both delta-seconds and HTTP-date `Retry-After` headers.

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
