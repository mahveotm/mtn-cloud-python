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

SAMPLE_FLOATING_IP = {
    "id": 51,
    "externalId": "1b633f67-6a1e-4195-b1e3-45b9704e4766",
    "cloud": {"id": 1, "name": "MTNNG_CLOUD_AZ_1", "type": "openstack"},
    "server": {"id": 21840, "name": "test-vm"},
    "ipStatus": "assigned",
    "ipAddress": "10.32.23.188",
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

    def test_list_floating_ips(self):
        """Test listing floating IPs."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"networkFloatingIps": [SAMPLE_FLOATING_IP]}

        resource = NetworksResource(mock_http)
        ips = resource.list_floating_ips(cloud_id=1, ip_status="assigned")

        assert len(ips) == 1
        assert ips[0].ip_address == "10.32.23.188"
        call_args = mock_http.get.call_args
        assert call_args[0][0] == "/networks/floating-ips"
        assert call_args[1]["params"]["zoneId"] == 1
        assert call_args[1]["params"]["ipStatus"] == "assigned"

    def test_allocate_floating_ip(self):
        """Test allocating floating IP."""
        mock_http = MagicMock()
        mock_http.post.return_value = {"networkFloatingIp": SAMPLE_FLOATING_IP}

        resource = NetworksResource(mock_http)
        ip = resource.allocate_floating_ip(network_server_id=5, floating_ip_pool_id=1)

        assert ip.id == 51
        mock_http.post.assert_called_with(
            "/networks/floating-ips",
            json={"networkServerId": 5, "floatingIpPoolId": 1},
        )

    def test_release_floating_ip(self):
        """Test releasing floating IP."""
        mock_http = MagicMock()
        mock_http.put.return_value = {"success": True}

        resource = NetworksResource(mock_http)
        released = resource.release_floating_ip(51)

        assert released is True
        mock_http.put.assert_called_with("/networks/floating-ips/51/release")
