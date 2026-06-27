"""Tests for instance type models and resources."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from mtn_cloud.models.instance_type import InstanceType, InstanceTypeLayout
from mtn_cloud.resources.instance_types import InstanceTypesResource

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
    "name": "MTN Builds",
    "code": "mtnbuilds",
    "description": None,
    "labels": [],
    "provisionTypeCode": "mixed",
    "category": "web",
    "active": True,
    "environmentPrefix": "MTN_BUILDS",
    "visibility": "private",
    "featured": True,
    "versions": ["7.9-v1", "8.3-v1"],
    "instanceTypeLayouts": [
        {"id": 1313, "name": "MTN Debian", "provisionTypeCode": "vmware"},
        {"id": 1315, "name": "MTN Ubuntu", "provisionTypeCode": "vmware"},
        {"id": 1312, "name": "MTN CentOS", "provisionTypeCode": "vmware"},
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
                {
                    "id": 309,
                    "name": "MTN-Ubuntu Server 24.04.3LTS",
                    "provisionTypeCode": "openstack",
                }
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
                {
                    "id": 375,
                    "name": "Unmanaged Single Node MySQL",
                    "provisionTypeCode": "openstack",
                }
            ],
        },
    ],
    "meta": {"offset": 0, "max": 25, "size": 3, "total": 3},
}


@pytest.fixture
def resource(mock_http: MagicMock) -> InstanceTypesResource:
    """Return an instance types resource backed by a mocked HTTP client."""
    return InstanceTypesResource(mock_http)


class TestInstanceTypeLayoutModel:
    """Tests for InstanceTypeLayout model."""

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 327),
            ("name", "MTN-CentOS Stream 10"),
            ("provision_type_code", "openstack"),
        ],
    )
    def test_parse_layout_field(self, field: str, expected: Any) -> None:
        """Parse layout fields."""
        layout = InstanceTypeLayout.model_validate(
            {
                "id": 327,
                "name": "MTN-CentOS Stream 10",
                "provisionTypeCode": "openstack",
            }
        )

        assert getattr(layout, field) == expected

    @pytest.mark.parametrize("expected", ["327", "MTN-CentOS Stream 10"])
    def test_layout_str_contains_identity(self, expected: str) -> None:
        """Include stable layout identity in string output."""
        layout = InstanceTypeLayout(
            id=327,
            name="MTN-CentOS Stream 10",
            provisionTypeCode="openstack",
        )

        assert expected in str(layout)


class TestInstanceTypeModel:
    """Tests for InstanceType model."""

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 104),
            ("name", "MTN CentOS Stream 10"),
            ("code", "MTN-CS10"),
            ("category", "os"),
            ("active", True),
            ("visibility", "public"),
        ],
    )
    def test_parse_instance_type_field(self, field: str, expected: Any) -> None:
        """Parse instance type fields."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE)

        assert getattr(instance_type, field) == expected

    def test_parse_instance_type_version_count(self) -> None:
        """Parse instance type versions."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE)

        assert len(instance_type.versions) == 1

    def test_parse_instance_type_version_value(self) -> None:
        """Parse instance type version values."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE)

        assert "10" in instance_type.versions

    @pytest.mark.parametrize("expected", ["104", "MTN CentOS Stream 10", "MTN-CS10"])
    def test_instance_type_str_contains_identity(self, expected: str) -> None:
        """Include stable instance type identity in string output."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE)

        assert expected in str(instance_type)

    def test_default_layout_id(self) -> None:
        """Return the first layout ID as the default."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE)

        assert instance_type.default_layout_id == 327

    @pytest.mark.parametrize(("field", "expected"), [("id", 327), ("name", "MTN-CentOS Stream 10")])
    def test_default_layout_field(self, field: str, expected: Any) -> None:
        """Return the first layout as the default."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE)

        assert getattr(instance_type.default_layout, field) == expected

    @pytest.mark.parametrize(("index", "expected"), [(0, 1313), (1, 1315), (2, 1312)])
    def test_layout_id_by_index(self, index: int, expected: int) -> None:
        """Expose all layouts in API order."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE_MULTIPLE_LAYOUTS)

        assert instance_type.layouts[index].id == expected

    def test_layout_count(self) -> None:
        """Expose all parsed layouts."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE_MULTIPLE_LAYOUTS)

        assert len(instance_type.layouts) == 3

    def test_get_layout_by_name(self) -> None:
        """Find a layout by name."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE_MULTIPLE_LAYOUTS)

        assert instance_type.get_layout_by_name("MTN Ubuntu").id == 1315

    def test_get_layout_by_name_returns_none_when_missing(self) -> None:
        """Return None when a layout name does not exist."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE_MULTIPLE_LAYOUTS)

        assert instance_type.get_layout_by_name("NonExistent") is None

    def test_get_layout_by_id(self) -> None:
        """Find a layout by ID."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE_MULTIPLE_LAYOUTS)

        assert instance_type.get_layout_by_id(1312).name == "MTN CentOS"

    def test_get_layout_by_id_returns_none_when_missing(self) -> None:
        """Return None when a layout ID does not exist."""
        instance_type = InstanceType.model_validate(SAMPLE_INSTANCE_TYPE_MULTIPLE_LAYOUTS)

        assert instance_type.get_layout_by_id(99999) is None

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("default_layout_id", None),
            ("default_layout", None),
            ("layouts", []),
        ],
    )
    def test_empty_layout_field(self, field: str, expected: Any) -> None:
        """Handle instance types with no layouts."""
        data = {**SAMPLE_INSTANCE_TYPE, "instanceTypeLayouts": []}
        instance_type = InstanceType.model_validate(data)

        assert getattr(instance_type, field) == expected


