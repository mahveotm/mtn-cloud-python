"""Base primitives shared by all resource managers."""

from __future__ import annotations

from builtins import list as builtin_list
from collections.abc import Iterator
from typing import Any, Generic, TypeVar

from mtn_cloud.http import HTTPClient
from mtn_cloud.models.base import Resource

T = TypeVar("T", bound=Resource)


class BaseResource(Generic[T]):
    """
    Base class for resource managers.

    Provides common CRUD operations for API resources.
    Subclasses should define:
    - `_path`: API path for the resource
    - `_model`: Pydantic model class for the resource
    - `_name`: Human-readable name (for error messages)
    - `_list_key`: Key in API response containing the list of items
    - `_item_key`: Key in API response containing a single item
    """

    _path: str = ""
    _model: type[T]
    _name: str = "resource"
    _list_key: str = "items"
    _item_key: str = "item"

    def __init__(self, http: HTTPClient) -> None:
        """
        Initialize the resource manager.

        Args:
            http: HTTP client for making API requests
        """
        self._http = http

    def _parse_item(self, data: dict[str, Any]) -> T:
        """
        Parse a single item from API response.

        Args:
            data: Raw API response data

        Returns:
            Parsed model instance
        """
        # Handle wrapped responses
        if self._item_key in data:
            data = data[self._item_key]
        return self._model.model_validate(data)

    def _parse_list(self, data: dict[str, Any]) -> builtin_list[T]:
        """
        Parse a list of items from API response.

        Args:
            data: Raw API response data

        Returns:
            List of parsed model instances
        """
        items = data.get(self._list_key, [])
        return [self._model.model_validate(item) for item in items]

    def _build_list_params(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        **filters: Any,
    ) -> dict[str, Any]:
        """Build query parameters for list-style operations."""
        params: dict[str, Any] = {}

        if max_results is not None:
            params["max"] = max_results
        if offset > 0:
            params["offset"] = offset
        if sort:
            params["sort"] = sort
        if direction:
            params["direction"] = direction
        if phrase:
            params["phrase"] = phrase

        params.update(filters)
        return params

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        **filters: Any,
    ) -> builtin_list[T]:
        """
        List resources.

        Args:
            max_results: Maximum number of results to return
            offset: Offset for pagination
            sort: Field to sort by
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            **filters: Additional filter parameters

        Returns:
            List of resources
        """
        params = self._build_list_params(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        )
        response = self._http.get(self._path, params=params)
        return self._parse_list(response)

    def paginate(
        self,
        page_size: int = 100,
        start_offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        **filters: Any,
    ) -> Iterator[builtin_list[T]]:
        """
        Iterate through resources page by page.

        This helper repeatedly calls `list(...)` with `max_results=page_size`,
        incrementing offset until the API returns a partial page or no items.

        Args:
            page_size: Number of items per page (must be >= 1)
            start_offset: Initial pagination offset (must be >= 0)
            sort: Field to sort by
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            **filters: Additional filters (resource-specific)

        Yields:
            Lists of resource model instances for each page

        Raises:
            ValueError: If `page_size` is less than 1 or `start_offset` is negative
        """
        if page_size < 1:
            raise ValueError("page_size must be >= 1")
        if start_offset < 0:
            raise ValueError("start_offset must be >= 0")

        offset = start_offset
        while True:
            page = self.list(
                max_results=page_size,
                offset=offset,
                sort=sort,
                direction=direction,
                phrase=phrase,
                **filters,
            )
            if not page:
                break

            yield page

            if len(page) < page_size:
                break

            offset += len(page)

    def iter_all(
        self,
        page_size: int = 100,
        start_offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        **filters: Any,
    ) -> Iterator[T]:
        """
        Iterate through all resources item-by-item.

        This helper flattens pages produced by `paginate(...)`.

        Args:
            page_size: Number of items per page (must be >= 1)
            start_offset: Initial pagination offset (must be >= 0)
            sort: Field to sort by
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            **filters: Additional filters (resource-specific)

        Yields:
            Individual resource model instances
        """
        for page in self.paginate(
            page_size=page_size,
            start_offset=start_offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        ):
            yield from page

    def get(self, resource_id: int) -> T:
        """
        Get a single resource by ID.

        Args:
            resource_id: Resource ID

        Returns:
            Resource instance
        """
        path = f"{self._path}/{resource_id}"
        response = self._http.get(path)
        return self._parse_item(response)

    def _create(self, payload: dict[str, Any]) -> T:
        """
        Create a new resource.

        Args:
            payload: Request payload

        Returns:
            Created resource
        """
        response = self._http.post(self._path, json=payload)
        return self._parse_item(response)

    def _update(self, resource_id: int, payload: dict[str, Any]) -> T:
        """
        Update a resource.

        Args:
            resource_id: Resource ID
            payload: Update payload

        Returns:
            Updated resource
        """
        path = f"{self._path}/{resource_id}"
        response = self._http.put(path, json=payload)
        return self._parse_item(response)

    def _delete(
        self,
        resource_id: int,
        params: dict[str, Any] | None = None,
    ) -> bool:
        """
        Delete a resource.

        Args:
            resource_id: Resource ID
            params: Additional parameters

        Returns:
            True if deleted successfully
        """
        path = f"{self._path}/{resource_id}"
        self._http.delete(path, params=params)
        return True

    def exists(self, resource_id: int) -> bool:
        """
        Check if a resource exists.

        Args:
            resource_id: Resource ID

        Returns:
            True if resource exists
        """
        from mtn_cloud.exceptions import NotFoundError

        try:
            self.get(resource_id)
            return True
        except NotFoundError:
            return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
