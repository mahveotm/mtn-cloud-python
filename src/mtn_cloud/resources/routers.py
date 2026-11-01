"""Resource manager for MTN Cloud routers."""

from __future__ import annotations

import time
from typing import Any

from mtn_cloud.exceptions import MTNCloudError, NotFoundError, TimeoutError
from mtn_cloud.models.router import ExternalNetwork, Router, RouterCreate
from mtn_cloud.resources.base import BaseResource
from mtn_cloud.resources.groups import GroupsResource
from mtn_cloud.resources.instances import InstancesResource


class RoutersResource(BaseResource[Router]):
    """Inspect routers and create/delete MTN neutronRouter resources."""

    _path = "/networks/routers"
    _model = Router
    _name = "router"
    _list_key = "networkRouters"
    _item_key = "networkRouter"

    def _type_id(self) -> int:
        matches: list[dict[str, Any]] = []
        offset = 0
        while True:
            response = self._http.get(
                "/network-router-types", params={"max": 100, "offset": offset}
            )
            page = response.get("networkRouterTypes", [])
            matches.extend(item for item in page if item.get("code") == "neutronRouter")
            if len(page) < 100:
                break
            offset += len(page)
        if len(matches) != 1:
            raise ValueError("Expected exactly one available MTN neutronRouter type.")
        type_id = int(matches[0]["id"])
        detail = self._http.get(f"/network-router-types/{type_id}")["networkRouterType"]
        if (
            detail.get("code") != "neutronRouter"
            or not detail.get("creatable")
            or detail.get("hasNetworkServer")
        ):
            raise ValueError("The MTN neutronRouter type is not available for creation.")
        return type_id

    def _external_network_scope(
        self, group: str | int, resource_pool: str | int, cloud_id: int | None
    ) -> tuple[int, int, str]:
        groups = GroupsResource(self._http)
        if isinstance(group, int) and not isinstance(group, bool) and group > 0:
            selected = groups.get(group)
        elif isinstance(group, str) and group.strip():
            matches = [g for g in groups.iter_all(name=group) if g.name == group]
            if not matches:
                raise NotFoundError(resource_type="Group", resource_id=group)
            if len(matches) > 1:
                raise ValueError(f"Group name {group!r} is ambiguous; pass its numeric ID.")
            selected = matches[0]
        else:
            raise ValueError("group must be a nonempty name or positive numeric ID.")
        if cloud_id is None:
            if len(selected.cloud_ids) != 1:
                raise ValueError(
                    f"Group {selected.name!r} has {len(selected.cloud_ids)} clouds; set cloud_id explicitly."
                )
            cloud_id = selected.cloud_ids[0]
        if type(cloud_id) is not int or cloud_id <= 0 or cloud_id not in selected.cloud_ids:
            raise ValueError(f"Cloud {cloud_id!r} is not attached to group {selected.name!r}.")
        if isinstance(resource_pool, bool) or not isinstance(resource_pool, str | int):
            raise ValueError("resource_pool must be a name, code, or positive numeric ID.")
        pools = InstancesResource(self._http).list_resource_pools(
            cloud_id=cloud_id, group_id=selected.id
        )
        matches_pool = [
            p
            for p in pools
            if (isinstance(resource_pool, int) and p.id == resource_pool)
            or (isinstance(resource_pool, str) and resource_pool in (p.name, p.code))
        ]
        if not matches_pool:
            raise NotFoundError(
                resource_type="ResourcePool",
                resource_id=resource_pool,
                message=f"Resource pool {resource_pool!r} is not available in group {selected.name!r}, cloud {cloud_id}.",
            )
        if len(matches_pool) > 1:
            raise ValueError(
                f"Resource pool {resource_pool!r} is ambiguous; use its code or numeric ID."
            )
        if not matches_pool[0].code:
            raise ValueError("Selected resource pool has no API option code.")
        return selected.id, cloud_id, matches_pool[0].code

    def list_external_networks(
        self, *, group: str | int, resource_pool: str | int, cloud_id: int | None = None
    ) -> list[ExternalNetwork]:
        """List router gateways scoped to a group, cloud, and resource pool.

        group accepts a name or numeric ID; resource_pool accepts a name, code,
        or numeric ID. Infer the cloud only when the group has exactly one.
        Returned IDs are Morpheus option values, not OpenStack UUIDs. These
        networks may be unavailable through the ordinary networks endpoint.
        """
        group_id, zone_id, pool_code = self._external_network_scope(group, resource_pool, cloud_id)
        response = self._http.get(
            "/options/openstackExternalNetworks",
            params={
                "router.zone.id": zone_id,
                "router.site.id": group_id,
                "router.poolId": pool_code,
                "routerType.id": self._type_id(),
            },
        )
        if response.get("success") is False:
            raise MTNCloudError("External-network discovery failed.", response=response)
        if not isinstance(response.get("data"), list):
            raise MTNCloudError("External-network response is missing its options list.")
        return [ExternalNetwork.model_validate(item) for item in response["data"]]

    def get_external_network(
        self,
        name: str,
        *,
        group: str | int,
        resource_pool: str | int,
        cloud_id: int | None = None,
    ) -> ExternalNetwork:
        """Resolve one exact gateway name; reject missing or ambiguous matches."""
        if not name.strip():
            raise ValueError("External network name must not be empty.")
        networks = self.list_external_networks(
            group=group, resource_pool=resource_pool, cloud_id=cloud_id
        )
        matches = [network for network in networks if network.name == name]
        if len(matches) > 1:
            raise ValueError(
                f"External network {name!r} is ambiguous; list the options and select an ID explicitly."
            )
        if not matches:
            available = ", ".join(network.name for network in networks)
            raise NotFoundError(
                resource_type="ExternalNetwork",
                resource_id=name,
                message=f"External network {name!r} is unavailable in the selected scope. Available names: {available}.",
            )
        return matches[0]

    def create(
        self,
        name: str,
        *,
        group_id: int,
        cloud_id: int,
        resource_pool_id: int,
        internal_subnet_ids: list[int],
        external_network_id: int | None = None,
        enabled: bool = True,
    ) -> Router:
        """Submit an MTN router and fetch its initial state.

        Use numeric Morpheus IDs, including the resource pool's numeric ID.
        Internal subnets must belong to that pool. Call wait_until_ready() to
        confirm provisioning; successful submission alone does not mean ready.
        Errors after creation include the router ID in response["router_id"].
        """
        request = RouterCreate(
            name=name,
            group_id=group_id,
            cloud_id=cloud_id,
            resource_pool_id=resource_pool_id,
            internal_subnet_ids=internal_subnet_ids,
            external_network_id=external_network_id,
            enabled=enabled,
        )
        response = self._http.post(self._path, json=request.to_api_payload(self._type_id()))
        router_id = response.get("id")
        if response.get("success") is not True or type(router_id) is not int or router_id <= 0:
            raise MTNCloudError(
                "Router creation did not return success and a valid ID.",
                response=response,
            )
        try:
            return self.get(router_id)
        except Exception as exc:
            raise MTNCloudError(
                f"Router {router_id} was submitted but could not be read; inspect or delete it by ID.",
                response={"router_id": router_id},
            ) from exc

    def delete(self, router_id: int) -> bool:
        """Submit deletion of an MTN router; an already absent router is success.

        Call wait_until_deleted() to confirm removal. Other router types cannot
        be deleted through this manager.
        """
        try:
            router = self.get(router_id)
        except NotFoundError:
            return True
        self._require_mtn(router)
        try:
            return self._delete(router_id)
        except NotFoundError:
            return True

    @staticmethod
    def _require_mtn(router: Router) -> None:
        if router.type is None or router.type.code != "neutronRouter":
            raise ValueError(f"Router {router.id} is not an MTN neutronRouter.")

    @staticmethod
    def _deadline(timeout: float, poll_interval: float) -> float:
        if timeout <= 0 or poll_interval <= 0:
            raise ValueError("timeout and poll_interval must be positive.")
        return time.monotonic() + timeout

    def wait_until_ready(
        self, router_id: int, timeout: float = 300, poll_interval: float = 5
    ) -> Router:
        """Wait for ok/available/active; raise on provisioning failure or timeout."""
        deadline = self._deadline(timeout, poll_interval)
        while True:
            router = self.get(router_id)
            self._require_mtn(router)
            status = (router.status or "").lower()
            if status in {"ok", "available", "active"}:
                return router
            if status in {"failed", "error"}:
                raise MTNCloudError(
                    f"Router {router_id} provisioning failed: {status}.",
                    response={"router_id": router_id, "status": status},
                )
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"Router {router_id} did not become ready (status: {status}).",
                    timeout=timeout,
                    response={"router_id": router_id, "status": status},
                )
            time.sleep(min(poll_interval, remaining))

    def wait_until_deleted(
        self, router_id: int, timeout: float = 300, poll_interval: float = 5
    ) -> bool:
        """Wait until the router endpoint returns 404; other API errors propagate."""
        deadline = self._deadline(timeout, poll_interval)
        while True:
            try:
                self.get(router_id)
            except NotFoundError:
                return True
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"Router {router_id} was not deleted.",
                    timeout=timeout,
                    response={"router_id": router_id},
                )
            time.sleep(min(poll_interval, remaining))
