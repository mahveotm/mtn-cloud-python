"""Tests for instance models and resources."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from mtn_cloud.models.instance import (
    Instance,
    InstanceCreate,
    InstanceNetwork,
    InstanceUpdate,
    InstanceVolume,
)
from mtn_cloud.resources.instances import InstancesResource

from .conftest import SAMPLE_INSTANCE, SAMPLE_INSTANCES_LIST, nested_value


@pytest.fixture
def resource(mock_http: MagicMock) -> InstancesResource:
    """Return an instances resource backed by a mocked HTTP client."""
    return InstancesResource(mock_http)


@pytest.fixture
def create_kwargs() -> dict[str, Any]:
    """Return valid instance creation arguments."""
    return {
        "name": "MyInstanceName",
        "cloud": "MTNNG_CLOUD_AZ_1",
        "type": "MTN-CS10",
        "group_id": 621,
        "layout": 327,
        "plan": 6923,
        "resource_pool_id": "pool-214",
    }


class TestInstanceModel:
    """Tests for Instance model."""

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 123),
            ("name", "test-instance"),
            ("status", "running"),
            ("ip_address", "192.168.1.100"),
        ],
    )
    def test_parse_instance_field(self, field: str, expected: Any) -> None:
        """Parse API response fields."""
        instance = Instance.model_validate(SAMPLE_INSTANCE)

        assert getattr(instance, field) == expected

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("primary_ip", "192.168.1.100"),
            ("is_running", True),
            ("is_stopped", False),
        ],
    )
    def test_running_instance_property(self, field: str, expected: Any) -> None:
        """Expose computed properties for running instances."""
        instance = Instance.model_validate(SAMPLE_INSTANCE)

        assert getattr(instance, field) == expected

    @pytest.mark.parametrize(
        ("status", "field", "expected"),
        [
            ("stopped", "is_running", False),
            ("stopped", "is_stopped", True),
            ("off", "is_stopped", True),
        ],
    )
    def test_status_property(self, status: str, field: str, expected: bool) -> None:
        """Expose status helpers for stopped variants."""
        instance = Instance.model_validate({**SAMPLE_INSTANCE, "status": status})

        assert getattr(instance, field) is expected

    @pytest.mark.parametrize("expected", ["123", "test-instance"])
    def test_instance_str_contains_identity(self, expected: str) -> None:
        """Include stable identity fields in string output."""
        instance = Instance.model_validate(SAMPLE_INSTANCE)

        assert expected in str(instance)


class TestInstanceCreate:
    """Tests for InstanceCreate model."""

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("instance.name", "MyInstanceName"),
            ("instance.cloud", "MTNNG_CLOUD_AZ_1"),
            ("instance.type", "MTN-CS10"),
            ("instance.instanceType.code", "MTN-CS10"),
            ("instance.site.id", 621),
            ("instance.layout.id", 327),
            ("instance.plan.id", 6923),
            ("config.resourcePoolId", "pool-214"),
        ],
    )
    def test_create_payload_field(
        self,
        create_kwargs: dict[str, Any],
        path: str,
        expected: Any,
    ) -> None:
        """Build required create payload fields."""
        payload = InstanceCreate(**create_kwargs).to_api_payload()

        assert nested_value(payload, path) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("config.resourcePoolId", "pool-214"),
            ("config.availabilityZone", "Lagos-AZ-1-fd1"),
            ("config.securityGroup", "default"),
            ("config.osExternalNetworkId", "public-network-01"),
        ],
    )
    def test_create_payload_config_field(
        self,
        create_kwargs: dict[str, Any],
        path: str,
        expected: Any,
    ) -> None:
        """Build MTN Cloud provisioning config fields."""
        create = InstanceCreate(
            **create_kwargs,
            availability_zone="Lagos-AZ-1-fd1",
            security_group="default",
            os_external_network_id="public-network-01",
        )

        assert nested_value(create.to_api_payload(), path) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("volumes.0.name", "root"),
            ("volumes.0.size", 10),
            ("volumes.0.storageType", 11),
        ],
    )
    def test_create_payload_volume_field(
        self,
        create_kwargs: dict[str, Any],
        path: str,
        expected: Any,
    ) -> None:
        """Build volume payload fields."""
        create = InstanceCreate(
            **create_kwargs,
            volumes=[InstanceVolume(name="root", size=10, storage_type=11)],
        )

        assert nested_value(create.to_api_payload(), path) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("networkInterfaces.0.network.id", "network-298"),
            ("networkInterfaces.0.ipAddress", "192.168.100.40"),
            ("networkInterfaces.0.ipMode", "static"),
        ],
    )
    def test_create_payload_network_field(
        self,
        create_kwargs: dict[str, Any],
        path: str,
        expected: Any,
    ) -> None:
        """Build network interface payload fields."""
        create = InstanceCreate(
            **create_kwargs,
            network_interfaces=[
                InstanceNetwork(network_id="network-298", ip_address="192.168.100.40")
            ],
        )

        assert nested_value(create.to_api_payload(), path) == expected


class TestInstanceUpdate:
    """Tests for InstanceUpdate model."""

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("instance.name", "updated-name"),
            ("instance.description", "Updated description"),
        ],
    )
    def test_update_payload_field(self, path: str, expected: str) -> None:
        """Build update payload fields."""
        update = InstanceUpdate(name="updated-name", description="Updated description")

        assert nested_value(update.to_api_payload(), path) == expected

    def test_update_partial_includes_set_field(self) -> None:
        """Include provided update fields."""
        payload = InstanceUpdate(name="new-name").to_api_payload()

        assert "name" in payload["instance"]

    def test_update_partial_excludes_unset_field(self) -> None:
        """Omit absent update fields."""
        payload = InstanceUpdate(name="new-name").to_api_payload()

        assert "description" not in payload["instance"]


class TestInstancesResource:
    """Tests for InstancesResource."""

    def test_list_instances_count(self, resource: InstancesResource, mock_http: MagicMock) -> None:
        """Return all instances from the list endpoint."""
        mock_http.get.return_value = SAMPLE_INSTANCES_LIST

        assert len(resource.list()) == 2

    @pytest.mark.parametrize(("index", "expected"), [(0, "test-instance"), (1, "test-instance-2")])
    def test_list_instance_name(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
        index: int,
        expected: str,
    ) -> None:
        """Parse listed instance names."""
        mock_http.get.return_value = SAMPLE_INSTANCES_LIST

        assert resource.list()[index].name == expected

    def test_list_uses_get(self, resource: InstancesResource, mock_http: MagicMock) -> None:
        """Call the list endpoint once."""
        mock_http.get.return_value = SAMPLE_INSTANCES_LIST

        resource.list()

        mock_http.get.assert_called_once()

    @pytest.mark.parametrize(("field", "expected"), [("id", 123), ("name", "test-instance")])
    def test_get_instance_field(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Return parsed instance data from the get endpoint."""
        mock_http.get.return_value = {"instance": SAMPLE_INSTANCE}

        assert getattr(resource.get(123), field) == expected

    def test_get_instance_path(self, resource: InstancesResource, mock_http: MagicMock) -> None:
        """Call the expected get endpoint."""
        mock_http.get.return_value = {"instance": SAMPLE_INSTANCE}

        resource.get(123)

        mock_http.get.assert_called_with("/instances/123")

    def test_create_instance_name(self, resource: InstancesResource, mock_http: MagicMock) -> None:
        """Return the created instance."""
        mock_http.post.return_value = {"instance": SAMPLE_INSTANCE}
        mock_http.get.return_value = {"groups": [{"id": 621, "name": "MTNNG_CLOUD_AZ_1"}]}

        instance = resource.create(
            name="MyInstanceName",
            cloud="MTNNG_CLOUD_AZ_1",
            type="MTN-CS10",
            group="MTNNG_CLOUD_AZ_1",
            layout=327,
            plan=6923,
            resource_pool_id="pool-214",
            availability_zone="Lagos-AZ-1-fd1",
            security_group="default",
            os_external_network_id="public-network-01",
        )

        assert instance.name == "test-instance"

    def test_create_instance_posts_once(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
    ) -> None:
        """Post one create request."""
        mock_http.post.return_value = {"instance": SAMPLE_INSTANCE}
        mock_http.get.return_value = {"groups": [{"id": 621, "name": "MTNNG_CLOUD_AZ_1"}]}

        resource.create(
            name="MyInstanceName",
            cloud="MTNNG_CLOUD_AZ_1",
            type="MTN-CS10",
            group="MTNNG_CLOUD_AZ_1",
            layout=327,
            plan=6923,
            resource_pool_id="pool-214",
        )

        mock_http.post.assert_called_once()

    def test_delete_instance_result(
        self, resource: InstancesResource, mock_http: MagicMock
    ) -> None:
        """Return true when deletion succeeds."""
        mock_http.delete.return_value = {"success": True}

        assert resource.delete(123) is True

    def test_delete_instance_uses_delete(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
    ) -> None:
        """Call the delete endpoint."""
        mock_http.delete.return_value = {"success": True}

        resource.delete(123)

        mock_http.delete.assert_called_once()

    @pytest.mark.parametrize(
        ("method_name", "path"),
        [
            ("start", "/instances/123/start"),
            ("stop", "/instances/123/stop"),
            ("restart", "/instances/123/restart"),
        ],
    )
    def test_instance_action_path(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
        method_name: str,
        path: str,
    ) -> None:
        """Call the expected action endpoint."""
        mock_http.put.return_value = {"success": True}
        mock_http.get.return_value = {"instance": SAMPLE_INSTANCE}

        getattr(resource, method_name)(123)

        mock_http.put.assert_called_with(path)

    def test_start_instance_returns_refreshed_instance(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
    ) -> None:
        """Return the refreshed instance after starting."""
        mock_http.put.return_value = {"success": True}
        mock_http.get.return_value = {"instance": SAMPLE_INSTANCE}

        assert resource.start(123).id == 123

    @pytest.mark.parametrize(
        ("filter_name", "filter_value", "param_name", "expected"),
        [
            ("status", "running", "status", "running"),
            ("cloud_id", 1, "zoneId", 1),
            ("group_id", 621, "siteId", 621),
            ("labels", ["prod", "api"], "labels", "prod,api"),
        ],
    )
    def test_list_filter_param(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
        filter_name: str,
        filter_value: Any,
        param_name: str,
        expected: Any,
    ) -> None:
        """Translate resource filters to API query parameters."""
        mock_http.get.return_value = SAMPLE_INSTANCES_LIST

        resource.list(**{filter_name: filter_value})

        assert mock_http.get.call_args.kwargs["params"][param_name] == expected

    def test_paginate_page_lengths(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
    ) -> None:
        """Yield pages until a partial page is returned."""
        self._mock_paginated_instances(mock_http)

        pages = list(resource.paginate(page_size=2))

        assert [len(page) for page in pages] == [2, 2, 1]

    def test_paginate_first_item_ids(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
    ) -> None:
        """Preserve item ordering across pages."""
        self._mock_paginated_instances(mock_http)

        pages = list(resource.paginate(page_size=2))

        assert [page[0].id for page in pages] == [123, 125, 127]

    @pytest.mark.parametrize(
        ("call_index", "param_name", "expected"),
        [
            (0, "max", 2),
            (1, "offset", 2),
            (2, "offset", 4),
        ],
    )
    def test_paginate_request_param(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
        call_index: int,
        param_name: str,
        expected: int,
    ) -> None:
        """Send expected pagination parameters."""
        self._mock_paginated_instances(mock_http)

        list(resource.paginate(page_size=2))

        assert mock_http.get.call_args_list[call_index].kwargs["params"][param_name] == expected

    def test_paginate_first_request_omits_offset(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
    ) -> None:
        """Omit offset from the first pagination request."""
        self._mock_paginated_instances(mock_http)

        list(resource.paginate(page_size=2))

        assert "offset" not in mock_http.get.call_args_list[0].kwargs["params"]

    def test_iter_all_instances_count(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
    ) -> None:
        """Flatten a page into individual instances."""
        mock_http.get.return_value = SAMPLE_INSTANCES_LIST

        assert len(list(resource.iter_all(page_size=5, status="running", cloud_id=1))) == 2

    @pytest.mark.parametrize(("index", "expected"), [(0, 123), (1, 124)])
    def test_iter_all_instance_id(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
        index: int,
        expected: int,
    ) -> None:
        """Yield parsed instances from flattened iteration."""
        mock_http.get.return_value = SAMPLE_INSTANCES_LIST

        assert list(resource.iter_all(page_size=5))[index].id == expected

    @pytest.mark.parametrize(
        ("param_name", "expected"),
        [
            ("max", 5),
            ("status", "running"),
            ("zoneId", 1),
        ],
    )
    def test_iter_all_request_param(
        self,
        resource: InstancesResource,
        mock_http: MagicMock,
        param_name: str,
        expected: Any,
    ) -> None:
        """Pass filters through flattened iteration."""
        mock_http.get.return_value = SAMPLE_INSTANCES_LIST

        list(resource.iter_all(page_size=5, status="running", cloud_id=1))

        assert mock_http.get.call_args.kwargs["params"][param_name] == expected

    @pytest.mark.parametrize(
        ("kwargs", "message"),
        [
            ({"page_size": 0}, "page_size must be >= 1"),
            ({"start_offset": -1}, "start_offset must be >= 0"),
        ],
    )
    def test_paginate_validation(self, kwargs: dict[str, int], message: str) -> None:
        """Validate pagination arguments."""
        resource = InstancesResource(MagicMock())

        with pytest.raises(ValueError, match=message):
            list(resource.paginate(**kwargs))

    @staticmethod
    def _mock_paginated_instances(mock_http: MagicMock) -> None:
        pages = {
            0: SAMPLE_INSTANCES_LIST,
            2: {
                "instances": [
                    {
                        "id": 125,
                        "name": "test-instance-3",
                        "status": "running",
                        "ipAddress": "192.168.1.102",
                    },
                    {
                        "id": 126,
                        "name": "test-instance-4",
                        "status": "running",
                        "ipAddress": "192.168.1.103",
                    },
                ]
            },
            4: {
                "instances": [
                    {
                        "id": 127,
                        "name": "test-instance-5",
                        "status": "stopped",
                        "ipAddress": "192.168.1.104",
                    }
                ]
            },
        }

        def get_side_effect(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
            if path != "/instances":
                raise AssertionError(f"Unexpected path: {path}")
            offset = (params or {}).get("offset", 0)
            return pages.get(offset, {"instances": []})

        mock_http.get.side_effect = get_side_effect