class TestInstanceTypesResource:
    """Tests for InstanceTypesResource."""

    def test_list_instance_type_count(
        self,
        resource: InstanceTypesResource,
        mock_http: MagicMock,
    ) -> None:
        """Return all instance types from the list endpoint."""
        mock_http.get.return_value = SAMPLE_INSTANCE_TYPES_LIST

        assert len(resource.list()) == 3

    @pytest.mark.parametrize(
        ("index", "expected"),
        [(0, "MTN-CS10"), (1, "MTN-U24.04LTS"), (2, "MTN-MySQL01")],
    )
    def test_list_instance_type_code(
        self,
        resource: InstanceTypesResource,
        mock_http: MagicMock,
        index: int,
        expected: str,
    ) -> None:
        """Parse listed instance type codes."""
        mock_http.get.return_value = SAMPLE_INSTANCE_TYPES_LIST

        assert resource.list()[index].code == expected

    def test_list_instance_types_calls_get(
        self,
        resource: InstanceTypesResource,
        mock_http: MagicMock,
    ) -> None:
        """Call the instance type list endpoint once."""
        mock_http.get.return_value = SAMPLE_INSTANCE_TYPES_LIST

        resource.list()

        mock_http.get.assert_called_once()

    @pytest.mark.parametrize(("field", "expected"), [("id", 104), ("code", "MTN-CS10")])
    def test_get_instance_type_field(
        self,
        resource: InstanceTypesResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Return an instance type by ID."""
        mock_http.get.return_value = {"instanceType": SAMPLE_INSTANCE_TYPE}

        assert getattr(resource.get(104), field) == expected

    def test_get_instance_type_path(
        self,
        resource: InstanceTypesResource,
        mock_http: MagicMock,
    ) -> None:
        """Call the expected instance type detail endpoint."""
        mock_http.get.return_value = {"instanceType": SAMPLE_INSTANCE_TYPE}

        resource.get(104)

        mock_http.get.assert_called_with("/instance-types/104")

    @pytest.mark.parametrize(
        ("lookup_method", "lookup_value", "field", "expected"),
        [
            ("get_by_code", "MTN-CS10", "code", "MTN-CS10"),
            ("get_by_code", "MTN-CS10", "name", "MTN CentOS Stream 10"),
            ("get_by_name", "MTN CentOS Stream 10", "name", "MTN CentOS Stream 10"),
            ("get_by_name", "MTN CentOS Stream 10", "code", "MTN-CS10"),
        ],
    )
    def test_lookup_instance_type_field(
        self,
        resource: InstanceTypesResource,
        mock_http: MagicMock,
        lookup_method: str,
        lookup_value: str,
        field: str,
        expected: Any,
    ) -> None:
        """Look up instance types by stable identifiers."""
        mock_http.get.return_value = {"instanceTypes": [SAMPLE_INSTANCE_TYPE]}

        instance_type = getattr(resource, lookup_method)(lookup_value)

        assert getattr(instance_type, field) == expected

    @pytest.mark.parametrize(
        ("method_name", "expected"),
        [
            ("list", "os"),
            ("list_os", "os"),
            ("list_databases", "sql"),
            ("list_web", "web"),
            ("list_apps", "apps"),
        ],
    )
    def test_category_filter(
        self,
        resource: InstanceTypesResource,
        mock_http: MagicMock,
        method_name: str,
        expected: str,
    ) -> None:
        """Send expected category filters."""
        mock_http.get.return_value = {"instanceTypes": [SAMPLE_INSTANCE_TYPE]}

        if method_name == "list":
            resource.list(category=expected)
        else:
            getattr(resource, method_name)()

        assert mock_http.get.call_args.kwargs["params"]["category"] == expected
