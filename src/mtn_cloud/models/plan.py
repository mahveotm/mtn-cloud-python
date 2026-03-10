"""
Service Plan Models
===================

Models for MTN Cloud service plans.
"""

from typing import Any, Optional
from pydantic import Field

from mtn_cloud.models.base import Resource


class ServicePlan(Resource):
    """
    MTN Cloud service plan.

    Service plans define the compute resources (CPU, memory, storage)
    available to instances.

    Example:
        ```python
        # List plans
        for plan in cloud.plans.list():
            print(f"{plan.name}: {plan.cores} cores, {plan.memory_gb}GB RAM")
        ```
    """

    # Plan details
    description: Optional[str] = Field(default=None)
    code: Optional[str] = Field(default=None)

    # Resources
    max_memory: Optional[int] = Field(
        default=None,
        alias="maxMemory",
        description="Maximum memory in bytes",
    )
    max_storage: Optional[int] = Field(
        default=None,
        alias="maxStorage",
        description="Maximum storage in bytes",
    )
    max_cores: Optional[int] = Field(
        default=None,
        alias="maxCores",
        description="Maximum CPU cores",
    )
    cores_per_socket: Optional[int] = Field(
        default=None,
        alias="coresPerSocket"
    )

    # Custom options
    custom_cores: bool = Field(default=False, alias="customCores")
    custom_max_storage: bool = Field(default=False, alias="customMaxStorage")
    custom_max_memory: bool = Field(default=False, alias="customMaxMemory")

    # Pricing
    price_sets: list[dict[str, Any]] = Field(
        default_factory=list,
        alias="priceSets"
    )

    # Status
    active: bool = Field(default=True)
    deleted: bool = Field(default=False)

    # Provisioning
    provision_type: Optional[dict[str, Any]] = Field(
        default=None,
        alias="provisionType"
    )

    # Sorting
    sort_order: Optional[int] = Field(default=None, alias="sortOrder")

    # Config
    config: Optional[dict[str, Any]] = Field(default=None)

    @property
    def memory_gb(self) -> Optional[float]:
        """Get memory in GB."""
        if self.max_memory:
            return self.max_memory / (1024 * 1024 * 1024)
        return None

    @property
    def storage_gb(self) -> Optional[float]:
        """Get storage in GB."""
        if self.max_storage:
            return self.max_storage / (1024 * 1024 * 1024)
        return None

    @property
    def cores(self) -> Optional[int]:
        """Get number of cores."""
        return self.max_cores

