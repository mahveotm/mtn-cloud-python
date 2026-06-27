"""Tests for storage bucket models and resources."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from mtn_cloud.models.storage_bucket import (
    StorageBucket,
    StorageBucketCreate,
    StorageBucketUpdate,
)
from mtn_cloud.resources.storage_buckets import StorageBucketsResource

from .conftest import nested_value

SAMPLE_STORAGE_BUCKET = {
    "id": 334,
    "name": "cb-s3bucket-1001",
    "active": True,
    "accountId": 1,
    "providerType": "s3",
    "storageServer": None,
    "config": {
        "accessKey": "AKIAxxxx",
        "secretKey": "********",
        "endpoint": "https://ps1csp-s3.ict.mtn.com.ng:9021",
    },
    "bucketName": "cb-s3bucket-1001",
    "readOnly": False,
    "defaultBackupTarget": False,
    "defaultDeploymentTarget": False,
    "defaultVirtualImageTarget": False,
    "copyToStore": True,
}


@pytest.fixture
def resource(mock_http: MagicMock) -> StorageBucketsResource:
    """Return a storage buckets resource backed by a mocked HTTP client."""
    return StorageBucketsResource(mock_http)


class TestStorageBucketModel:
    """Tests for StorageBucket model."""

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 334),
            ("name", "cb-s3bucket-1001"),
            ("provider_type", "s3"),
            ("bucket_name", "cb-s3bucket-1001"),
            ("is_s3", True),
        ],
    )
    def test_parse_storage_bucket_field(self, field: str, expected: Any) -> None:
        """Parse storage bucket fields."""
        bucket = StorageBucket.model_validate(SAMPLE_STORAGE_BUCKET)

        assert getattr(bucket, field) == expected


class TestStorageBucketPayloadModels:
    """Tests for storage bucket payload models."""

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("storageBucket.name", "my-store"),
            ("storageBucket.providerType", "s3"),
            ("storageBucket.bucketName", "my-bucket"),
            ("storageBucket.createBucket", True),
            ("storageBucket.config.accessKey", "AKIA123"),
        ],
    )
    def test_create_payload_field(self, path: str, expected: Any) -> None:
        """Build create payload fields."""
        payload = StorageBucketCreate(
            name="my-store",
            bucketName="my-bucket",
            config={
                "accessKey": "AKIA123",
                "secretKey": "secret",
                "endpoint": "https://s3.example.com",
            },
            createBucket=True,
        ).to_api_payload()

        assert nested_value(payload, path) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("storageBucket.name", "my-store-updated"),
            ("storageBucket.copyToStore", False),
        ],
    )
    def test_update_payload_field(self, path: str, expected: Any) -> None:
        """Build update payload fields."""
        payload = StorageBucketUpdate(
            name="my-store-updated",
            copyToStore=False,
        ).to_api_payload()

        assert nested_value(payload, path) == expected

    def test_update_payload_omits_config(self) -> None:
        """Omit unset config from update payloads."""
        payload = StorageBucketUpdate(name="my-store-updated").to_api_payload()

        assert "config" not in payload["storageBucket"]


class TestStorageBucketsResource:
    """Tests for StorageBucketsResource."""

    def test_list_storage_bucket_count(
        self,
        resource: StorageBucketsResource,
        mock_http: MagicMock,
    ) -> None:
        """Return matching storage buckets."""
        mock_http.get.return_value = {"storageBuckets": [SAMPLE_STORAGE_BUCKET]}

        assert len(resource.list(name="cb-s3bucket-1001")) == 1

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("args.0", "/storage-buckets"),
            ("kwargs.params.name", "cb-s3bucket-1001"),
        ],
    )
    def test_list_request(
        self,
        resource: StorageBucketsResource,
        mock_http: MagicMock,
        path: str,
        expected: Any,
    ) -> None:
        """Send expected storage bucket list request."""
        mock_http.get.return_value = {"storageBuckets": [SAMPLE_STORAGE_BUCKET]}

        resource.list(name="cb-s3bucket-1001")

        assert nested_value(_call_data(mock_http.get.call_args), path) == expected

    def test_create_s3_storage_bucket_id(
        self,
        resource: StorageBucketsResource,
        mock_http: MagicMock,
    ) -> None:
        """Return the created storage bucket."""
        mock_http.post.return_value = {"storageBucket": SAMPLE_STORAGE_BUCKET}

        assert self._create_s3(resource).id == 334

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("args.0", "/storage-buckets"),
            ("kwargs.json.storageBucket.providerType", "s3"),
            ("kwargs.json.storageBucket.bucketName", "cb-s3bucket-1001"),
            ("kwargs.json.storageBucket.config.accessKey", "AKIA123"),
            ("kwargs.json.storageBucket.createBucket", True),
        ],
    )
    def test_create_s3_request(
        self,
        resource: StorageBucketsResource,
        mock_http: MagicMock,
        path: str,
        expected: Any,
    ) -> None:
        """Send expected S3 storage bucket create request."""
        mock_http.post.return_value = {"storageBucket": SAMPLE_STORAGE_BUCKET}

        self._create_s3(resource)

        assert nested_value(_call_data(mock_http.post.call_args), path) == expected

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 334),
            ("name", "updated-storage"),
        ],
    )
    def test_update_storage_bucket_field(
        self,
        resource: StorageBucketsResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Return the updated storage bucket."""
        mock_http.put.return_value = {
            "storageBucket": {**SAMPLE_STORAGE_BUCKET, "name": "updated-storage"},
        }

        updated = resource.update(334, name="updated-storage", copy_to_store=False)

        assert getattr(updated, field) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("args.0", "/storage-buckets/334"),
            ("kwargs.json.storageBucket.name", "updated-storage"),
            ("kwargs.json.storageBucket.copyToStore", False),
        ],
    )
    def test_update_storage_bucket_request(
        self,
        resource: StorageBucketsResource,
        mock_http: MagicMock,
        path: str,
        expected: Any,
    ) -> None:
        """Send expected storage bucket update request."""
        mock_http.put.return_value = {
            "storageBucket": {**SAMPLE_STORAGE_BUCKET, "name": "updated-storage"},
        }

        resource.update(334, name="updated-storage", copy_to_store=False)

        assert nested_value(_call_data(mock_http.put.call_args), path) == expected

    def test_delete_storage_bucket_with_resources(
        self,
        resource: StorageBucketsResource,
        mock_http: MagicMock,
    ) -> None:
        """Pass resource-removal intent to delete requests."""
        mock_http.delete.return_value = {"success": True}

        assert resource.delete(334, remove_resources=True) is True
        mock_http.delete.assert_called_with(
            "/storage-buckets/334", params={"removeResources": True}
        )

    @staticmethod
    def _create_s3(resource: StorageBucketsResource) -> StorageBucket:
        return resource.create_s3(
            name="my-s3-store",
            bucket_name="cb-s3bucket-1001",
            access_key="AKIA123",
            secret_key="secret",
            endpoint="https://s3.example.com",
            create_bucket=True,
        )


def _call_data(call_args: Any) -> dict[str, Any]:
    return {"args": list(call_args.args), "kwargs": call_args.kwargs}
