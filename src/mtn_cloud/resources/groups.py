"""
Groups Resource
===============

Resource manager for MTN Cloud groups (sites).
"""

from typing import Any, Optional

from mtn_cloud.resources.base import BaseResource
from mtn_cloud.models.group import Group
from mtn_cloud.exceptions import NotFoundError


class GroupsResource(BaseResource[Group]):
    """
    Manage MTN Cloud groups (sites).

    Groups are organizational units for resources.

    Example:
        ```python
        # List groups
        groups = cloud.groups.list()

        # Get group
        group = cloud.groups.get(1)

        # Get group by name
        group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
        ```
    """

    _path = "/groups"
    _model = Group
    _name = "group"
    _list_key = "groups"
    _item_key = "group"

    def list(
        self,
        max_results: Optional[int] = None,
        offset: int = 0,
        sort: Optional[str] = None,
        direction: Optional[str] = None,
        phrase: Optional[str] = None,
        name: Optional[str] = None,
        **filters: Any,
    ) -> list[Group]:
        """
        List groups.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            sort: Field to sort by
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            name: Filter by name
            **filters: Additional filters

        Returns:
            List of groups
        """
        if name:
            filters["name"] = name

        return super().list(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        )

    def get(self, group_id: int) -> Group:
        """
        Get a group by ID.

        Args:
            group_id: Group ID

        Returns:
            Group object

        Raises:
            NotFoundError: If group not found
        """
        return super().get(group_id)

    def get_by_name(self, name: str) -> Group:
        """
        Get a group by name.

        Args:
            name: Group name

        Returns:
            Group object

        Raises:
            NotFoundError: If group not found
        """
        groups = self.list(name=name, max_results=1)
        if not groups:
            raise NotFoundError(
                resource_type="Group",
                message=f"Group with name '{name}' not found",
            )
        return groups[0]

