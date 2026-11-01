"""Tests for group resources."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.resources.groups import GroupsResource

from .conftest import SAMPLE_GROUP


@pytest.fixture
def resource(mock_http: MagicMock) -> GroupsResource:
    """Return a groups resource backed by a mocked HTTP client."""
    return GroupsResource(mock_http)


class TestGroupsResource:
    """Tests for GroupsResource."""

    @pytest.mark.parametrize(("field", "expected"), [("id", 1), ("name", "MTNNG_CLOUD_AZ_1")])
    def test_list_group_field(
        self,
        resource: GroupsResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse listed group fields."""
        mock_http.get.return_value = {"groups": [SAMPLE_GROUP]}

        assert getattr(resource.list()[0], field) == expected

    def test_list_group_name_filter(self, resource: GroupsResource, mock_http: MagicMock) -> None:
        """Send group name filters as query parameters."""
        mock_http.get.return_value = {"groups": [SAMPLE_GROUP]}

        resource.list(name="MTNNG_CLOUD_AZ_1")

        assert mock_http.get.call_args.kwargs["params"]["name"] == "MTNNG_CLOUD_AZ_1"

    def test_get_group_path(self, resource: GroupsResource, mock_http: MagicMock) -> None:
        """Call the expected group detail endpoint."""
        mock_http.get.return_value = {"group": SAMPLE_GROUP}

        resource.get(1)

        mock_http.get.assert_called_with("/groups/1")

    def test_get_by_name_returns_match(
        self, resource: GroupsResource, mock_http: MagicMock
    ) -> None:
        """Return the first group matching a name."""
        mock_http.get.return_value = {"groups": [SAMPLE_GROUP]}

        assert resource.get_by_name("MTNNG_CLOUD_AZ_1").id == 1

    def test_get_by_name_raises_when_missing(
        self,
        resource: GroupsResource,
        mock_http: MagicMock,
    ) -> None:
        """Raise when a named group cannot be found."""
        mock_http.get.return_value = {"groups": []}

        with pytest.raises(NotFoundError):
            resource.get_by_name("missing")


@pytest.mark.parametrize("body", [{}, {"groups": None}])
def test_list_rejects_missing_or_null_collection(resource, mock_http, body):
    from mtn_cloud.exceptions import MTNCloudError

    mock_http.get.return_value = body
    with pytest.raises(MTNCloudError, match="expected a 'groups' list"):
        resource.list()


def test_pagination_uses_total_when_server_caps_page_size(resource, mock_http):
    mock_http.get.side_effect = [
        {"groups": [{"id": 1}, {"id": 2}], "meta": {"total": 3, "max": 2}},
        {"groups": [{"id": 3}], "meta": {"total": 3, "max": 2}},
    ]
    assert [group.id for group in resource.iter_all(page_size=100)] == [1, 2, 3]
    assert mock_http.get.call_args.kwargs["params"]["offset"] == 2


def test_pagination_rejects_duplicate_ids_before_yielding_page(resource, mock_http):
    from mtn_cloud.exceptions import MTNCloudError

    mock_http.get.return_value = {"groups": [{"id": 1}], "meta": {"total": 2}}
    pages = resource.paginate(page_size=1)
    assert next(pages)[0].id == 1
    with pytest.raises(MTNCloudError, match="Duplicate group IDs.*offset 1"):
        next(pages)
