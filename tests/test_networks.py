"""Tests for network models and resources."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from mtn_cloud.models.network import Network, NetworkCreate, NetworkUpdate
from mtn_cloud.resources.networks import NetworksResource

from .conftest import SAMPLE_NETWORK, nested_value

SAMPLE_SUBNET = {
    "id": 26,
    "name": "test-subnet",
    "cidr": "192.168.1.0/24",
    "gateway": "192.168.1.1",
    "dhcpServer": True,
    "network": {"id": 298, "name": "test-network"},
    "type": {"id": 6, "code": "openstackSubnet", "name": "OpenStack Subnet"},
    "active": True,
}

SAMPLE_NETWORK_POOL = {
    "id": 9,
    "name": "sdk-pool-1",
    "type": {"id": 1, "name": "Morpheus", "code": "morpheus"},
    "ipCount": 51,
    "freeCount": 50,
    "poolEnabled": True,
    "gateway": "10.252.69.1",
    "ipRanges": [
        {"id": 11, "startAddress": "10.252.69.10", "endAddress": "10.252.69.60"},
    ],
}

SAMPLE_NETWORK_POOL_IP = {
    "id": 100,
    "networkPoolId": 9,
    "ipType": "used",
    "ipAddress": "10.252.69.10",
    "hostname": "app-01",
}

SAMPLE_NETWORK_TYPES = {
    "networkTypes": [
        {
            "id": 1,
            "name": "OpenStack Network",
            "code": "openstackNetwork",
            "category": "openstack",
            "creatable": True,
            "deletable": True,
            "hasCidr": True,
            "hasFloatingIps": True,
            "optionTypes": [],
        },
        {
            "id": 2,
            "name": "Azure Network",
            "code": "azureNetwork",
            "category": "azure",
            "creatable": True,
            "deletable": True,
            "hasCidr": True,
            "hasFloatingIps": False,
            "optionTypes": [],
        },
    ]
}


@pytest.fixture
def resource(mock_http: MagicMock) -> NetworksResource:
    """Return a networks resource backed by a mocked HTTP client."""
    return NetworksResource(mock_http)


class TestNetworkModel:
    """Tests for Network model."""

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 298),
            ("name", "test-network"),
            ("type_code", "openstackNetwork"),
            ("type_name", "OpenStack Network"),
            ("cloud_id", 1),
        ],
    )
    def test_parse_network_field(self, field: str, expected: Any) -> None:
        """Parse network fields."""
        network = Network.model_validate(SAMPLE_NETWORK)

        assert getattr(network, field) == expected

    def test_parse_network_type(self) -> None:
        """Parse nested network type details."""
        network = Network.model_validate(SAMPLE_NETWORK)

        assert network.type is not None


class TestNetworkPayloadModels:
    """Tests for network payload models."""

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("network.name", "mtn-openstack-net"),
            ("network.zone.id", 1),
            ("network.site.id", 10),
            ("network.type.id", 7),
            ("network.cidr", "192.168.10.0/24"),
            ("network.dnsPrimary", "8.8.8.8"),
            ("network.visibility", "private"),
            ("network.tenants", [{"id": 1}, {"id": 2}]),
            ("network.resourcePermission.all", True),
        ],
    )
    def test_create_payload_field(self, path: str, expected: Any) -> None:
        """Build create payload fields."""
        payload = NetworkCreate(
            name="mtn-openstack-net",
            cloud_id=1,
            group_id=10,
            type_id=7,
            cidr="192.168.10.0/24",
            gateway="192.168.10.1",
            dns_primary="8.8.8.8",
            visibility="private",
            tenant_ids=[1, 2],
            resource_permission_all=True,
        ).to_api_payload()

        assert nested_value(payload, path) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("network.description", "updated"),
            ("network.assignPublicIp", False),
            ("network.tenants", [{"id": 1}]),
            ("network.resourcePermissions.sites", [{"id": 99}]),
        ],
    )
    def test_update_payload_field(self, path: str, expected: Any) -> None:
        """Build update payload fields."""
        payload = NetworkUpdate(
            description="updated",
            assign_public_ip=False,
            tenant_ids=[1],
            resource_permission_site_ids=[99],
        ).to_api_payload()

        assert nested_value(payload, path) == expected

    def test_update_payload_omits_display_name(self) -> None:
        """Omit unset display name from update payloads."""
        payload = NetworkUpdate(description="updated").to_api_payload()

        assert "displayName" not in payload["network"]


class TestNetworksResource:
    """Tests for NetworksResource."""

    def test_list_network_count(self, resource: NetworksResource, mock_http: MagicMock) -> None:
        """Return matching networks."""
        mock_http.get.return_value = {"networks": [SAMPLE_NETWORK]}

        assert len(resource.list(cloud_id=1)) == 1

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("args.0", "/networks"),
            ("kwargs.params.zoneId", 1),
        ],
    )
    def test_list_request(
        self,
        resource: NetworksResource,
        mock_http: MagicMock,
        path: str,
        expected: Any,
    ) -> None:
        """Send expected network list request."""
        mock_http.get.return_value = {"networks": [SAMPLE_NETWORK]}

        resource.list(cloud_id=1)

        assert nested_value(_call_data(mock_http.get.call_args), path) == expected

    def test_get_network_id(self, resource: NetworksResource, mock_http: MagicMock) -> None:
        """Return fetched network data."""
        mock_http.get.return_value = {"network": SAMPLE_NETWORK}

        assert resource.get(298).id == 298

    def test_get_network_path(self, resource: NetworksResource, mock_http: MagicMock) -> None:
        """Call the expected network detail endpoint."""
        mock_http.get.return_value = {"network": SAMPLE_NETWORK}

        resource.get(298)

        mock_http.get.assert_called_with("/networks/298")

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("args.0", "/networks"),
            ("kwargs.json.network.site.id", 10),
            ("kwargs.json.network.zone.id", 1),
            ("kwargs.json.network.type.id", 8),
        ],
    )
    def test_create_network_request(
        self,
        resource: NetworksResource,
        mock_http: MagicMock,
        path: str,
        expected: Any,
    ) -> None:
        """Send expected network create request."""
        mock_http.post.return_value = {"network": SAMPLE_NETWORK}

        self._create_network(resource)

        assert nested_value(_call_data(mock_http.post.call_args), path) == expected

    def test_create_network_id(self, resource: NetworksResource, mock_http: MagicMock) -> None:
        """Return the created network."""
        mock_http.post.return_value = {"network": SAMPLE_NETWORK}

        assert self._create_network(resource).id == 298

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 298),
            ("description", "updated"),
        ],
    )
    def test_update_network_field(
        self,
        resource: NetworksResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Return the updated network."""
        mock_http.put.return_value = {"network": {**SAMPLE_NETWORK, "description": "updated"}}

        assert getattr(resource.update(298, description="updated"), field) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("args.0", "/networks/298"),
            ("kwargs.json.network.description", "updated"),
        ],
    )
    def test_update_network_request(
        self,
        resource: NetworksResource,
        mock_http: MagicMock,
        path: str,
        expected: Any,
    ) -> None:
        """Send expected network update request."""
        mock_http.put.return_value = {"network": {**SAMPLE_NETWORK, "description": "updated"}}

        resource.update(298, description="updated")

        assert nested_value(_call_data(mock_http.put.call_args), path) == expected

    def test_delete_network(self, resource: NetworksResource, mock_http: MagicMock) -> None:
        """Delete a network by ID."""
        mock_http.delete.return_value = {"success": True}

        assert resource.delete(298) is True
        mock_http.delete.assert_called_with("/networks/298", params=None)

    def test_list_subnet_count(self, resource: NetworksResource, mock_http: MagicMock) -> None:
        """Return subnets for a network."""
        mock_http.get.return_value = {"subnets": [SAMPLE_SUBNET]}

        assert len(resource.list_subnets(298)) == 1

    def test_list_subnet_network_id(
        self,
        resource: NetworksResource,
        mock_http: MagicMock,
    ) -> None:
        """Parse subnet network relationship."""
        mock_http.get.return_value = {"subnets": [SAMPLE_SUBNET]}

        assert resource.list_subnets(298)[0].network_id == 298

    def test_list_subnet_path(self, resource: NetworksResource, mock_http: MagicMock) -> None:
        """Call the expected subnet list endpoint."""
        mock_http.get.return_value = {"subnets": [SAMPLE_SUBNET]}

        resource.list_subnets(298)

        mock_http.get.assert_called_with("/networks/298/subnets")

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("code", "openstackNetwork"),
            ("is_openstack", True),
        ],
    )
    def test_list_openstack_network_type_field(
        self,
        resource: NetworksResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Return only OpenStack network types."""
        mock_http.get.return_value = SAMPLE_NETWORK_TYPES

        assert getattr(resource.list_types(openstack_only=True)[0], field) == expected

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("name", "sdk-pool-1"),
            ("free_count", 50),
            ("ip_ranges.0.start_address", "10.252.69.10"),
        ],
    )
    def test_list_pool_field(
        self,
        resource: NetworksResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse network pool fields."""
        mock_http.get.return_value = {"networkPools": [SAMPLE_NETWORK_POOL]}
        pool = resource.list_pools(phrase="sdk")[0]

        assert nested_value({"pool": pool.model_dump()}, f"pool.{field}") == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("args.0", "/networks/pools"),
            ("kwargs.params.phrase", "sdk"),
        ],
    )
    def test_list_pool_request(
        self,
        resource: NetworksResource,
        mock_http: MagicMock,
        path: str,
        expected: Any,
    ) -> None:
        """Send expected network pool list request."""
        mock_http.get.return_value = {"networkPools": [SAMPLE_NETWORK_POOL]}

        resource.list_pools(phrase="sdk")

        assert nested_value(_call_data(mock_http.get.call_args), path) == expected

    @pytest.mark.parametrize(("field", "expected"), [("id", 9), ("ip_count", 51)])
    def test_get_pool_field(
        self,
        resource: NetworksResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Return a network pool by ID."""
        mock_http.get.return_value = {"networkPool": SAMPLE_NETWORK_POOL}

        assert getattr(resource.get_pool(9), field) == expected

    def test_get_pool_path(self, resource: NetworksResource, mock_http: MagicMock) -> None:
        """Call the expected network pool detail endpoint."""
        mock_http.get.return_value = {"networkPool": SAMPLE_NETWORK_POOL}

        resource.get_pool(9)

        mock_http.get.assert_called_with("/networks/pools/9")

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("ip_address", "10.252.69.10"),
            ("hostname", "app-01"),
        ],
    )
    def test_list_pool_ip_field(
        self,
        resource: NetworksResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse network pool IP fields."""
        mock_http.get.return_value = {"networkPoolIps": [SAMPLE_NETWORK_POOL_IP]}

        assert getattr(resource.list_pool_ips(9, hostname="app-01")[0], field) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("args.0", "/networks/pools/9/ips"),
            ("kwargs.params.hostname", "app-01"),
        ],
    )
    def test_list_pool_ip_request(
        self,
        resource: NetworksResource,
        mock_http: MagicMock,
        path: str,
        expected: Any,
    ) -> None:
        """Send expected network pool IP request."""
        mock_http.get.return_value = {"networkPoolIps": [SAMPLE_NETWORK_POOL_IP]}

        resource.list_pool_ips(9, hostname="app-01")

        assert nested_value(_call_data(mock_http.get.call_args), path) == expected

    @staticmethod
    def _create_network(resource: NetworksResource) -> Network:
        return resource.create(
            name="test-network",
            cloud_id=1,
            group_id=10,
            type_id=8,
            cidr="192.168.1.0/24",
            gateway="192.168.1.1",
        )


def _call_data(call_args: Any) -> dict[str, Any]:
    return {"args": list(call_args.args), "kwargs": call_args.kwargs}
