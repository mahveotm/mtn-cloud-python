"""
Tests for Cloud models and resource.
"""

from unittest.mock import MagicMock

from mtn_cloud.resources.clouds import CloudsResource

from .conftest import SAMPLE_CLOUD


class TestCloudsResource:
    """Tests for CloudsResource."""

    def test_list_clouds(self):
        """Test listing clouds."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"zones": [SAMPLE_CLOUD]}

        resource = CloudsResource(mock_http)
        clouds = resource.list()

        assert len(clouds) == 1
        assert clouds[0].id == 1
        assert clouds[0].name == "MTNNG_CLOUD_AZ_1"
        assert clouds[0].type_code == "openstack"

    def test_list_openstack_clouds(self):
        """Test listing OpenStack clouds."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"zones": [SAMPLE_CLOUD]}

        resource = CloudsResource(mock_http)
        _clouds = resource.list_openstack()

        call_args = mock_http.get.call_args
        assert call_args[0][0] == "/zones"
        assert call_args[1]["params"]["type"] == "openstack"

    def test_get_cloud(self):
        """Test getting cloud by ID."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"zone": SAMPLE_CLOUD}

        resource = CloudsResource(mock_http)
        cloud = resource.get(1)

        assert cloud.id == 1
        assert cloud.type_code == "openstack"
        mock_http.get.assert_called_with("/zones/1")
