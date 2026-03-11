"""
Clouds Resource
===============

Resource manager for MTN Cloud clouds (zones).
"""

from __future__ import annotations

from typing import Any, List

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.models.cloud import Cloud
from mtn_cloud.resources.base import BaseResource


class CloudsResource(BaseResource[Cloud]):
    """
    Manage MTN Cloud clouds (zones).

    Clouds represent infrastructure endpoints where resources can be deployed.

    Example:
        ```python
        # List clouds
        clouds = cloud.clouds.list()

        # Get cloud
        c = cloud.clouds.get(1)

        # Get cloud by name
        c = cloud.clouds.get_by_name("MTNNG_CLOUD_AZ_1")
        ```
    """

    _path = "/zones"
    _model = Cloud
    _name = "cloud"
    _list_key = "zones"
    _item_key = "zone"

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        name: str | None = None,
        group_id: int | None = None,
        type_code: str | None = None,
        **filters: Any,
    ) -> List[Cloud]:
        """
        List clouds.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            sort: Field to sort by
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            name: Filter by name
            group_id: Filter by group ID
            type_code: Cloud type code filter (e.g. 'openstack')
            **filters: Additional filters

        Returns:
            List of clouds
        """
        if name:
            filters["name"] = name
        if group_id:
            filters["groupId"] = group_id
        if type_code:
            filters["type"] = type_code

        return super().list(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        )

    def list_openstack(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        name: str | None = None,
        group_id: int | None = None,
        **filters: Any,
    ) -> List[Cloud]:
        """
        List OpenStack clouds only.
        """
        return self.list(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            name=name,
            group_id=group_id,
            type_code="openstack",
            **filters,
        )

    def get(self, cloud_id: int) -> Cloud:
        """
        Get a cloud by ID.

        Args:
            cloud_id: Cloud ID

        Returns:
            Cloud object

        Raises:
            NotFoundError: If cloud not found
        """
        return super().get(cloud_id)

    def get_by_name(self, name: str) -> Cloud:
        """
        Get a cloud by name.

        Args:
            name: Cloud name

        Returns:
            Cloud object

        Raises:
            NotFoundError: If cloud not found
        """
        clouds = self.list(name=name, max_results=1)
        if not clouds:
            raise NotFoundError(
                resource_type="Cloud",
                message=f"Cloud with name '{name}' not found",
            )
        return clouds[0]

    def list_by_group(self, group_id: int) -> List[Cloud]:
        """
        List all clouds in a specific group.

        Args:
            group_id: Group ID

        Returns:
            List of clouds in the group
        """
        return self.list(group_id=group_id)
