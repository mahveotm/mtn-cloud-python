"""Tests for service plan resources."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.resources.plans import PlansResource

SAMPLE_PLAN = {
    "id": 6923,
    "name": "Small",
    "code": "small",
    "maxCores": 2,
    "maxMemory": 4 * 1024 * 1024 * 1024,
    "maxStorage": 40 * 1024 * 1024 * 1024,
    "active": True,
}


@pytest.fixture
def resource(mock_http: MagicMock) -> PlansResource:
    """Return a plans resource backed by a mocked HTTP client."""
    return PlansResource(mock_http)


class TestPlansResource:
    """Tests for PlansResource."""

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 6923),
            ("name", "Small"),
            ("cores", 2),
            ("memory_gb", 4),
            ("storage_gb", 40),
        ],
    )
    def test_list_plan_field(
        self,
        resource: PlansResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse listed plan fields."""
        mock_http.get.return_value = {"servicePlans": [SAMPLE_PLAN]}

        assert getattr(resource.list()[0], field) == expected

    def test_list_plan_name_filter(self, resource: PlansResource, mock_http: MagicMock) -> None:
        """Send plan name filters as query parameters."""
        mock_http.get.return_value = {"servicePlans": [SAMPLE_PLAN]}

        resource.list(name="Small")

        assert mock_http.get.call_args.kwargs["params"]["name"] == "Small"

    def test_get_plan_path(self, resource: PlansResource, mock_http: MagicMock) -> None:
        """Call the expected plan detail endpoint."""
        mock_http.get.return_value = {"servicePlan": SAMPLE_PLAN}

        resource.get(6923)

        mock_http.get.assert_called_with("/service-plans/6923")

    def test_get_by_name_returns_match(self, resource: PlansResource, mock_http: MagicMock) -> None:
        """Return the first plan matching a name."""
        mock_http.get.return_value = {"servicePlans": [SAMPLE_PLAN]}

        assert resource.get_by_name("Small").id == 6923

    def test_get_by_name_raises_when_missing(
        self,
        resource: PlansResource,
        mock_http: MagicMock,
    ) -> None:
        """Raise when a named plan cannot be found."""
        mock_http.get.return_value = {"servicePlans": []}

        with pytest.raises(NotFoundError):
            resource.get_by_name("missing")

    @pytest.mark.parametrize(
        ("kwargs", "expected"),
        [
            ({"cores": 2}, 6923),
            ({"memory_gb": 4}, 6923),
            ({"storage_gb": 40}, 6923),
            ({"cores": 8}, None),
        ],
    )
    def test_find_plan(
        self,
        resource: PlansResource,
        mock_http: MagicMock,
        kwargs: dict[str, Any],
        expected: int | None,
    ) -> None:
        """Find the first plan satisfying resource requirements."""
        mock_http.get.return_value = {"servicePlans": [SAMPLE_PLAN]}

        plan = resource.find(**kwargs)

        assert (plan.id if plan else None) == expected
