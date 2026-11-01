"""Focused router lifecycle tests using the shared mocked HTTP client."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mtn_cloud.exceptions import MTNCloudError, NotFoundError, TimeoutError
from mtn_cloud.resources.routers import RoutersResource

ROUTER = {
    "id": 42,
    "name": "app",
    "status": "ok",
    "type": {"id": 1, "code": "neutronRouter"},
}
CREATE = {
    "name": "app",
    "group_id": 621,
    "cloud_id": 4,
    "resource_pool_id": 213,
    "internal_subnet_ids": [4112],
    "external_network_id": 34,
}


def prepare_create(http: MagicMock) -> RoutersResource:
    http.get.side_effect = [
        {
            "networkRouterTypes": [
                {"id": 9, "code": "other"},
                {"id": 1, "code": "neutronRouter"},
            ]
        },
        {
            "networkRouterType": {
                "id": 1,
                "code": "neutronRouter",
                "creatable": True,
                "hasNetworkServer": False,
            }
        },
        {"networkRouter": ROUTER},
    ]
    http.post.return_value = {"success": True, "id": 42}
    return RoutersResource(http)


def test_create_resolves_mtn_type_and_reads_id_only_response(
    mock_http: MagicMock,
) -> None:
    routers = prepare_create(mock_http)
    assert routers.create(**CREATE).id == 42
    mock_http.post.assert_called_once_with(
        "/networks/routers",
        json={
            "networkRouter": {
                "name": "app",
                "site": {"id": 621},
                "zone": {"id": 4},
                "type": {"id": 1},
                "poolId": "pool-213",
                "config": {"poolId": "pool-213"},
                "enabled": True,
                "externalNetwork": {"id": 34},
                "interfaces": [{"networkSubnet": {"id": 4112}}],
            }
        },
    )
    mock_http.get.assert_called_with("/networks/routers/42")


def test_post_create_read_error_preserves_cleanup_id(mock_http: MagicMock) -> None:
    routers = prepare_create(mock_http)
    responses = list(mock_http.get.side_effect)
    responses[-1] = NotFoundError(resource_type="Router", resource_id=42)
    mock_http.get.side_effect = responses
    with pytest.raises(MTNCloudError) as exc:
        routers.create(**CREATE)
    assert exc.value.response == {"router_id": 42}


def test_rejects_invalid_subnets_before_requests(mock_http: MagicMock) -> None:
    with pytest.raises(ValueError):
        RoutersResource(mock_http).create(**{**CREATE, "internal_subnet_ids": []})
    mock_http.get.assert_not_called()
    mock_http.post.assert_not_called()


def test_list_and_delete_lifecycle(mock_http: MagicMock) -> None:
    routers = RoutersResource(mock_http)
    mock_http.get.return_value = {"networkRouters": [ROUTER]}
    assert routers.list()[0].id == 42
    mock_http.get.return_value = {"networkRouter": ROUTER}
    assert routers.delete(42)
    mock_http.delete.assert_called_once_with("/networks/routers/42", params=None)
    mock_http.get.side_effect = [{"networkRouter": ROUTER}, NotFoundError()]
    with patch("mtn_cloud.resources.routers.time.sleep"):
        assert routers.wait_until_deleted(42)
    mock_http.get.side_effect = NotFoundError()
    assert routers.delete(42)


def test_delete_rejects_other_router_types(mock_http: MagicMock) -> None:
    mock_http.get.return_value = {"networkRouter": {**ROUTER, "type": {"id": 9, "code": "other"}}}
    with pytest.raises(ValueError, match="not an MTN"):
        RoutersResource(mock_http).delete(42)
    mock_http.delete.assert_not_called()


def test_wait_until_ready(mock_http: MagicMock) -> None:
    mock_http.get.side_effect = [
        {"networkRouter": {**ROUTER, "status": "provisioning"}},
        {"networkRouter": ROUTER},
    ]
    with patch("mtn_cloud.resources.routers.time.sleep"):
        assert RoutersResource(mock_http).wait_until_ready(42).status == "ok"


def test_failed_provisioning_keeps_router_id(mock_http: MagicMock) -> None:
    mock_http.get.return_value = {"networkRouter": {**ROUTER, "status": "failed"}}
    with pytest.raises(MTNCloudError, match="provisioning failed") as exc:
        RoutersResource(mock_http).wait_until_ready(42)
    assert exc.value.response["router_id"] == 42


@pytest.mark.parametrize("method", ["wait_until_ready", "wait_until_deleted"])
def test_wait_timeout(mock_http: MagicMock, method: str) -> None:
    mock_http.get.return_value = {"networkRouter": {**ROUTER, "status": "provisioning"}}
    with patch("mtn_cloud.resources.routers.time.monotonic", side_effect=[0, 301]):
        with pytest.raises(TimeoutError) as exc:
            getattr(RoutersResource(mock_http), method)(42)
    assert exc.value.response["router_id"] == 42


def test_create_requires_mtn_type(mock_http: MagicMock) -> None:
    mock_http.get.return_value = {"networkRouterTypes": [{"id": 9, "code": "other"}]}
    with pytest.raises(ValueError, match="neutronRouter"):
        RoutersResource(mock_http).create(**CREATE)
    mock_http.post.assert_not_called()


@pytest.fixture
def external_discovery_http(mock_http: MagicMock) -> MagicMock:
    options = json.loads(
        (Path(__file__).parent / "fixtures/external_network_options.json").read_text()
    )

    def get(path: str, params: dict | None = None) -> dict:
        if path == "/groups":
            return {"groups": [{"id": 621, "name": "group", "zones": [{"id": 4}]}]}
        if path == "/options/zonePools":
            assert params == {"cloudId": 4, "groupId": 621, "provisionTypeCode": "openstack"}
            return {"data": [{"id": 213, "name": "project", "value": "pool-213"}]}
        if path == "/network-router-types":
            return {"networkRouterTypes": [{"id": 17, "code": "neutronRouter"}]}
        if path == "/network-router-types/17":
            return {
                "networkRouterType": {
                    "id": 17,
                    "code": "neutronRouter",
                    "creatable": True,
                    "hasNetworkServer": False,
                }
            }
        if path == "/options/openstackExternalNetworks":
            assert params == {
                "router.zone.id": 4,
                "router.site.id": 621,
                "router.poolId": "pool-213",
                "routerType.id": 17,
            }
            return options
        raise AssertionError(f"Unexpected endpoint: {path}")

    mock_http.get.side_effect = get
    return mock_http


def test_external_network_discovery_uses_scoped_options(external_discovery_http: MagicMock) -> None:
    routers = RoutersResource(external_discovery_http)
    networks = routers.list_external_networks(group="group", resource_pool="project")
    assert [(n.name, n.id) for n in networks] == [
        ("public-network-01", 34),
        ("public-network-02", 32),
        ("public-network-03", 30),
        ("public-network-04", 31),
    ]
    assert (
        routers.get_external_network(
            "public-network-02", group="group", resource_pool="pool-213"
        ).id
        == 32
    )
    with pytest.raises(NotFoundError, match="Available names: public-network-01"):
        routers.get_external_network("missing", group="group", resource_pool="project")


def test_external_network_lookup_rejects_duplicate_names(
    external_discovery_http: MagicMock,
) -> None:
    original = external_discovery_http.get.side_effect

    def get(path: str, params: dict | None = None) -> dict:
        if path == "/options/openstackExternalNetworks":
            return {"data": [{"name": "public", "value": 34}, {"name": "public", "value": 32}]}
        return original(path, params=params)

    external_discovery_http.get.side_effect = get
    with pytest.raises(ValueError, match="ambiguous"):
        RoutersResource(external_discovery_http).get_external_network(
            "public", group="group", resource_pool="project"
        )


def test_external_discovery_requires_unambiguous_cloud(mock_http: MagicMock) -> None:
    mock_http.get.return_value = {
        "groups": [{"id": 621, "name": "group", "zones": [{"id": 4}, {"id": 5}]}]
    }
    with pytest.raises(ValueError, match="set cloud_id explicitly"):
        RoutersResource(mock_http).list_external_networks(group="group", resource_pool="project")
    mock_http.get.assert_called_once()
