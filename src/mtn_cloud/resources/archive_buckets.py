"""Resource manager for MTN Cloud archive buckets and files."""

from __future__ import annotations

import os
import tempfile
from builtins import list as builtin_list
from pathlib import Path
from typing import Any
from urllib.parse import quote

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.models.archive import (
    ArchiveBucket,
    ArchiveBucketCreate,
    ArchiveBucketUpdate,
    ArchiveBucketVisibility,
    ArchiveDirectorySkippedFile,
    ArchiveDirectoryUploadFailure,
    ArchiveDirectoryUploadResult,
    ArchiveFile,
)
from mtn_cloud.resources.base import BaseResource


class ArchiveBucketsResource(BaseResource[ArchiveBucket]):
    """
    Manage archive buckets and files.

    Example:
        archive_bucket = cloud.archive_buckets.create(
            name="my-archive",
            storage_provider_id=bucket.id,
        )

        cloud.archive_buckets.upload_file(
            bucket_name=archive_bucket.name,
            remote_path="/",
            local_path="./backup.sql",
        )
    """

    _path = "/archives/buckets"
    _model = ArchiveBucket
    _name = "archive bucket"
    _list_key = "archiveBuckets"
    _item_key = "archiveBucket"

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        name: str | None = None,
        **filters: Any,
    ) -> list[ArchiveBucket]:
        """
        List archive buckets.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            sort: Field to sort by
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            name: Filter by name
            **filters: Additional filters

        Returns:
            List of archive buckets
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

    def get(self, archive_bucket_id: int) -> ArchiveBucket:
        """
        Get an archive bucket by ID.

        Args:
            archive_bucket_id: Archive bucket ID
        """
        return super().get(archive_bucket_id)

    def get_by_name(self, name: str) -> ArchiveBucket:
        """
        Get an archive bucket by name.

        Args:
            name: Archive bucket name
        """
        buckets = self.list(name=name, max_results=1)
        if not buckets:
            raise NotFoundError(
                resource_type="ArchiveBucket",
                message=f"Archive bucket with name '{name}' not found",
            )
        return buckets[0]

    def create(
        self,
        name: str,
        *,
        storage_provider_id: int,
        description: str | None = None,
        visibility: ArchiveBucketVisibility | str = ArchiveBucketVisibility.PRIVATE,
        is_public: bool = False,
        account_id: int | None = None,
    ) -> ArchiveBucket:
        """
        Create an archive bucket.

        Args:
            name: Archive bucket name (must be globally unique)
            storage_provider_id: Storage provider ID (storage bucket ID)
            description: Optional description
            visibility: Archive visibility (`private` or `public`)
            is_public: Enable anonymous public download URL
            account_id: Optional tenant account ID
        """
        create_model = ArchiveBucketCreate(
            name=name,
            storage_provider_id=storage_provider_id,
            description=description,
            visibility=visibility,
            isPublic=is_public,
            account_id=account_id,
        )
        return self._create(create_model.to_api_payload())

    def update(
        self,
        archive_bucket_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
        visibility: ArchiveBucketVisibility | str | None = None,
        is_public: bool | None = None,
        account_id: int | None = None,
    ) -> ArchiveBucket:
        """
        Update an archive bucket.

        Args:
            archive_bucket_id: Archive bucket ID
            name: Archive bucket name
            description: Description
            visibility: Archive visibility (`private` or `public`)
            is_public: Enable/disable anonymous public download URL
            account_id: Optional tenant account ID
        """
        update_model = ArchiveBucketUpdate(
            name=name,
            description=description,
            visibility=visibility,
            isPublic=is_public,
            account_id=account_id,
        )
        return self._update(archive_bucket_id, update_model.to_api_payload())

    def delete(self, archive_bucket_id: int) -> bool:
        """
        Delete an archive bucket.

        Args:
            archive_bucket_id: Archive bucket ID
        """
        return self._delete(archive_bucket_id)

    def list_files(
        self,
        *,
        bucket_name: str,
        remote_path: str | None = None,
        name: str | None = None,
        phrase: str | None = None,
        full_tree: bool | None = None,
    ) -> builtin_list[ArchiveFile]:
        """
        List files in an archive bucket path.

        Args:
            bucket_name: Archive bucket name (not storage bucket/provider name)
            remote_path: Path inside the archive bucket to list
            name: Exact file name filter
            phrase: Wildcard search phrase
            full_tree: Include subdirectories
        """
        path = self._files_path(bucket_name=bucket_name, remote_path=remote_path or "/")
        params: dict[str, Any] = {}
        if name:
            params["name"] = name
        if phrase:
            params["phrase"] = phrase
        if full_tree is not None:
            params["fullTree"] = full_tree

        response = self._http.get(path, params=params or None)
        files = response.get("archiveFiles", [])
        return [ArchiveFile.model_validate(item) for item in files]

    def upload_file(
        self,
        *,
        bucket_name: str,
        remote_path: str,
        local_path: str | Path,
        filename: str | None = None,
    ) -> ArchiveFile:
        """
        Upload a file to an archive bucket path.

        Args:
            bucket_name: Archive bucket name (not storage bucket/provider name)
            remote_path: Destination path inside the archive bucket
            local_path: Local file path to upload
            filename: Optional destination filename override

        Notes:
            - Unsupported characters (including spaces) are rejected.
        """
        upload_path = Path(local_path)
        if not upload_path.is_file():
            raise FileNotFoundError(f"File not found: {upload_path}")

        # Treat explicit filename="" as invalid user input rather than silently falling back.
        if filename is None:
            resolved_filename = upload_path.name
        else:
            resolved_filename = filename
        self._validate_filename(resolved_filename)

        params: dict[str, Any] = {}
        if resolved_filename:
            params["filename"] = resolved_filename

        path = self._files_path(bucket_name=bucket_name, remote_path=remote_path)
        with upload_path.open("rb") as file_handle:
            try:
                response = self._http.request(
                    "POST",
                    path,
                    params=params or None,
                    files={"file": (resolved_filename, file_handle)},
                )
            except NotFoundError as exc:
                detail = (
                    exc.message if exc.message and exc.message != "Unknown error" else "not found"
                )
                raise NotFoundError(
                    message=(
                        "Archive upload target not found "
                        f"(bucket_name='{bucket_name}', remote_path='{remote_path}', filename='{resolved_filename}'). "
                        f"Backend detail: {detail}."
                    ),
                    response=exc.response,
                    request_id=exc.request_id,
                ) from exc

        return ArchiveFile.model_validate(response.get("archiveFile", response))

    def upload_directory(
        self,
        *,
        bucket_name: str,
        remote_path: str,
        local_directory: str | Path,
        recursive: bool = True,
        dry_run: bool = False,
        strict: bool = False,
    ) -> ArchiveDirectoryUploadResult:
        """
        Upload files from a local directory into an archive bucket path.

        This method uses a 2-phase flow:
        1) Preflight scan/validation to classify files as eligible or skipped.
        2) Upload eligible files (unless `dry_run=True`, or `strict=True` with skipped files).

        Directory structure is preserved relative to `local_directory`.

        Args:
            bucket_name: Archive bucket name (not storage bucket/provider name)
            remote_path: Destination base path inside the archive bucket
            local_directory: Local directory path containing files to upload
            recursive: Upload files from nested subdirectories when True
            dry_run: Perform preflight only and skip network uploads
            strict: Abort upload phase when preflight skipped files are found

        Returns:
            Two-phase upload summary:
            - preflight counts (`scanned`, `eligible`, `skipped`)
            - upload counts (`uploaded`, `failed`)
            - per-file reasons for skipped/failed files
        """
        source_dir = Path(local_directory)
        if not source_dir.exists():
            raise FileNotFoundError(f"Directory not found: {source_dir}")
        if not source_dir.is_dir():
            raise NotADirectoryError(f"Expected directory path, got file: {source_dir}")

        base_remote_path = self._normalize_archive_directory_path(remote_path)
        local_files = self._iter_directory_files(source_dir=source_dir, recursive=recursive)

        eligible_uploads: list[tuple[Path, str]] = []
        skipped_files: list[ArchiveDirectorySkippedFile] = []
        for local_file in local_files:
            relative_parent = local_file.relative_to(source_dir).parent
            destination_remote_path = base_remote_path
            if relative_parent != Path("."):
                destination_remote_path = self._join_archive_directory_path(
                    base_remote_path=base_remote_path,
                    relative_parent=relative_parent.as_posix(),
                )

            try:
                self._validate_upload_candidate(local_file)
            except Exception as exc:
                skipped_files.append(
                    ArchiveDirectorySkippedFile(
                        local_path=str(local_file),
                        remote_path=destination_remote_path,
                        reason=self._format_exception_reason(exc),
                        error_type=exc.__class__.__name__,
                    )
                )
                continue
            eligible_uploads.append((local_file, destination_remote_path))

        scanned = len(local_files)
        eligible = len(eligible_uploads)
        skipped = len(skipped_files)

        if dry_run or (strict and skipped > 0):
            return ArchiveDirectoryUploadResult(
                scanned=scanned,
                eligible=eligible,
                skipped=skipped,
                uploaded=0,
                failed=0,
                dry_run=dry_run,
                strict=strict,
                aborted=strict and skipped > 0,
                uploaded_files=[],
                skipped_files=skipped_files,
                failed_files=[],
            )

        uploaded_files: list[ArchiveFile] = []
        failed_files: list[ArchiveDirectoryUploadFailure] = []
        for local_file, destination_remote_path in eligible_uploads:
            try:
                uploaded = self.upload_file(
                    bucket_name=bucket_name,
                    remote_path=destination_remote_path,
                    local_path=local_file,
                )
            except Exception as exc:
                failed_files.append(
                    ArchiveDirectoryUploadFailure(
                        local_path=str(local_file),
                        remote_path=destination_remote_path,
                        reason=self._format_exception_reason(exc),
                        error_type=exc.__class__.__name__,
                    )
                )
                continue
            uploaded_files.append(uploaded)

        return ArchiveDirectoryUploadResult(
            scanned=scanned,
            eligible=eligible,
            skipped=skipped,
            uploaded=len(uploaded_files),
            failed=len(failed_files),
            dry_run=dry_run,
            strict=strict,
            aborted=False,
            uploaded_files=uploaded_files,
            skipped_files=skipped_files,
            failed_files=failed_files,
        )

    def download_file(
        self,
        *,
        bucket_name: str,
        remote_path: str,
        local_path: str | Path | None = None,
    ) -> bytes | Path:
        """
        Download an archive file.

        Args:
            bucket_name: Archive bucket name
            remote_path: File path inside archive bucket
            local_path: Optional local destination path

        Returns:
            File bytes when local_path is not provided, otherwise saved file path.
        """
        path = self._download_path(bucket_name=bucket_name, remote_path=remote_path)
        content = self._http.get_bytes(path)

        if local_path is None:
            return content

        resolved_local_path = Path(local_path)
        resolved_local_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_local_path.write_bytes(content)
        return resolved_local_path

    def copy_file(
        self,
        *,
        source_bucket_name: str,
        source_path: str,
        destination_bucket_name: str,
        destination_path: str | None = None,
        destination_filename: str | None = None,
    ) -> ArchiveFile:
        """
        Copy an archive file from one bucket/path to another.

        This operation downloads file bytes from the source and uploads them to the target.
        """
        downloaded = self.download_file(
            bucket_name=source_bucket_name,
            remote_path=source_path,
        )
        if isinstance(downloaded, Path):
            file_bytes = downloaded.read_bytes()
        else:
            file_bytes = downloaded
        source_name = Path(source_path).name or "copied-file"
        final_name = destination_filename or source_name

        temp_file: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"-{final_name}") as temp_handle:
                temp_handle.write(file_bytes)
                temp_file = Path(temp_handle.name)

            return self.upload_file(
                bucket_name=destination_bucket_name,
                remote_path=destination_path or "/",
                local_path=temp_file,
                filename=final_name,
            )
        finally:
            if temp_file and temp_file.exists():
                temp_file.unlink()

    def get_file(self, archive_file_id: int) -> ArchiveFile:
        """
        Get an archive file by ID.

        Args:
            archive_file_id: Archive file ID
        """
        response = self._http.get(f"/archives/files/{archive_file_id}")
        file_data = response.get("archiveFile", response)
        return ArchiveFile.model_validate(file_data)

    def delete_file(self, archive_file_id: int) -> bool:
        """
        Delete an archive file or directory by ID.

        Args:
            archive_file_id: Archive file ID
        """
        self._http.delete(f"/archives/files/{archive_file_id}")
        return True

    @staticmethod
    def _files_path(bucket_name: str, remote_path: str) -> str:
        """Build URL-safe path for archive files endpoint."""
        encoded_bucket = quote(bucket_name, safe="")
        normalized_remote_path = remote_path if remote_path else "/"
        encoded_remote_path = quote(normalized_remote_path, safe="/")
        return f"/archives/buckets/{encoded_bucket}/files/{encoded_remote_path}"

    @staticmethod
    def _download_path(bucket_name: str, remote_path: str) -> str:
        """Build URL-safe path for archive download endpoint."""
        encoded_bucket = quote(bucket_name, safe="")
        normalized_remote_path = remote_path if remote_path else "/"
        encoded_remote_path = quote(normalized_remote_path, safe="/")
        return f"/archives/download/{encoded_bucket}/{encoded_remote_path}"

    @staticmethod
    def _normalize_archive_directory_path(remote_path: str) -> str:
        """Normalize destination archive directory path."""
        normalized = (remote_path or "/").strip()
        if not normalized:
            normalized = "/"
        if not normalized.startswith("/"):
            normalized = f"/{normalized}"
        if not normalized.endswith("/"):
            normalized = f"{normalized}/"
        return normalized

    @staticmethod
    def _join_archive_directory_path(base_remote_path: str, relative_parent: str) -> str:
        """Join archive base path with relative local parent directory."""
        cleaned_parent = relative_parent.strip("/")
        if not cleaned_parent:
            return base_remote_path
        return f"{base_remote_path.rstrip('/')}/{cleaned_parent}/"

    @staticmethod
    def _iter_directory_files(source_dir: Path, recursive: bool) -> builtin_list[Path]:
        """Collect local files in deterministic order."""
        iterator = source_dir.rglob("*") if recursive else source_dir.iterdir()
        files = [path for path in iterator if path.is_file()]
        return sorted(files, key=lambda item: item.relative_to(source_dir).as_posix())

    @staticmethod
    def _validate_filename(filename: str) -> None:
        """Validate filename before making upload request."""
        if not filename:
            raise ValueError("Invalid filename: value cannot be empty.")
        if filename in {".", ".."}:
            raise ValueError("Invalid filename: '.' and '..' are not allowed.")
        if filename.startswith("."):
            raise ValueError("Invalid filename: names starting with '.' are not allowed.")
        if any(ch.isspace() for ch in filename):
            raise ValueError(
                "Invalid filename: spaces are not allowed. Use a filename without spaces."
            )

        # Includes SDK-invalid chars and additional chars observed to be blocked by backend WAF.
        invalid_chars = {
            "\\",
            "/",
            ":",
            "*",
            "?",
            '"',
            "<",
            ">",
            "|",
            "#",
            "%",
            "&",
            "+",
            "'",
            ";",
            "=",
            "^",
        }
        found = sorted({ch for ch in filename if ch in invalid_chars})
        if found:
            joined = " ".join(found)
            raise ValueError(
                f"Invalid filename: contains unsupported character(s): {joined}. "
                "Use a filename without unsupported characters."
            )

    @staticmethod
    def _validate_upload_candidate(local_file: Path) -> None:
        """Validate local file before upload phase starts."""
        if not local_file.exists():
            raise FileNotFoundError(f"File not found: {local_file}")
        if not local_file.is_file():
            raise ValueError(f"Expected file path, got directory: {local_file}")
        if not os.access(local_file, os.R_OK):
            raise PermissionError(f"File is not readable: {local_file}")
        ArchiveBucketsResource._validate_filename(local_file.name)

    @staticmethod
    def _format_exception_reason(exc: Exception) -> str:
        """Extract a readable error reason for upload summary."""
        if isinstance(exc, NotFoundError) and exc.message:
            return exc.message
        message = str(exc).strip()
        if message:
            return message
        return exc.__class__.__name__
