"""Archive-related models for buckets, files, and upload summaries."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import Field

from mtn_cloud.models.base import BaseModel, Resource


class ArchiveBucketVisibility(str, Enum):
    """Archive bucket visibility values."""

    PUBLIC = "public"
    PRIVATE = "private"


class ArchiveReference(BaseModel):
    """Simple id/name reference used by archive resources."""

    id: int
    name: str | None = None


class ArchiveUserReference(BaseModel):
    """Simple username reference."""

    username: str | None = None


class ArchiveFileBucketReference(ArchiveReference):
    """Archive bucket reference included in archive file payloads."""

    is_public: bool | None = Field(default=None, alias="isPublic")


class ArchiveBucket(Resource):
    """Archive bucket."""

    description: str | None = None
    storage_provider: ArchiveReference | None = Field(default=None, alias="storageProvider")
    owner: ArchiveReference | None = None
    created_by: ArchiveUserReference | None = Field(default=None, alias="createdBy")
    is_public: bool | None = Field(default=None, alias="isPublic")
    visibility: str | None = None
    code: str | None = None
    file_path: str | None = Field(default=None, alias="filePath")
    raw_size: int | None = Field(default=None, alias="rawSize")
    file_count: int | None = Field(default=None, alias="fileCount")
    accounts: list[ArchiveReference] = Field(default_factory=list)


class ArchiveFile(Resource):
    """Archive file entry."""

    file_path: str | None = Field(default=None, alias="filePath")
    archive_bucket: ArchiveFileBucketReference | None = Field(default=None, alias="archiveBucket")
    created_by: ArchiveUserReference | None = Field(default=None, alias="createdBy")
    is_directory: bool | None = Field(default=None, alias="isDirectory")
    status: str | None = None
    raw_size: int | None = Field(default=None, alias="rawSize")
    content_type: str | None = Field(default=None, alias="contentType")
    download_count: int | None = Field(default=None, alias="downloadCount")


class ArchiveDirectoryUploadFailure(BaseModel):
    """Details about a file that failed during directory upload."""

    local_path: str
    remote_path: str
    reason: str
    error_type: str


class ArchiveDirectorySkippedFile(BaseModel):
    """Details about a file skipped during preflight validation."""

    local_path: str
    remote_path: str
    reason: str
    error_type: str


class ArchiveDirectoryUploadResult(BaseModel):
    """Two-phase summary result for directory uploads."""

    scanned: int = 0
    eligible: int = 0
    skipped: int = 0
    uploaded: int = 0
    failed: int = 0
    dry_run: bool = False
    strict: bool = False
    aborted: bool = False
    uploaded_files: list[ArchiveFile] = Field(default_factory=list)
    skipped_files: list[ArchiveDirectorySkippedFile] = Field(default_factory=list)
    failed_files: list[ArchiveDirectoryUploadFailure] = Field(default_factory=list)

    @property
    def uploaded_count(self) -> int:
        """Number of files uploaded successfully."""
        return self.uploaded

    @property
    def failed_count(self) -> int:
        """Number of files that failed during upload."""
        return self.failed

    @property
    def skipped_count(self) -> int:
        """Number of files skipped before upload (preflight failures)."""
        return self.skipped

    @property
    def scanned_count(self) -> int:
        """Number of files discovered during directory scan."""
        return self.scanned

    @property
    def eligible_count(self) -> int:
        """Number of files eligible for upload after preflight validation."""
        return self.eligible

    @property
    def total_count(self) -> int:
        """Total number of files processed."""
        return self.scanned

    @property
    def has_failures(self) -> bool:
        """Whether any file failed validation or upload."""
        return self.failed > 0 or self.skipped > 0


class ArchiveBucketCreate(BaseModel):
    """Create archive bucket payload builder."""

    name: str
    storage_provider_id: int
    description: str | None = None
    visibility: ArchiveBucketVisibility | Literal["public", "private"] | None = None
    is_public: bool | None = Field(default=None, alias="isPublic")
    account_id: int | None = None

    def to_api_payload(self) -> dict[str, Any]:
        """Convert model to Morpheus API create payload."""
        archive_bucket: dict[str, Any] = {
            "name": self.name,
            "storageProvider": {"id": self.storage_provider_id},
        }

        if self.description is not None:
            archive_bucket["description"] = self.description
        if self.visibility is not None:
            archive_bucket["visibility"] = self.visibility
        if self.is_public is not None:
            archive_bucket["isPublic"] = self.is_public
        if self.account_id is not None:
            archive_bucket["accounts"] = {"id": self.account_id}

        return {"archiveBucket": archive_bucket}


class ArchiveBucketUpdate(BaseModel):
    """Update archive bucket payload builder."""

    name: str | None = None
    description: str | None = None
    visibility: ArchiveBucketVisibility | Literal["public", "private"] | None = None
    is_public: bool | None = Field(default=None, alias="isPublic")
    account_id: int | None = None

    def to_api_payload(self) -> dict[str, Any]:
        """Convert model to Morpheus API update payload."""
        archive_bucket: dict[str, Any] = {}

        if self.name is not None:
            archive_bucket["name"] = self.name
        if self.description is not None:
            archive_bucket["description"] = self.description
        if self.visibility is not None:
            archive_bucket["visibility"] = self.visibility
        if self.is_public is not None:
            archive_bucket["isPublic"] = self.is_public
        if self.account_id is not None:
            archive_bucket["accounts"] = {"id": self.account_id}

        return {"archiveBucket": archive_bucket}
