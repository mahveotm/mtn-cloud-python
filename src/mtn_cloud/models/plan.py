"""Models for MTN Cloud service plans."""

from typing import Any

from pydantic import Field

from mtn_cloud.models.base import Resource


class ServicePlan(Resource):
    """
    MTN Cloud service plan.

    Service plans define the compute resources (CPU, memory, storage)
    available to instances.

    Example:
        # List plans
        for plan in cloud.plans.list():
            print(f"{plan.name}: {plan.cores} cores, {plan.memory_gb}GB RAM")
    """

    description: str | None = Field(default=None)
    code: str | None = Field(default=None)

    max_memory: int | None = Field(
        default=None,
        alias="maxMemory",
        description="Maximum memory in bytes",
    )
    max_storage: int | None = Field(
        default=None,
        alias="maxStorage",
        description="Maximum storage in bytes",
    )
    max_cores: int | None = Field(
        default=None,
        alias="maxCores",
        description="Maximum CPU cores",
    )
    cores_per_socket: int | None = Field(default=None, alias="coresPerSocket")

    custom_cores: bool = Field(default=False, alias="customCores")
    custom_max_storage: bool = Field(default=False, alias="customMaxStorage")
    custom_max_memory: bool = Field(default=False, alias="customMaxMemory")

    price_sets: list[dict[str, Any]] = Field(default_factory=list, alias="priceSets")

    active: bool = Field(default=True)
    deleted: bool = Field(default=False)

    provision_type: dict[str, Any] | None = Field(default=None, alias="provisionType")

    sort_order: int | None = Field(default=None, alias="sortOrder")

    config: dict[str, Any] | None = Field(default=None)

    @property
    def memory_gb(self) -> float | None:
        """Get memory in GB."""
        if self.max_memory:
            return self.max_memory / (1024 * 1024 * 1024)
        return None

    @property
    def storage_gb(self) -> float | None:
        """Get storage in GB."""
        if self.max_storage:
            return self.max_storage / (1024 * 1024 * 1024)
        return None

    @property
    def cores(self) -> int | None:
        """Get number of cores."""
        return self.max_cores
