"""
Instance Type Models
====================

Models for MTN Cloud instance types.
"""

from __future__ import annotations

from typing import Any, List

from pydantic import Field

from mtn_cloud.models.base import BaseModel, Resource


class InstanceTypeLayout(BaseModel):
    """Layout available for an instance type."""

    id: int
    name: str
    provision_type_code: str = Field(alias="provisionTypeCode", default="openstack")

    def __str__(self) -> str:
        """Return string representation with id and name."""
        return f"InstanceTypeLayout(id={self.id}, name='{self.name}')"

    def __repr__(self) -> str:
        """Return detailed representation."""
        return self.__str__()


class InstanceType(Resource):
    """
    MTN Cloud instance type.

    Represents an available instance type (OS or application template)
    that can be provisioned on MTN Cloud.

    Example:
        ```python
        # List available instance types
        instance_types = cloud.instance_types.list()
        for it in instance_types:
            print(f"{it.code}: {it.name} (Layout ID: {it.default_layout_id})")

        # Get instance type by code
        centos = cloud.instance_types.get_by_code("MTN-CS10")
        print(f"Layout ID: {centos.default_layout_id}")

        # Access all layouts
        for layout in centos.layouts:
            print(f"  Layout: {layout.id} - {layout.name}")
        ```
    """

    # Basic info
    code: str = Field(..., description="Instance type code (e.g., 'MTN-CS10')")
    description: str | None = Field(default=None, description="Instance type description")

    # Category
    category: str | None = Field(
        default=None, description="Category (e.g., 'os', 'sql', 'web', 'apps')"
    )

    # Labels
    labels: List[str] = Field(default_factory=list, description="Labels/tags")

    # Status
    active: bool = Field(default=True, description="Whether instance type is active")
    featured: bool = Field(default=False, description="Whether instance type is featured")
    visibility: str = Field(default="public", description="Visibility (public/private)")

    # Provisioning
    provision_type_code: str | None = Field(alias="provisionTypeCode", default="openstack")
    environment_prefix: str | None = Field(alias="environmentPrefix", default=None)

    # Versions
    versions: List[str] = Field(default_factory=list, description="Available versions")

    # Layouts
    instance_type_layouts: List[InstanceTypeLayout] = Field(
        alias="instanceTypeLayouts",
        default_factory=list,
        description="Available layouts for this instance type",
    )

    # Account
    account: dict[str, Any] | None = Field(default=None, description="Account info")

    def __str__(self) -> str:
        """Return string representation with id, name, code, and default layout id."""
        return f"InstanceType(id={self.id}, name='{self.name}', code='{self.code}', layout_id={self.default_layout_id})"

    def __repr__(self) -> str:
        """Return detailed representation."""
        return self.__str__()

    @property
    def layouts(self) -> List[InstanceTypeLayout]:
        """Get all available layouts for this instance type."""
        return self.instance_type_layouts

    @property
    def default_layout_id(self) -> int | None:
        """Get the default (first) layout ID for this instance type."""
        if self.instance_type_layouts:
            return self.instance_type_layouts[0].id
        return None

    @property
    def default_layout(self) -> InstanceTypeLayout | None:
        """Get the default (first) layout for this instance type."""
        if self.instance_type_layouts:
            return self.instance_type_layouts[0]
        return None

    def get_layout_by_name(self, name: str) -> InstanceTypeLayout | None:
        """
        Get a layout by name.

        Args:
            name: Layout name to search for

        Returns:
            InstanceTypeLayout if found, None otherwise
        """
        for layout in self.instance_type_layouts:
            if layout.name == name:
                return layout
        return None

    def get_layout_by_id(self, layout_id: int) -> InstanceTypeLayout | None:
        """
        Get a layout by ID.

        Args:
            layout_id: Layout ID to search for

        Returns:
            InstanceTypeLayout if found, None otherwise
        """
        for layout in self.instance_type_layouts:
            if layout.id == layout_id:
                return layout
        return None
