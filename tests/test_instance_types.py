"""
Tests for InstanceType models and resource.
"""

from unittest.mock import MagicMock

from mtn_cloud.models.instance_type import InstanceType, InstanceTypeLayout
from mtn_cloud.resources.instance_types import InstanceTypesResource


# Sample instance type data matching MTN Cloud API response
SAMPLE_INSTANCE_TYPE = {
    "id": 104,
    "name": "MTN CentOS Stream 10",
    "code": "MTN-CS10",
    "description": "MTN CentOS Stream 10 is a cloud-optimized CentOS Stream 10 image tailored for MTN Cloud.",
    "labels": [],
    "provisionTypeCode": "openstack",
    "category": "os",
    "active": True,
    "environmentPrefix": "MTN_CENTOS_STREAM_10",
    "visibility": "public",
    "featured": False,
    "versions": ["10"],
    "instanceTypeLayouts": [
        {
            "id": 327,
            "name": "MTN-CentOS Stream 10",
            "provisionTypeCode": "openstack",
        }
    ],
    "account": {
        "id": 1,
        "name": "MTNNG_MASTER_TENANT",
    },
}

SAMPLE_INSTANCE_TYPE_MULTIPLE_LAYOUTS = {
    "id": 113,
    "name": "Morpheus Builds",
    "code": "morphbuilds",
    "description": None,
    "labels": [],
    "provisionTypeCode": "mixed",
    "category": "web",
    "active": True,
    "environmentPrefix": "MORPHEUS_BUILDS",
    "visibility": "private",
    "featured": True,
    "versions": ["7.9-v1", "8.3-v1"],
    "instanceTypeLayouts": [
        {"id": 1313, "name": "Morpheus Debian", "provisionTypeCode": "vmware"},
        {"id": 1315, "name": "Morpheus Ubuntu", "provisionTypeCode": "vmware"},
        {"id": 1312, "name": "Morpheus CentOS", "provisionTypeCode": "vmware"},
    ],
    "account": {"id": 1, "name": "mastertenant"},
}

SAMPLE_INSTANCE_TYPES_LIST = {
    "instanceTypes": [
        SAMPLE_INSTANCE_TYPE,
        {
            "id": 89,
            "name": "MTN Ubuntu Server 24.04.3LTS",
            "code": "MTN-U24.04LTS",
            "description": "MTN Ubuntu Server 24.04.3LTS is a cloud-optimized Ubuntu Server image.",
            "labels": [],
            "provisionTypeCode": "openstack",
            "category": "os",
            "active": True,
            "environmentPrefix": "MTN_UBUNTU_SERVER_24_04_3LTS",
            "visibility": "public",
            "featured": False,
            "versions": ["v24.04"],
            "instanceTypeLayouts": [
                {"id": 309, "name": "MTN-Ubuntu Server 24.04.3LTS", "provisionTypeCode": "openstack"}
            ],
        },
        {
            "id": 144,
            "name": "MTN MySQL Single-Node",
            "code": "MTN-MySQL01",
            "description": "A production-ready MySQL instance optimized for MTN Cloud.",
            "labels": ["Database", "Linux", "Managed", "Mysql"],
            "provisionTypeCode": "openstack",
            "category": "sql",
            "active": True,
            "environmentPrefix": "MYSQL_SINGLE-NODE",
            "visibility": "public",
            "featured": False,
            "versions": ["1"],
            "instanceTypeLayouts": [
                {"id": 375, "name": "Unmanaged Single Node MySQL", "provisionTypeCode": "openstack"}
            ],
        },
    ],
    "meta": {"offset": 0, "max": 25, "size": 3, "total": 3},
}


class TestInstanceTypeLayoutModel:
    """Tests for InstanceTypeLayout model."""

    def test_parse_layout(self):
        """Test parsing layout from API response."""
        layout_data = {"id": 327, "name": "MTN-CentOS Stream 10", "provisionTypeCode": "openstack"}
        layout = InstanceTypeLayout.model_validate(layout_data)

        assert layout.id == 327
        assert layout.name == "MTN-CentOS Stream 10"
        assert layout.provision_type_code == "openstack"

    def test_layout_str(self):
        """Test layout string representation."""
        layout = InstanceTypeLayout(id=327, name="MTN-CentOS Stream 10", provisionTypeCode="openstack")
        assert "327" in str(layout)
        assert "MTN-CentOS Stream 10" in str(layout)


