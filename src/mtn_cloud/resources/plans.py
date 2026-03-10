"""
Plans Resource
==============

Resource manager for MTN Cloud service plans.
"""

from typing import Any

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.models.plan import ServicePlan
from mtn_cloud.resources.base import BaseResource


class PlansResource(BaseResource[ServicePlan]):
    """
    Manage MTN Cloud service plans.

    Service plans define compute resources for instances.

    Example:
        ```python
        # List plans
        plans = cloud.plans.list()

        # Get plan
        plan = cloud.plans.get(6923)

        # Find plan by cores/memory
        plan = cloud.plans.find(cores=2, memory_gb=4)
        ```
    """

    _path = "/service-plans"
    _model = ServicePlan
    _name = "service plan"
    _list_key = "servicePlans"
    _item_key = "servicePlan"

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        name: str | None = None,
        **filters: Any,
    ) -> list[ServicePlan]:
        """
        List service plans.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            sort: Field to sort by
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            name: Filter by name
            **filters: Additional filters

        Returns:
            List of service plans
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

    def get(self, plan_id: int) -> ServicePlan:
        """
        Get a service plan by ID.

        Args:
            plan_id: Service plan ID

        Returns:
            ServicePlan object

        Raises:
            NotFoundError: If plan not found
        """
        return super().get(plan_id)

    def get_by_name(self, name: str) -> ServicePlan:
        """
        Get a service plan by name.

        Args:
            name: Plan name

        Returns:
            ServicePlan object

        Raises:
            NotFoundError: If plan not found
        """
        plans = self.list(name=name, max_results=1)
        if not plans:
            raise NotFoundError(
                resource_type="ServicePlan",
                message=f"Service plan with name '{name}' not found",
            )
        return plans[0]

    def find(
        self,
        cores: int | None = None,
        memory_gb: float | None = None,
        storage_gb: float | None = None,
    ) -> ServicePlan | None:
        """
        Find a service plan matching the specified requirements.

        Args:
            cores: Minimum number of CPU cores
            memory_gb: Minimum memory in GB
            storage_gb: Minimum storage in GB

        Returns:
            Matching service plan or None
        """
        plans = self.list()

        for plan in plans:
            if cores and (plan.cores is None or plan.cores < cores):
                continue
            if memory_gb and (plan.memory_gb is None or plan.memory_gb < memory_gb):
                continue
            if storage_gb and (plan.storage_gb is None or plan.storage_gb < storage_gb):
                continue
            return plan

        return None
