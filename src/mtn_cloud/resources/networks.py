"""
Networks Resource
=================

Resource manager for MTN Cloud networks.
"""

from __future__ import annotations

from typing import Any, List

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.models.network import Network
from mtn_cloud.resources.base import BaseResource


class NetworksResource(BaseResource[Network]):
    """
    Manage MTN Cloud networks.

    Example:
        ```python
        # List networks
        networks = cloud.networks.list()

        # List networks for a specific cloud
        networks = cloud.networks.list(cloud_id=1)

        # Get network
        network = cloud.networks.get(123)
        ```
    """

    _path = "/networks"
    _model = Network
    _name = "network"
    _list_key = "networks"
    _item_key = "network"

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        name: str | None = None,
        cloud_id: int | None = None,
        **filters: Any,
    ) -> List[Network]:
        """
        List networks.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            sort: Field to sort by
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            name: Filter by name
            cloud_id: Filter by cloud/zone ID
            **filters: Additional filters

        Returns:
            List of networks
        """
        if name:
            filters["name"] = name
        if cloud_id:
            filters["zoneId"] = cloud_id

        return super().list(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        )

    def get(self, network_id: int) -> Network:
        """
        Get a network by ID.

        Args:
            network_id: Network ID

        Returns:
            Network object

        Raises:
            NotFoundError: If network not found
        """
        return super().get(network_id)

    def get_by_name(self, name: str, cloud_id: int | None = None) -> Network:
        """
        Get a network by name.

        Args:
            name: Network name
            cloud_id: Optional cloud ID to narrow search

        Returns:
            Network object

        Raises:
            NotFoundError: If network not found
        """
        networks = self.list(name=name, cloud_id=cloud_id, max_results=1)
        if not networks:
            raise NotFoundError(
                resource_type="Network",
                message=f"Network with name '{name}' not found",
            )
        return networks[0]

    def list_by_cloud(self, cloud_id: int) -> List[Network]:
        """
        List all networks in a specific cloud.

        Args:
            cloud_id: Cloud/zone ID

        Returns:
            List of networks in the cloud
        """
        return self.list(cloud_id=cloud_id)
