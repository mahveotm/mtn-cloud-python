"""Tests for virtual image resources."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.resources.virtual_images import VirtualImagesResource

SAMPLE_VIRTUAL_IMAGE = {
    "id": 44,
    "name": "Ubuntu 22.04",
    "imageType": "qcow2",
    "status": "Active",
    "isPublic": True,
    "osType": {"name": "Ubuntu", "code": "ubuntu"},
}


@pytest.fixture
def resource(mock_http: MagicMock) -> VirtualImagesResource:
    """Return a virtual images resource backed by a mocked HTTP client."""
    return VirtualImagesResource(mock_http)


class TestVirtualImagesResource:
    """Tests for VirtualImagesResource."""

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 44),
            ("name", "Ubuntu 22.04"),
            ("image_type", "qcow2"),
            ("is_public", True),
            ("os_name", "Ubuntu"),
            ("os_code", "ubuntu"),
        ],
    )
    def test_list_virtual_image_field(
        self,
        resource: VirtualImagesResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse listed virtual image fields."""
        mock_http.get.return_value = {"virtualImages": [SAMPLE_VIRTUAL_IMAGE]}

        assert getattr(resource.list()[0], field) == expected

    @pytest.mark.parametrize(
        ("kwargs", "param_name", "expected"),
        [
            ({"name": "Ubuntu 22.04"}, "name", "Ubuntu 22.04"),
            ({"image_type": "qcow2"}, "imageType", "qcow2"),
            ({"is_public": True}, "filterType", "public"),
            ({"is_public": False}, "filterType", "private"),
        ],
    )
    def test_list_filter_param(
        self,
        resource: VirtualImagesResource,
        mock_http: MagicMock,
        kwargs: dict[str, Any],
        param_name: str,
        expected: Any,
    ) -> None:
        """Translate virtual image filters to API parameters."""
        mock_http.get.return_value = {"virtualImages": [SAMPLE_VIRTUAL_IMAGE]}

        resource.list(**kwargs)

        assert mock_http.get.call_args.kwargs["params"][param_name] == expected

    def test_get_virtual_image_path(
        self,
        resource: VirtualImagesResource,
        mock_http: MagicMock,
    ) -> None:
        """Call the expected virtual image detail endpoint."""
        mock_http.get.return_value = {"virtualImage": SAMPLE_VIRTUAL_IMAGE}

        resource.get(44)

        mock_http.get.assert_called_with("/virtual-images/44")

    def test_get_by_name_returns_exact_match(
        self,
        resource: VirtualImagesResource,
        mock_http: MagicMock,
    ) -> None:
        """Return the image with an exact name match."""
        mock_http.get.return_value = {"virtualImages": [SAMPLE_VIRTUAL_IMAGE]}

        assert resource.get_by_name("Ubuntu 22.04").id == 44

    def test_get_by_name_raises_when_missing(
        self,
        resource: VirtualImagesResource,
        mock_http: MagicMock,
    ) -> None:
        """Raise when a named virtual image cannot be found."""
        mock_http.get.return_value = {"virtualImages": []}

        with pytest.raises(NotFoundError):
            resource.get_by_name("missing")

    def test_delete_virtual_image(
        self, resource: VirtualImagesResource, mock_http: MagicMock
    ) -> None:
        """Delete a virtual image by ID."""
        mock_http.delete.return_value = {"success": True}

        assert resource.delete(44) is True
        mock_http.delete.assert_called_with("/virtual-images/44", params=None)
