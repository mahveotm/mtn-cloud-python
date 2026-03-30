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
| `ValidationError` | `400` invalid input/payload |
| `RateLimitError` | `429` too many requests |
| `ServerError` | `5xx` backend failure |
| `TimeoutError` | request timeout |
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

## Shared Inherited Helper

Every resource manager (`instances`, `networks`, `plans`, etc.) inherits:

### `resource.exists(resource_id: int) -> bool`

- Endpoint sequence:
    - `GET /api/<resource-path>/{resource_id}`
- Returns:
    - `True` if found
    - `False` only when `NotFoundError` occurs
- Raises:
    - Any non-`NotFoundError` common API exception


## References

- MTN Cloud Console: <https://console.cloud.mtn.ng>
- MTN Cloud Guide: <https://cloud.mtn.ng/documentation>
- Morpheus API Documentation (supplementary): <https://apidocs.morpheusdata.com/>
- SDK Source: <https://github.com/mahveotm/mtn-cloud-python>
