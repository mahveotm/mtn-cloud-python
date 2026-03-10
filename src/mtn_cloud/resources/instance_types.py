"""
Instance Types Resource
=======================

Resource manager for MTN Cloud instance types.
"""

from __future__ import annotations

from typing import Any, List

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.models.instance_type import InstanceType
from mtn_cloud.resources.base import BaseResource


class InstanceTypesResource(BaseResource[InstanceType]):
    """
    Manage MTN Cloud instance types.

    Instance types define the OS or application templates available
    for provisioning on MTN Cloud.

    Example:
        ```python
        # List all instance types
        instance_types = cloud.instance_types.list()

        # List by category
        os_types = cloud.instance_types.list(category="os")
        db_types = cloud.instance_types.list(category="sql")

        # Get instance type by code
        centos = cloud.instance_types.get_by_code("MTN-CS10")
        print(f"Name: {centos.name}")
        print(f"Layout ID: {centos.default_layout_id}")
        ```
    """

    _path = "/instance-types"
    _model = InstanceType
    _name = "instanceType"
    _list_key = "instanceTypes"
    _item_key = "instanceType"

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = "name",
        direction: str | None = "asc",
        phrase: str | None = None,
        name: str | None = None,
        code: str | None = None,
        category: str | None = None,
        featured: bool | None = None,
        **filters: Any,
    ) -> list[InstanceType]:
        """
        List instance types.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            sort: Field to sort by (default: 'name')
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            name: Filter by name
            code: Filter by code
            category: Filter by category (e.g., 'os', 'sql', 'web', 'apps', 'network')
            featured: Filter by featured status
            **filters: Additional filters

        Returns:
            List of instance types
        """
        if name:
            filters["name"] = name
        if code:
            filters["code"] = code
        if category:
            filters["category"] = category
        if featured is not None:
            filters["featured"] = featured

        return super().list(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        )

    def get(self, instance_type_id: int) -> InstanceType:
        """
        Get an instance type by ID.

        Args:
            instance_type_id: Instance type ID

        Returns:
            InstanceType object

        Raises:
            NotFoundError: If instance type not found
        """
        return super().get(instance_type_id)

    def get_by_code(self, code: str) -> InstanceType:
        """
        Get an instance type by code.

        Args:
            code: Instance type code (e.g., 'MTN-CS10')

        Returns:
            InstanceType object

        Raises:
            NotFoundError: If instance type not found

        Example:
            ```python
            centos = cloud.instance_types.get_by_code("MTN-CS10")
            ubuntu = cloud.instance_types.get_by_code("MTN-U24.04LTS")
            ```
        """
        instance_types = self.list(code=code, max_results=1)
        if not instance_types:
            raise NotFoundError(
                resource_type="InstanceType",
                message=f"Instance type with code '{code}' not found",
            )
        return instance_types[0]

    def get_by_name(self, name: str) -> InstanceType:
        """
        Get an instance type by name.

        Args:
            name: Instance type name

        Returns:
            InstanceType object

        Raises:
            NotFoundError: If instance type not found
        """
        instance_types = self.list(name=name, max_results=1)
        if not instance_types:
            raise NotFoundError(
                resource_type="InstanceType",
                message=f"Instance type with name '{name}' not found",
            )
        return instance_types[0]

    def list_os(self) -> list[InstanceType]:
        """
        List operating system instance types.

        Returns:
            List of OS instance types
        """
        return self.list(category="os")

    def list_databases(self) -> list[InstanceType]:
        """
        List database instance types.

        Returns:
            List of database instance types
        """
        return self.list(category="sql")

    def list_web(self) -> list[InstanceType]:
        """
        List web server instance types.

        Returns:
            List of web server instance types
        """
        return self.list(category="web")

    def list_apps(self) -> list[InstanceType]:
        """
        List application instance types.

        Returns:
            List of application instance types
        """
        return self.list(category="apps")

