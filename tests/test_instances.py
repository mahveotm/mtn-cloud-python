"""
Tests for Instance models and resource.
"""

import pytest
from unittest.mock import MagicMock, patch

from mtn_cloud.models.instance import (
    Instance,
    InstanceCreate,
    InstanceUpdate,
    InstanceConfig,
    InstanceVolume,
    InstanceNetwork,
)
from mtn_cloud.resources.instances import InstancesResource

from conftest import SAMPLE_INSTANCE, SAMPLE_INSTANCES_LIST


class TestInstanceModel:
    """Tests for Instance model."""

    def test_parse_instance(self):
        """Test parsing instance from API response."""
        instance = Instance.model_validate(SAMPLE_INSTANCE)

        assert instance.id == 123
        assert instance.name == "test-instance"
        assert instance.status == "running"
        assert instance.ip_address == "192.168.1.100"

    def test_instance_properties(self):
        """Test instance computed properties."""
        instance = Instance.model_validate(SAMPLE_INSTANCE)

        assert instance.primary_ip == "192.168.1.100"
        assert instance.is_running is True
        assert instance.is_stopped is False

    def test_instance_stopped(self):
        """Test stopped instance properties."""
        data = {**SAMPLE_INSTANCE, "status": "stopped"}
        instance = Instance.model_validate(data)

        assert instance.is_running is False
        assert instance.is_stopped is True

    def test_instance_str(self):
        """Test instance string representation."""
        instance = Instance.model_validate(SAMPLE_INSTANCE)
        assert "123" in str(instance)
        assert "test-instance" in str(instance)


class TestInstanceCreate:
    """Tests for InstanceCreate model."""

    def test_create_payload(self):
        """Test converting create model to API payload."""
        create = InstanceCreate(
            name="new-instance",
            cloud_id=1,
            group_id=1,
            instance_type_code="MTN-CS10",
            layout_id=327,
            plan_id=6923,
        )

        payload = create.to_api_payload()

        assert payload["instance"]["name"] == "new-instance"
        assert payload["zoneId"] == 1
        assert payload["instance"]["instanceType"]["code"] == "MTN-CS10"
        assert payload["instance"]["layout"]["id"] == 327
        assert payload["instance"]["plan"]["id"] == 6923

    def test_create_with_config(self):
        """Test create payload with config."""
        config = InstanceConfig(
            resource_pool_id="pool-214",
            availability_zone="Lagos-AZ-1",
        )
        create = InstanceCreate(
            name="new-instance",
            cloud_id=1,
            group_id=1,
            instance_type_code="MTN-CS10",
            layout_id=327,
            plan_id=6923,
            config=config,
        )

        payload = create.to_api_payload()

        assert "config" in payload["instance"]
        assert payload["instance"]["config"]["resourcePoolId"] == "pool-214"

    def test_create_with_volumes(self):
        """Test create payload with volumes."""
        volumes = [InstanceVolume(name="root", size=20)]
        create = InstanceCreate(
            name="new-instance",
            cloud_id=1,
            group_id=1,
            instance_type_code="MTN-CS10",
            layout_id=327,
            plan_id=6923,
            volumes=volumes,
        )

        payload = create.to_api_payload()

        assert "volumes" in payload
        assert payload["volumes"][0]["name"] == "root"
        assert payload["volumes"][0]["size"] == 20


class TestInstanceUpdate:
    """Tests for InstanceUpdate model."""

    def test_update_payload(self):
        """Test converting update model to API payload."""
        update = InstanceUpdate(
            name="updated-name",
            description="Updated description",
        )

        payload = update.to_api_payload()

        assert payload["instance"]["name"] == "updated-name"
        assert payload["instance"]["description"] == "Updated description"

    def test_update_partial(self):
        """Test partial update only includes set fields."""
        update = InstanceUpdate(name="new-name")

        payload = update.to_api_payload()

        assert "name" in payload["instance"]
        assert "description" not in payload["instance"]


class TestInstancesResource:
    """Tests for InstancesResource."""

    def test_list_instances(self):
        """Test listing instances."""
        mock_http = MagicMock()
        mock_http.get.return_value = SAMPLE_INSTANCES_LIST

        resource = InstancesResource(mock_http)
        instances = resource.list()

        assert len(instances) == 2
        assert instances[0].name == "test-instance"
        assert instances[1].name == "test-instance-2"
        mock_http.get.assert_called_once()

    def test_get_instance(self):
        """Test getting single instance."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"instance": SAMPLE_INSTANCE}

        resource = InstancesResource(mock_http)
        instance = resource.get(123)

        assert instance.id == 123
        assert instance.name == "test-instance"
        mock_http.get.assert_called_with("/instances/123")

    def test_create_instance(self):
        """Test creating instance."""
        mock_http = MagicMock()
        mock_http.post.return_value = {"instance": SAMPLE_INSTANCE}

        resource = InstancesResource(mock_http)
        instance = resource.create(
            name="test-instance",
            cloud_id=1,
            group_id=1,
            instance_type_code="MTN-CS10",
            layout_id=327,
            plan_id=6923,
        )

        assert instance.name == "test-instance"
        mock_http.post.assert_called_once()

    def test_delete_instance(self):
        """Test deleting instance."""
        mock_http = MagicMock()
        mock_http.delete.return_value = {"success": True}

        resource = InstancesResource(mock_http)
        result = resource.delete(123)

        assert result is True
        mock_http.delete.assert_called_once()

    def test_start_instance(self):
        """Test starting instance."""
        mock_http = MagicMock()
        mock_http.put.return_value = {"success": True}
        mock_http.get.return_value = {"instance": SAMPLE_INSTANCE}

        resource = InstancesResource(mock_http)
        instance = resource.start(123)

        mock_http.put.assert_called_with("/instances/123/start")
        assert instance.id == 123

    def test_stop_instance(self):
        """Test stopping instance."""
        mock_http = MagicMock()
        mock_http.put.return_value = {"success": True}
        mock_http.get.return_value = {"instance": {**SAMPLE_INSTANCE, "status": "stopped"}}

        resource = InstancesResource(mock_http)
        instance = resource.stop(123)

        mock_http.put.assert_called_with("/instances/123/stop")

    def test_restart_instance(self):
        """Test restarting instance."""
        mock_http = MagicMock()
        mock_http.put.return_value = {"success": True}
        mock_http.get.return_value = {"instance": SAMPLE_INSTANCE}

        resource = InstancesResource(mock_http)
        instance = resource.restart(123)

        mock_http.put.assert_called_with("/instances/123/restart")

    def test_list_with_filters(self):
        """Test listing instances with filters."""
        mock_http = MagicMock()
        mock_http.get.return_value = SAMPLE_INSTANCES_LIST

        resource = InstancesResource(mock_http)
        instances = resource.list(status="running", cloud_id=1)

        call_args = mock_http.get.call_args
        params = call_args[1]["params"]
        assert params["status"] == "running"
        assert params["zoneId"] == 1

