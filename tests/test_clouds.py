"""Tests for cloud resources."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from mtn_cloud.resources.clouds import CloudsResource

from .conftest import SAMPLE_CLOUD


@pytest.fixture
def resource(mock_http: MagicMock) -> CloudsResource:
    """Return a clouds resource backed by a mocked HTTP client."""
    return CloudsResource(mock_http)


class TestCloudsResource:
    """Tests for CloudsResource."""

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 1),
            ("name", "MTNNG_CLOUD_AZ_1"),
            ("type_code", "openstack"),
        ],
    )
    def test_list_cloud_field(
        self,
        resource: CloudsResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse listed cloud fields."""
        mock_http.get.return_value = {"zones": [SAMPLE_CLOUD]}

        assert getattr(resource.list()[0], field) == expected

    def test_list_cloud_count(self, resource: CloudsResource, mock_http: MagicMock) -> None:
        """Return all clouds from the list endpoint."""
        mock_http.get.return_value = {"zones": [SAMPLE_CLOUD]}

        assert len(resource.list()) == 1

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("args.0", "/zones"),
            ("kwargs.params.type", "openstack"),
        ],
    )
    def test_list_openstack_request(
        self,
        resource: CloudsResource,
        mock_http: MagicMock,
        path: str,
        expected: Any,
    ) -> None:
        """Filter cloud list requests to OpenStack clouds."""
        mock_http.get.return_value = {"zones": [SAMPLE_CLOUD]}

        resource.list_openstack()

        call_args = {
            "args": mock_http.get.call_args.args,
            "kwargs": mock_http.get.call_args.kwargs,
        }
        assert self._nested_value(call_args, path) == expected

    @pytest.mark.parametrize(("field", "expected"), [("id", 1), ("type_code", "openstack")])
    def test_get_cloud_field(
        self,
        resource: CloudsResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse a fetched cloud."""
        mock_http.get.return_value = {"zone": SAMPLE_CLOUD}

        assert getattr(resource.get(1), field) == expected

    def test_get_cloud_path(self, resource: CloudsResource, mock_http: MagicMock) -> None:
        """Call the expected cloud detail endpoint."""
        mock_http.get.return_value = {"zone": SAMPLE_CLOUD}

        resource.get(1)

        mock_http.get.assert_called_with("/zones/1")

    @staticmethod
    def _nested_value(data: dict[str, Any], path: str) -> Any:
        value: Any = data
        for key in path.split("."):
            if isinstance(value, tuple):
                value = value[int(key)]
            else:
                value = value[key]
        return value
