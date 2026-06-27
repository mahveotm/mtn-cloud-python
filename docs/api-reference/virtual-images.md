# Resource: `cloud.virtual_images` (`VirtualImagesResource`)

### `list(max_results=None, offset=0, phrase=None, name=None, image_type=None, is_public=None, **filters) -> list[VirtualImage]`

- Endpoint: `GET /api/virtual-images`
- Parameters:
    - Shared list args (see [API Reference](./index.md#shared-list-query-arguments))
    - `name`: filter by name (exact)
    - `image_type`: filter by image type string (e.g. `"vmware"`, `"qcow2"`)
    - `is_public`: `True` maps to query `filterType=public`; `False` maps to `filterType=private`
- Returns: `list[VirtualImage]`
- Raises: common API exceptions

### `get(virtual_image_id: int) -> VirtualImage`

- Endpoint: `GET /api/virtual-images/{virtual_image_id}`
- Returns: `VirtualImage`
- Raises: common API exceptions

### `get_by_name(name: str) -> VirtualImage`

- Endpoint sequence:
    - `GET /api/virtual-images?phrase=<name>&max=25`
    - Linear scan of results for exact name match
- Parameters:
    - `name`: exact image name
- Returns: `VirtualImage`
- Raises:
    - common API exceptions
    - `NotFoundError` when no image with that exact name is found

### `delete(virtual_image_id: int) -> bool`

- Endpoint: `DELETE /api/virtual-images/{virtual_image_id}`
- Only custom (user-uploaded) images can be deleted; platform-provided images will return a 403
- Returns: `True` on success
- Raises: common API exceptions
