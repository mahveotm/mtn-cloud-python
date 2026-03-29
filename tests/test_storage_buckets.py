"""
Tests for StorageBucket models and resource.
"""

from unittest.mock import MagicMock

from mtn_cloud.models.storage_bucket import (
    StorageBucket,
    StorageBucketCreate,
    StorageBucketUpdate,
)
from mtn_cloud.resources.storage_buckets import StorageBucketsResource

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


class TestStorageBucketModel:
    """Tests for StorageBucket model."""

    def test_parse_storage_bucket(self):
        """Test parsing storage bucket from API response."""
        bucket = StorageBucket.model_validate(SAMPLE_STORAGE_BUCKET)

        assert bucket.id == 334
        assert bucket.name == "cb-s3bucket-1001"
        assert bucket.provider_type == "s3"
        assert bucket.bucket_name == "cb-s3bucket-1001"
        assert bucket.is_s3 is True


class TestStorageBucketPayloadModels:
    """Tests for storage bucket payload models."""

    def test_create_payload(self):
        """Test StorageBucketCreate payload generation."""
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

        assert payload["storageBucket"]["name"] == "my-store"
        assert payload["storageBucket"]["providerType"] == "s3"
        assert payload["storageBucket"]["bucketName"] == "my-bucket"
        assert payload["storageBucket"]["createBucket"] is True
        assert payload["storageBucket"]["config"]["accessKey"] == "AKIA123"

    def test_update_payload(self):
        """Test StorageBucketUpdate payload generation."""
        payload = StorageBucketUpdate(
            name="my-store-updated",
            copyToStore=False,
        ).to_api_payload()

        assert payload["storageBucket"]["name"] == "my-store-updated"
        assert payload["storageBucket"]["copyToStore"] is False
        assert "config" not in payload["storageBucket"]


class TestStorageBucketsResource:
    """Tests for StorageBucketsResource."""

    def test_list_storage_buckets(self):
        """Test listing storage buckets."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"storageBuckets": [SAMPLE_STORAGE_BUCKET]}

        resource = StorageBucketsResource(mock_http)
        buckets = resource.list(name="cb-s3bucket-1001")

        assert len(buckets) == 1
        assert buckets[0].id == 334
        call_args = mock_http.get.call_args
        assert call_args[0][0] == "/storage-buckets"
        assert call_args[1]["params"]["name"] == "cb-s3bucket-1001"

    def test_create_s3_storage_bucket(self):
        """Test creating an S3 storage bucket."""
        mock_http = MagicMock()
        mock_http.post.return_value = {"storageBucket": SAMPLE_STORAGE_BUCKET}

        resource = StorageBucketsResource(mock_http)
        created = resource.create_s3(
            name="my-s3-store",
            bucket_name="cb-s3bucket-1001",
            access_key="AKIA123",
            secret_key="secret",
            endpoint="https://s3.example.com",
            create_bucket=True,
        )

        assert created.id == 334
        call_args = mock_http.post.call_args
        assert call_args[0][0] == "/storage-buckets"
        storage_bucket_payload = call_args[1]["json"]["storageBucket"]
        assert storage_bucket_payload["providerType"] == "s3"
        assert storage_bucket_payload["bucketName"] == "cb-s3bucket-1001"
        assert storage_bucket_payload["config"]["accessKey"] == "AKIA123"
        assert storage_bucket_payload["createBucket"] is True

    def test_update_storage_bucket(self):
        """Test updating a storage bucket."""
        mock_http = MagicMock()
        mock_http.put.return_value = {
            "storageBucket": {**SAMPLE_STORAGE_BUCKET, "name": "updated-storage"},
        }

        resource = StorageBucketsResource(mock_http)
        updated = resource.update(334, name="updated-storage", copy_to_store=False)

        assert updated.id == 334
        assert updated.name == "updated-storage"
        call_args = mock_http.put.call_args
        assert call_args[0][0] == "/storage-buckets/334"
        assert call_args[1]["json"]["storageBucket"]["name"] == "updated-storage"
        assert call_args[1]["json"]["storageBucket"]["copyToStore"] is False

    def test_delete_storage_bucket_with_resources(self):
        """Test deleting a storage bucket with resources."""
        mock_http = MagicMock()
        mock_http.delete.return_value = {"success": True}

        resource = StorageBucketsResource(mock_http)
        deleted = resource.delete(334, remove_resources=True)

        assert deleted is True
        mock_http.delete.assert_called_with(
            "/storage-buckets/334", params={"removeResources": True}
        )
