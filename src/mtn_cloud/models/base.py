"""
Base Models
===========

Base classes for all MTN Cloud SDK models.
"""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel as PydanticBaseModel, ConfigDict, Field


class BaseModel(PydanticBaseModel):
    """
    Base model with common configuration.

    All MTN Cloud models inherit from this base class which provides:
    - Automatic camelCase to snake_case conversion
    - Extra field handling
    - JSON serialization configuration
    """

    model_config = ConfigDict(
        populate_by_name=True,  # Allow both camelCase and snake_case
        str_strip_whitespace=True,
        use_enum_values=True,
        extra="ignore",  # Ignore unknown fields from API
        from_attributes=True,  # Allow creating from ORM objects
    )


class Resource(BaseModel):
    """
    Base class for API resources with common fields.

    Most MTN Cloud resources have an ID and timestamps.
    """

    id: int = Field(..., description="Unique resource ID")
    name: Optional[str] = Field(default=None, description="Resource name")

    # Timestamps (optional as not all resources have these)
    date_created: Optional[datetime] = Field(
        default=None,
        alias="dateCreated",
        description="Creation timestamp",
    )
    last_updated: Optional[datetime] = Field(
        default=None,
        alias="lastUpdated",
        description="Last update timestamp",
    )

    def __str__(self) -> str:
        if self.name:
            return f"{self.__class__.__name__}(id={self.id}, name={self.name!r})"
        return f"{self.__class__.__name__}(id={self.id})"

    def __repr__(self) -> str:
        return str(self)


T = TypeVar("T", bound=Resource)


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated API response.

    Many list endpoints return paginated results with metadata.
    """

    items: list[T] = Field(default_factory=list, description="List of items")

    # Pagination metadata
    meta: Optional[dict[str, Any]] = Field(
        default=None,
        description="Response metadata",
    )

    # Pagination info (various field names used by API)
    offset: int = Field(default=0, description="Result offset")
    max: int = Field(default=25, description="Maximum results per page")
    size: Optional[int] = Field(default=None, description="Total number of results")
    total: Optional[int] = Field(default=None, description="Total number of results")

    @property
    def total_count(self) -> int:
        """Get total count of items."""
        return self.total or self.size or len(self.items)

    @property
    def has_more(self) -> bool:
        """Check if there are more pages."""
        return self.offset + len(self.items) < self.total_count

    def __iter__(self):
        """Iterate over items."""
        return iter(self.items)

    def __len__(self) -> int:
        """Return number of items in current page."""
        return len(self.items)


class APIResponse(BaseModel):
    """Generic API response wrapper."""

    success: bool = Field(default=True, description="Whether the request succeeded")
    message: Optional[str] = Field(default=None, description="Response message")
    errors: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Error details if request failed",
    )
    data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Response data",
    )

