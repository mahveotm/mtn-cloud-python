"""Base model primitives shared by all SDK resource models."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, field_validator


class BaseModel(PydanticBaseModel):
    """
    Base model with common configuration.

    All MTN Cloud models inherit from this base class which provides:
    - Automatic camelCase to snake_case conversion
    - Extra field handling
    - JSON serialization configuration
    """

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        extra="ignore",
        from_attributes=True,
    )

    @field_validator("labels", mode="before", check_fields=False)
    @classmethod
    def _coerce_null_labels(cls, value: Any) -> Any:
        """Treat a null ``labels`` field from the API as an empty list."""
        return [] if value is None else value


class Resource(BaseModel):
    """
    Base class for API resources with common fields.

    Most MTN Cloud resources have an ID and timestamps.
    """

    id: int = Field(..., description="Unique resource ID")
    name: str | None = Field(default=None, description="Resource name")

    date_created: datetime | None = Field(
        default=None,
        alias="dateCreated",
        description="Creation timestamp",
    )
    last_updated: datetime | None = Field(
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

    meta: dict[str, Any] | None = Field(
        default=None,
        description="Response metadata",
    )

    offset: int = Field(default=0, description="Result offset")
    max: int = Field(default=25, description="Maximum results per page")
    size: int | None = Field(default=None, description="Total number of results")
    total: int | None = Field(default=None, description="Total number of results")

    @property
    def total_count(self) -> int:
        """Get total count of items."""
        return self.total or self.size or len(self.items)

    @property
    def has_more(self) -> bool:
        """Check if there are more pages."""
        return self.offset + len(self.items) < self.total_count

    def __len__(self) -> int:
        """Return number of items in current page."""
        return len(self.items)

    def iter_items(self) -> Iterator[T]:
        """Iterate over items."""
        return iter(self.items)


class APIResponse(BaseModel):
    """Generic API response wrapper."""

    success: bool = Field(default=True, description="Whether the request succeeded")
    message: str | None = Field(default=None, description="Response message")
    errors: list[dict[str, Any]] | None = Field(
        default=None,
        description="Error details if request failed",
    )
    data: dict[str, Any] | None = Field(
        default=None,
        description="Response data",
    )
