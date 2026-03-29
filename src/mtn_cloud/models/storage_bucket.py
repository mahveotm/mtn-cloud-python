"""Models for Morpheus storage buckets."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from mtn_cloud.models.base import BaseModel, Resource

S3_PROVIDER_TYPE = "s3"


class StorageServerReference(BaseModel):
    """Simple storage server reference."""

    id: int
    name: str | None = None


class StorageBucket(Resource):
    """Storage bucket or file share."""

    active: bool | None = None
    account_id: int | None = Field(default=None, alias="accountId")
    provider_type: str | None = Field(default=None, alias="providerType")
    storage_server: StorageServerReference | None = Field(default=None, alias="storageServer")
    config: dict[str, Any] | None = None
    bucket_name: str | None = Field(default=None, alias="bucketName")
    read_only: bool | None = Field(default=None, alias="readOnly")
    default_backup_target: bool | None = Field(default=None, alias="defaultBackupTarget")
    default_deployment_target: bool | None = Field(default=None, alias="defaultDeploymentTarget")
    default_virtual_image_target: bool | None = Field(
        default=None, alias="defaultVirtualImageTarget"
    )
    copy_to_store: bool | None = Field(default=None, alias="copyToStore")
    retention_policy_type: str | None = Field(default=None, alias="retentionPolicyType")
    retention_policy_days: int | str | None = Field(default=None, alias="retentionPolicyDays")
    retention_provider: str | None = Field(default=None, alias="retentionProvider")

    @property
    def is_s3(self) -> bool:
        """Return True when this bucket uses S3-compatible provider."""
        return (self.provider_type or "").lower() == S3_PROVIDER_TYPE


class StorageBucketCreate(BaseModel):
    """Create S3-compatible storage bucket payload builder."""

    name: str
    provider_type: Literal["s3"] = Field(default="s3", alias="providerType")
    bucket_name: str = Field(alias="bucketName")
    config: dict[str, Any]
    storage_server: int | None = Field(default=None, alias="storageServer")
    default_backup_target: bool | None = Field(default=None, alias="defaultBackupTarget")
    copy_to_store: bool | None = Field(default=None, alias="copyToStore")
    default_deployment_target: bool | None = Field(default=None, alias="defaultDeploymentTarget")
    default_virtual_image_target: bool | None = Field(
        default=None, alias="defaultVirtualImageTarget"
    )
    retention_policy_type: Literal["backup", "delete", "none"] | None = Field(
        default=None, alias="retentionPolicyType"
    )
    retention_policy_days: int | None = Field(default=None, alias="retentionPolicyDays")
    retention_provider: str | None = Field(default=None, alias="retentionProvider")
    create_bucket: bool | None = Field(default=None, alias="createBucket")

    def to_api_payload(self) -> dict[str, Any]:
        """Convert model to Morpheus API create payload."""
        return {
            "storageBucket": self.model_dump(
                by_alias=True,
                exclude_none=True,
            )
        }


class StorageBucketUpdate(BaseModel):
    """Update S3-compatible storage bucket payload builder."""

    name: str | None = None
    bucket_name: str | None = Field(default=None, alias="bucketName")
    config: dict[str, Any] | None = None
    default_backup_target: bool | None = Field(default=None, alias="defaultBackupTarget")
    copy_to_store: bool | None = Field(default=None, alias="copyToStore")
    default_deployment_target: bool | None = Field(default=None, alias="defaultDeploymentTarget")
    default_virtual_image_target: bool | None = Field(
        default=None, alias="defaultVirtualImageTarget"
    )
    retention_policy_type: Literal["backup", "delete", "none"] | None = Field(
        default=None, alias="retentionPolicyType"
    )
    retention_policy_days: int | None = Field(default=None, alias="retentionPolicyDays")
    retention_provider: str | None = Field(default=None, alias="retentionProvider")
    create_bucket: bool | None = Field(default=None, alias="createBucket")

    def to_api_payload(self) -> dict[str, Any]:
        """Convert model to Morpheus API update payload."""
        return {
            "storageBucket": self.model_dump(
                by_alias=True,
                exclude_none=True,
            )
        }
