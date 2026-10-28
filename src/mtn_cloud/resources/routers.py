"""Resource manager for MTN Cloud routers."""

from __future__ import annotations

import time
from typing import Any

from mtn_cloud.exceptions import MTNCloudError, NotFoundError, TimeoutError
from mtn_cloud.models.router import Router, RouterCreate
from mtn_cloud.resources.base import BaseResource


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
