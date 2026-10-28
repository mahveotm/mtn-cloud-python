"""Focused router lifecycle tests using the shared mocked HTTP client."""

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
