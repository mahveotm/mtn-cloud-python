"""
Tests for Network models and resource.
"""

from unittest.mock import MagicMock

from mtn_cloud.models.network import Network, NetworkCreate, NetworkUpdate
from mtn_cloud.resources.networks import NetworksResource

from .conftest import SAMPLE_NETWORK

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


class TestNetworkModel:
    """Tests for Network model."""

    def test_parse_network(self):
        """Test parsing network from API response."""
        network = Network.model_validate(SAMPLE_NETWORK)

        assert network.id == 298
        assert network.name == "test-network"
        assert network.type is not None
        assert network.type_code == "openstackNetwork"
        assert network.type_name == "OpenStack Network"
        assert network.cloud_id == 1


class TestNetworkPayloadModels:
    """Tests for network payload models."""

    def test_create_payload(self):
        """Test NetworkCreate payload generation."""
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

        assert payload["network"]["name"] == "mtn-openstack-net"
        assert payload["network"]["zone"]["id"] == 1
        assert payload["network"]["site"]["id"] == 10
        assert payload["network"]["type"]["id"] == 7
        assert payload["network"]["cidr"] == "192.168.10.0/24"
        assert payload["network"]["dnsPrimary"] == "8.8.8.8"
        assert payload["network"]["visibility"] == "private"
        assert payload["network"]["tenants"] == [{"id": 1}, {"id": 2}]
        assert payload["network"]["resourcePermission"]["all"] is True

    def test_update_payload(self):
        """Test NetworkUpdate payload generation."""
        payload = NetworkUpdate(
            description="updated",
            assign_public_ip=False,
            tenant_ids=[1],
            resource_permission_site_ids=[99],
        ).to_api_payload()

        assert payload["network"]["description"] == "updated"
        assert payload["network"]["assignPublicIp"] is False
        assert payload["network"]["tenants"] == [{"id": 1}]
        assert payload["network"]["resourcePermissions"]["sites"] == [{"id": 99}]
        assert "displayName" not in payload["network"]


class TestNetworksResource:
    """Tests for NetworksResource."""

    def test_list_networks(self):
        """Test listing networks."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"networks": [SAMPLE_NETWORK]}

        resource = NetworksResource(mock_http)
        networks = resource.list(cloud_id=1)

        assert len(networks) == 1
        assert networks[0].id == 298
        call_args = mock_http.get.call_args
        assert call_args[0][0] == "/networks"
        assert call_args[1]["params"]["zoneId"] == 1

    def test_get_network(self):
        """Test getting network by ID."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"network": SAMPLE_NETWORK}

        resource = NetworksResource(mock_http)
        network = resource.get(298)

        assert network.id == 298
        mock_http.get.assert_called_with("/networks/298")

    def test_create_network(self):
        """Test creating network."""
        mock_http = MagicMock()
        mock_http.post.return_value = {"network": SAMPLE_NETWORK}

        resource = NetworksResource(mock_http)
        created = resource.create(
            name="test-network",
            cloud_id=1,
            group_id=10,
            type_id=8,
            cidr="192.168.1.0/24",
            gateway="192.168.1.1",
        )

        assert created.id == 298
        call_args = mock_http.post.call_args
        assert call_args[0][0] == "/networks"
        assert call_args[1]["json"]["network"]["site"]["id"] == 10
        assert call_args[1]["json"]["network"]["zone"]["id"] == 1
        assert call_args[1]["json"]["network"]["type"]["id"] == 8

    def test_update_network(self):
        """Test updating network."""
        mock_http = MagicMock()
        mock_http.put.return_value = {"network": {**SAMPLE_NETWORK, "description": "updated"}}

        resource = NetworksResource(mock_http)
        updated = resource.update(298, description="updated")

        assert updated.id == 298
        assert updated.description == "updated"
        call_args = mock_http.put.call_args
        assert call_args[0][0] == "/networks/298"
        assert call_args[1]["json"]["network"]["description"] == "updated"

    def test_delete_network(self):
        """Test deleting network."""
        mock_http = MagicMock()
        mock_http.delete.return_value = {"success": True}

        resource = NetworksResource(mock_http)
        deleted = resource.delete(298)

        assert deleted is True
        mock_http.delete.assert_called_with("/networks/298", params=None)

    def test_list_subnets(self):
        """Test listing network subnets."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"subnets": [SAMPLE_SUBNET]}

        resource = NetworksResource(mock_http)
        subnets = resource.list_subnets(298)

        assert len(subnets) == 1
        assert subnets[0].network_id == 298
        mock_http.get.assert_called_with("/networks/298/subnets")

    def test_list_network_types_openstack_only(self):
        """Test listing network types filtered to OpenStack."""
        mock_http = MagicMock()
        mock_http.get.return_value = SAMPLE_NETWORK_TYPES

        resource = NetworksResource(mock_http)
        network_types = resource.list_types(openstack_only=True)

        assert len(network_types) == 1
        assert network_types[0].code == "openstackNetwork"
        assert network_types[0].is_openstack is True

    def test_list_pools(self):
        """Test listing network pools."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"networkPools": [SAMPLE_NETWORK_POOL]}

        resource = NetworksResource(mock_http)
        pools = resource.list_pools(phrase="sdk")

        assert len(pools) == 1
        assert pools[0].name == "sdk-pool-1"
        assert pools[0].free_count == 50
        assert pools[0].ip_ranges[0].start_address == "10.252.69.10"
        call_args = mock_http.get.call_args
        assert call_args[0][0] == "/networks/pools"
        assert call_args[1]["params"]["phrase"] == "sdk"

    def test_get_pool(self):
        """Test getting a network pool by ID."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"networkPool": SAMPLE_NETWORK_POOL}

        resource = NetworksResource(mock_http)
        pool = resource.get_pool(9)

        assert pool.id == 9
        assert pool.ip_count == 51
        mock_http.get.assert_called_with("/networks/pools/9")

    def test_list_pool_ips(self):
        """Test listing IPs within a pool."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"networkPoolIps": [SAMPLE_NETWORK_POOL_IP]}

        resource = NetworksResource(mock_http)
        ips = resource.list_pool_ips(9, hostname="app-01")

        assert len(ips) == 1
        assert ips[0].ip_address == "10.252.69.10"
        assert ips[0].hostname == "app-01"
        call_args = mock_http.get.call_args
        assert call_args[0][0] == "/networks/pools/9/ips"
        assert call_args[1]["params"]["hostname"] == "app-01"
