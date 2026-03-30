"""Resource manager for MTN Cloud storage buckets."""

from __future__ import annotations

from typing import Any, Literal

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.models.storage_bucket import (
    StorageBucket,
    StorageBucketCreate,
    StorageBucketUpdate,
)
from mtn_cloud.resources.base import BaseResource


class StorageBucketsResource(BaseResource[StorageBucket]):
    """
    Manage storage buckets and file shares.

    Example:
        bucket = cloud.storage_buckets.create_s3(
            name="my-s3-store",
            bucket_name="my-archive-bucket",
            access_key="AKIA...",
            secret_key="...",
            endpoint="https://ps1csp-s3.ict.mtn.com.ng:9021",
            create_bucket=True,
        )
    """

    _path = "/storage-buckets"
    _model = StorageBucket
    _name = "storage bucket"
    _list_key = "storageBuckets"
    _item_key = "storageBucket"

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        name: str | None = None,
        **filters: Any,
    ) -> list[StorageBucket]:
        """
        List storage buckets.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            sort: Field to sort by
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            name: Filter by name
            **filters: Additional filters

        Returns:
            List of storage buckets
        """
        if name:
            filters["name"] = name

        return super().list(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        )

    def get(self, storage_bucket_id: int) -> StorageBucket:
        """
        Get a storage bucket by ID.

        Args:
            storage_bucket_id: Storage bucket ID

        Returns:
            Storage bucket object
        """
        return super().get(storage_bucket_id)

    def get_by_name(self, name: str) -> StorageBucket:
        """
        Get a storage bucket by name.

        Args:
            name: Storage bucket name

        Returns:
            Storage bucket object

        Raises:
            NotFoundError: If storage bucket is not found
        """
        buckets = self.list(name=name, max_results=1)
        if not buckets:
            raise NotFoundError(
                resource_type="StorageBucket",
                message=f"Storage bucket with name '{name}' not found",
            )
        return buckets[0]

    def create(
        self,
        name: str,
        *,
        bucket_name: str,
        access_key: str,
        secret_key: str,
        endpoint: str,
        storage_server: int | None = None,
        default_backup_target: bool | None = None,
        copy_to_store: bool | None = None,
        default_deployment_target: bool | None = None,
        default_virtual_image_target: bool | None = None,
        retention_policy_type: Literal["backup", "delete", "none"] | None = "none",
        retention_policy_days: int | None = None,
        retention_provider: str | None = None,
        create_bucket: bool = True,
    ) -> StorageBucket:
        """
        Create an S3-compatible storage bucket.

        Args:
            name: Unique storage bucket name
            bucket_name: Backing bucket name
            access_key: Access key
            secret_key: Secret key
            endpoint: S3-compatible endpoint URL
            storage_server: Optional storage server ID
            default_backup_target: Mark as default backup target
            copy_to_store: Archive snapshots to this store
            default_deployment_target: Mark as default deployment target
            default_virtual_image_target: Mark as default virtual image target
            retention_policy_type: Cleanup mode (`backup`, `delete`, `none`)
            retention_policy_days: Days before cleanup
            retention_provider: Backup target store for retention mode `backup`
            create_bucket: Create bucket if missing
        """
        config: dict[str, Any] = {
            "accessKey": access_key,
            "secretKey": secret_key,
            "endpoint": endpoint,
        }

        create_model = StorageBucketCreate(
            name=name,
            bucket_name=bucket_name,
            config=config,
            storage_server=storage_server,
            default_backup_target=default_backup_target,
            copy_to_store=copy_to_store,
            default_deployment_target=default_deployment_target,
            default_virtual_image_target=default_virtual_image_target,
            retention_policy_type=retention_policy_type,
            retention_policy_days=retention_policy_days,
            retention_provider=retention_provider,
            create_bucket=create_bucket,
        )
        return self._create(create_model.to_api_payload())

    def create_s3(
        self,
        name: str,
        *,
        bucket_name: str,
        access_key: str,
        secret_key: str,
        endpoint: str,
        storage_server: int | None = None,
        create_bucket: bool = True,
        default_backup_target: bool | None = None,
        copy_to_store: bool | None = None,
        default_deployment_target: bool | None = None,
        default_virtual_image_target: bool | None = None,
    ) -> StorageBucket:
        """
        Create an S3-compatible storage bucket.

        Args:
            name: Unique storage bucket name
            bucket_name: Backing S3 bucket name
            access_key: Access key
            secret_key: Secret key
            endpoint: S3-compatible endpoint URL
            storage_server: Optional storage server ID
            create_bucket: Create bucket if it does not exist
            default_backup_target: Mark as default backup target
            copy_to_store: Archive snapshots to this store
            default_deployment_target: Mark as default deployment target
            default_virtual_image_target: Mark as default virtual image target
        """
        return self.create(
            name=name,
            bucket_name=bucket_name,
            access_key=access_key,
            secret_key=secret_key,
            endpoint=endpoint,
            storage_server=storage_server,
            default_backup_target=default_backup_target,
            copy_to_store=copy_to_store,
            default_deployment_target=default_deployment_target,
            default_virtual_image_target=default_virtual_image_target,
            create_bucket=create_bucket,
        )

    def update(
        self,
        storage_bucket_id: int,
        *,
        name: str | None = None,
        bucket_name: str | None = None,
        config: dict[str, Any] | None = None,
        default_backup_target: bool | None = None,
        copy_to_store: bool | None = None,
        default_deployment_target: bool | None = None,
        default_virtual_image_target: bool | None = None,
        retention_policy_type: Literal["backup", "delete", "none"] | None = None,
        retention_policy_days: int | None = None,
        retention_provider: str | None = None,
        create_bucket: bool | None = None,
    ) -> StorageBucket:
        """
        Update a storage bucket.

        Args:
            storage_bucket_id: Storage bucket ID
            name: Bucket display name
            bucket_name: Backing bucket name
            config: Provider-specific configuration
            default_backup_target: Mark as default backup target
            copy_to_store: Archive snapshots to this store
            default_deployment_target: Mark as default deployment target
            default_virtual_image_target: Mark as default virtual image target
            retention_policy_type: Cleanup mode (`backup`, `delete`, `none`)
            retention_policy_days: Days before cleanup
            retention_provider: Backup target store for retention mode `backup`
            create_bucket: Create bucket if missing
        """
        update_model = StorageBucketUpdate(
            name=name,
            bucketName=bucket_name,
            config=config,
            defaultBackupTarget=default_backup_target,
            copyToStore=copy_to_store,
            defaultDeploymentTarget=default_deployment_target,
            defaultVirtualImageTarget=default_virtual_image_target,
            retentionPolicyType=retention_policy_type,
            retentionPolicyDays=retention_policy_days,
            retentionProvider=retention_provider,
            createBucket=create_bucket,
        )
        return self._update(storage_bucket_id, update_model.to_api_payload())

    def delete(self, storage_bucket_id: int, *, remove_resources: bool = False) -> bool:
        """
        Delete a storage bucket.

        Args:
            storage_bucket_id: Storage bucket ID
            remove_resources: Permanently delete bucket and files
        """
        params = {"removeResources": True} if remove_resources else None
        return self._delete(storage_bucket_id, params=params)
