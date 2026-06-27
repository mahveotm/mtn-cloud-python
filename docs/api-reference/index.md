# API Reference

This section documents the public SDK surface in endpoint-first format.

## Sections

- [Client (`MTNCloud`)](./client.md)
- [Instances (`cloud.instances`)](./instances.md)
- [Instance Types (`cloud.instance_types`)](./instance-types.md)
- [Networks (`cloud.networks`)](./networks.md)
- [Clouds (`cloud.clouds`)](./clouds.md)
- [Groups (`cloud.groups`)](./groups.md)
- [Plans (`cloud.plans`)](./plans.md)
- [Storage Buckets (`cloud.storage_buckets`)](./storage-buckets.md)
- [Archive Buckets (`cloud.archive_buckets`)](./archive-buckets.md)
- [Security Groups (`cloud.security_groups`)](./security-groups.md)
- [Backups (`cloud.backups`)](./backups.md)
- [Virtual Images (`cloud.virtual_images`)](./virtual-images.md)

## Conventions

- Base URL: `https://console.cloud.mtn.ng` by default (configurable via `MTN_CLOUD_URL`).
- API prefix: the SDK automatically appends `/api`.
- Endpoint examples below are shown as relative API paths, e.g. `GET /api/instances`.
- All resource managers are accessed from a client instance:

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="...")
```

## Common Exceptions

All HTTP-backed methods may raise these exceptions based on API response or transport errors:

| Exception | When it is raised |
|---|---|
| `AuthenticationError` | `401` or missing/invalid credentials |
| `ForbiddenError` | `403` insufficient permission |
| `NotFoundError` | `404` resource not found |
| `ValidationError` | `400` invalid input/payload; carries `.errors` |
| `QuotaExceededError` | `402` quota or limit exceeded; carries `.quota_type`, `.current`, `.limit` |
| `ResourceConflictError` | `409` resource conflict or invalid state transition |
| `RateLimitError` | `429` too many requests; carries `.retry_after` |
| `ServerError` | `5xx` backend failure |
| `TimeoutError` | request timeout; carries `.timeout` |
| `MTNCloudError` | connection errors, unknown status codes, generic request failures |

Method-specific local exceptions (for example `FileNotFoundError`) are documented per method.

## Shared `list(...)` Query Arguments

Most resource managers implement a `list(...)` variant with these common query controls:

| Argument | API Query Key | Notes |
|---|---|---|
| `max_results` | `max` | Maximum returned rows |
| `offset` | `offset` | Pagination offset |
| `sort` | `sort` | Sort field |
| `direction` | `direction` | `asc` or `desc` |
| `phrase` | `phrase` | API-side search phrase |
| `**filters` | passthrough | Extra endpoint-specific filters |

## Shared Inherited Helpers

Every resource manager (`instances`, `networks`, `plans`, etc.) inherits:

### `resource.exists(resource_id: int) -> bool`

- Endpoint sequence:
    - `GET /api/<resource-path>/{resource_id}`
- Returns:
    - `True` if found
    - `False` only when `NotFoundError` occurs
- Raises:
    - Any non-`NotFoundError` common API exception

### `resource.paginate(page_size=100, start_offset=0, sort=None, direction=None, phrase=None, **filters) -> Iterator[list[Model]]`

- Behavior:
    - Repeatedly calls `list(...)` with `max_results=page_size`
    - Increments pagination offset until a partial page or empty page is returned
- Parameters:
    - `page_size`: number of items per page (must be `>= 1`)
    - `start_offset`: initial pagination offset (must be `>= 0`)
    - `sort`, `direction`, `phrase`, `**filters`: same semantics as `list(...)`
- Yields:
    - `list[Model]` per page
- Raises:
    - `ValueError` for invalid pagination arguments
    - common API exceptions from internal `list(...)` calls

### `resource.iter_all(page_size=100, start_offset=0, sort=None, direction=None, phrase=None, **filters) -> Iterator[Model]`

- Behavior:
    - Flattens items from `paginate(...)`
- Parameters:
    - Same as `paginate(...)`
- Yields:
    - Individual resource model instances
- Raises:
    - Same as `paginate(...)`


## References

- MTN Cloud Console: <https://console.cloud.mtn.ng>
- MTN Cloud Guide: <https://cloud.mtn.ng/documentation>
- Morpheus API Documentation (supplementary): <https://apidocs.morpheusdata.com/>
- SDK Source: <https://github.com/mahveotm/mtn-cloud-python>