class TestInstanceTypeModel:
    """Tests for InstanceType model."""

    def test_parse_instance_type(self):
        """Test parsing instance type from API response."""
        it = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE)

        assert it.id == 104
        assert it.name == "MTN CentOS Stream 10"
        assert it.code == "MTN-CS10"
        assert it.category == "os"
        assert it.active is True
        assert it.visibility == "public"
        assert len(it.versions) == 1
        assert "10" in it.versions

    def test_instance_type_str(self):
        """Test instance type string representation includes id, name, code."""
        it = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE)
        str_repr = str(it)

        assert "104" in str_repr
        assert "MTN CentOS Stream 10" in str_repr
        assert "MTN-CS10" in str_repr

    def test_default_layout_id(self):
        """Test getting default layout ID."""
        it = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE)

        assert it.default_layout_id == 327

    def test_default_layout(self):
        """Test getting default layout."""
        it = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE)

        layout = it.default_layout
        assert layout is not None
        assert layout.id == 327
        assert layout.name == "MTN-CentOS Stream 10"

    def test_layouts_property(self):
        """Test accessing all layouts."""
        it = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE_MULTIPLE_LAYOUTS)

        assert len(it.layouts) == 3
        assert it.layouts[0].id == 1313
        assert it.layouts[1].id == 1315
        assert it.layouts[2].id == 1312

    def test_get_layout_by_name(self):
        """Test getting layout by name."""
        it = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE_MULTIPLE_LAYOUTS)

        layout = it.get_layout_by_name("Morpheus Ubuntu")
        assert layout is not None
        assert layout.id == 1315

        # Test not found
        not_found = it.get_layout_by_name("NonExistent")
        assert not_found is None

    def test_get_layout_by_id(self):
        """Test getting layout by ID."""
        it = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE_MULTIPLE_LAYOUTS)

        layout = it.get_layout_by_id(1312)
        assert layout is not None
        assert layout.name == "Morpheus CentOS"

        # Test not found
        not_found = it.get_layout_by_id(99999)
        assert not_found is None

    def test_empty_layouts(self):
        """Test instance type with no layouts."""
        data = {**SAMPLE_INSTANCE_TYPE, "instanceTypeLayouts": []}
        it = InstanceType.model_validate(data)

        assert it.default_layout_id is None
        assert it.default_layout is None
        assert len(it.layouts) == 0


class TestInstanceTypesResource:
    """Tests for InstanceTypesResource."""

    def test_list_instance_types(self):
        """Test listing instance types."""
        mock_http = MagicMock()
        mock_http.get.return_value = SAMPLE_INSTANCE_TYPES_LIST

        resource = InstanceTypesResource(mock_http)
        instance_types = resource.list()

        assert len(instance_types) == 3
        assert instance_types[0].code == "MTN-CS10"
        assert instance_types[1].code == "MTN-U24.04LTS"
        assert instance_types[2].code == "MTN-MySQL01"
        mock_http.get.assert_called_once()

    def test_get_instance_type(self):
        """Test getting single instance type by ID."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"instanceType": SAMPLE_INSTANCE_TYPE}

        resource = InstanceTypesResource(mock_http)
        it = resource.get(104)

        assert it.id == 104
        assert it.code == "MTN-CS10"
        mock_http.get.assert_called_with("/instance-types/104")

    def test_get_by_code(self):
        """Test getting instance type by code."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"instanceTypes": [SAMPLE_INSTANCE_TYPE]}

        resource = InstanceTypesResource(mock_http)
        it = resource.get_by_code("MTN-CS10")

        assert it.code == "MTN-CS10"
        assert it.name == "MTN CentOS Stream 10"

    def test_get_by_name(self):
        """Test getting instance type by name."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"instanceTypes": [SAMPLE_INSTANCE_TYPE]}

        resource = InstanceTypesResource(mock_http)
        it = resource.get_by_name("MTN CentOS Stream 10")

        assert it.name == "MTN CentOS Stream 10"
        assert it.code == "MTN-CS10"

    def test_list_with_category_filter(self):
        """Test listing instance types filtered by category."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"instanceTypes": [SAMPLE_INSTANCE_TYPE]}

        resource = InstanceTypesResource(mock_http)
        _instance_types = resource.list(category="os")

        call_args = mock_http.get.call_args
        params = call_args[1]["params"]
        assert params["category"] == "os"

    def test_list_os(self):
        """Test listing OS instance types."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"instanceTypes": [SAMPLE_INSTANCE_TYPE]}

        resource = InstanceTypesResource(mock_http)
        _instance_types = resource.list_os()

        call_args = mock_http.get.call_args
        params = call_args[1]["params"]
        assert params["category"] == "os"

    def test_list_databases(self):
        """Test listing database instance types."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"instanceTypes": []}

        resource = InstanceTypesResource(mock_http)
        _instance_types = resource.list_databases()

        call_args = mock_http.get.call_args
        params = call_args[1]["params"]
        assert params["category"] == "sql"

    def test_list_web(self):
        """Test listing web server instance types."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"instanceTypes": []}

        resource = InstanceTypesResource(mock_http)
        _instance_types = resource.list_web()

        call_args = mock_http.get.call_args
        params = call_args[1]["params"]
        assert params["category"] == "web"

    def test_list_apps(self):
        """Test listing application instance types."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"instanceTypes": []}

        resource = InstanceTypesResource(mock_http)
        _instance_types = resource.list_apps()

        call_args = mock_http.get.call_args
        params = call_args[1]["params"]
        assert params["category"] == "apps"

