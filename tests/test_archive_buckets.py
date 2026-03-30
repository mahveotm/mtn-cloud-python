"""
Tests for ArchiveBucket models and resource.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.models.archive import (
    ArchiveBucket,
    ArchiveBucketCreate,
    ArchiveBucketVisibility,
    ArchiveFile,
)
from mtn_cloud.resources.archive_buckets import ArchiveBucketsResource

SAMPLE_ARCHIVE_BUCKET = {
    "id": 1113,
    "name": "apitestmybucket",
    "description": "API Test: My Archive Bucket",
    "storageProvider": {"id": 113, "name": "Local Archives"},
    "owner": {"id": 1, "name": "MTN QA"},
    "createdBy": {"username": "apiuser"},
    "isPublic": False,
    "visibility": "private",
    "code": "64d94943f108",
    "filePath": "mtn-archives/64d94943f108/",
    "rawSize": 0,
    "fileCount": 0,
    "accounts": [],
}

SAMPLE_ARCHIVE_FILE = {
    "id": 5338,
    "name": "test.txt",
    "filePath": "mtn-archives/6f657af7bc7b/test.txt",
    "archiveBucket": {"id": 1115, "name": "apitestmybucket", "isPublic": False},
    "createdBy": {"username": "apiuser"},
    "isDirectory": False,
    "status": "Active",
    "rawSize": 0,
    "contentType": "text/plain",
}


class TestArchiveModels:
    """Tests for archive models."""

    def test_parse_archive_bucket(self):
        """Test parsing archive bucket."""
        bucket = ArchiveBucket.model_validate(SAMPLE_ARCHIVE_BUCKET)
        assert bucket.id == 1113
        assert bucket.name == "apitestmybucket"
        assert bucket.storage_provider is not None
        assert bucket.storage_provider.id == 113

    def test_parse_archive_file(self):
        """Test parsing archive file."""
        file_obj = ArchiveFile.model_validate(SAMPLE_ARCHIVE_FILE)
        assert file_obj.id == 5338
        assert file_obj.name == "test.txt"
        assert file_obj.archive_bucket is not None
        assert file_obj.archive_bucket.name == "apitestmybucket"

    def test_archive_bucket_create_payload(self):
        """Test archive bucket create payload generation."""
        payload = ArchiveBucketCreate(
            name="mybucket",
            storage_provider_id=113,
            visibility=ArchiveBucketVisibility.PRIVATE,
            isPublic=False,
        ).to_api_payload()

        assert payload["archiveBucket"]["name"] == "mybucket"
        assert payload["archiveBucket"]["storageProvider"]["id"] == 113
        assert payload["archiveBucket"]["visibility"] == "private"
        assert payload["archiveBucket"]["isPublic"] is False


class TestArchiveBucketsResource:
    """Tests for ArchiveBucketsResource."""

    def test_list_archive_buckets(self):
        """Test listing archive buckets."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"archiveBuckets": [SAMPLE_ARCHIVE_BUCKET]}

        resource = ArchiveBucketsResource(mock_http)
        buckets = resource.list(name="apitestmybucket")

        assert len(buckets) == 1
        assert buckets[0].id == 1113
        call_args = mock_http.get.call_args
        assert call_args[0][0] == "/archives/buckets"
        assert call_args[1]["params"]["name"] == "apitestmybucket"

    def test_create_archive_bucket(self):
        """Test creating archive bucket."""
        mock_http = MagicMock()
        mock_http.post.return_value = {"archiveBucket": SAMPLE_ARCHIVE_BUCKET}

        resource = ArchiveBucketsResource(mock_http)
        created = resource.create(
            name="apitestmybucket",
            storage_provider_id=113,
            visibility="private",
            is_public=False,
        )

        assert created.id == 1113
        call_args = mock_http.post.call_args
        assert call_args[0][0] == "/archives/buckets"
        assert call_args[1]["json"]["archiveBucket"]["storageProvider"]["id"] == 113

    def test_list_archive_files(self):
        """Test listing files in archive bucket."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"archiveFiles": [SAMPLE_ARCHIVE_FILE]}

        resource = ArchiveBucketsResource(mock_http)
        files = resource.list_files(
            bucket_name="apitestmybucket",
            remote_path="/",
            full_tree=True,
        )

        assert len(files) == 1
        assert files[0].id == 5338
        call_args = mock_http.get.call_args
        assert call_args[0][0] == "/archives/buckets/apitestmybucket/files//"
        assert call_args[1]["params"]["fullTree"] is True

    def test_upload_archive_file(self, tmp_path: Path):
        """Test uploading file to archive bucket."""
        local_file = tmp_path / "test.txt"
        local_file.write_text("hello", encoding="utf-8")

        mock_http = MagicMock()
        mock_http.request.return_value = {"archiveFile": SAMPLE_ARCHIVE_FILE}

        resource = ArchiveBucketsResource(mock_http)
        uploaded = resource.upload_file(
            bucket_name="apitestmybucket",
            remote_path="/",
            local_path=local_file,
        )

        assert uploaded.id == 5338
        call_args = mock_http.request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/archives/buckets/apitestmybucket/files//"
        assert "file" in call_args[1]["files"]

    def test_upload_archive_file_not_found(self):
        """Test uploading missing file raises FileNotFoundError."""
        mock_http = MagicMock()
        resource = ArchiveBucketsResource(mock_http)

        with pytest.raises(FileNotFoundError):
            resource.upload_file(
                bucket_name="apitestmybucket",
                remote_path="/",
                local_path="/tmp/does-not-exist-123.txt",
            )

    def test_upload_archive_file_not_found_api_error_has_context(self, tmp_path: Path):
        """Test upload adds bucket/path context when API returns 404."""
        local_file = tmp_path / "test.txt"
        local_file.write_text("hello", encoding="utf-8")

        mock_http = MagicMock()
        mock_http.request.side_effect = NotFoundError(message="Unknown error")
        resource = ArchiveBucketsResource(mock_http)

        with pytest.raises(NotFoundError) as exc_info:
            resource.upload_file(
                bucket_name="missing-bucket",
                remote_path="/",
                local_path=local_file,
            )

        message = str(exc_info.value)
        assert "bucket_name='missing-bucket'" in message
        assert "remote_path='/'" in message

    def test_upload_archive_file_invalid_filename(self, tmp_path: Path):
        """Test upload rejects invalid filenames such as names with spaces."""
        local_file = tmp_path / "test.txt"
        local_file.write_text("hello", encoding="utf-8")

        mock_http = MagicMock()
        resource = ArchiveBucketsResource(mock_http)

        with pytest.raises(ValueError):
            resource.upload_file(
                bucket_name="apitestmybucket",
                remote_path="/",
                local_path=local_file,
                filename="bad file name.txt",
            )

        mock_http.request.assert_not_called()

    def test_upload_archive_file_invalid_waf_sensitive_char(self, tmp_path: Path):
        """Test upload rejects filenames with chars known to be blocked by backend WAF."""
        local_file = tmp_path / "test.txt"
        local_file.write_text("hello", encoding="utf-8")

        mock_http = MagicMock()
        resource = ArchiveBucketsResource(mock_http)

        with pytest.raises(ValueError):
            resource.upload_file(
                bucket_name="apitestmybucket",
                remote_path="/",
                local_path=local_file,
                filename="bad'name.txt",
            )

        mock_http.request.assert_not_called()

    def test_upload_archive_file_empty_filename_is_invalid(self, tmp_path: Path):
        """Test explicit empty filename is rejected."""
        local_file = tmp_path / "test.txt"
        local_file.write_text("hello", encoding="utf-8")

        mock_http = MagicMock()
        resource = ArchiveBucketsResource(mock_http)

        with pytest.raises(ValueError):
            resource.upload_file(
                bucket_name="apitestmybucket",
                remote_path="/",
                local_path=local_file,
                filename="",
            )

        mock_http.request.assert_not_called()

    def test_upload_archive_file_leading_dot_is_invalid(self, tmp_path: Path):
        """Test filenames starting with dot are rejected."""
        local_file = tmp_path / "test.txt"
        local_file.write_text("hello", encoding="utf-8")

        mock_http = MagicMock()
        resource = ArchiveBucketsResource(mock_http)

        with pytest.raises(ValueError):
            resource.upload_file(
                bucket_name="apitestmybucket",
                remote_path="/",
                local_path=local_file,
                filename=".env",
            )

        mock_http.request.assert_not_called()

    def test_upload_archive_directory_recursive(self, tmp_path: Path):
        """Test recursive directory upload preserves folder structure."""
        src_dir = tmp_path / "data"
        nested_dir = src_dir / "nested"
        nested_dir.mkdir(parents=True)
        (src_dir / "a.txt").write_text("a", encoding="utf-8")
        (nested_dir / "b.txt").write_text("b", encoding="utf-8")

        mock_http = MagicMock()
        mock_http.request.return_value = {"archiveFile": SAMPLE_ARCHIVE_FILE}
        resource = ArchiveBucketsResource(mock_http)

        summary = resource.upload_directory(
            bucket_name="apitestmybucket",
            remote_path="/incoming",
            local_directory=src_dir,
            recursive=True,
        )

        assert summary.scanned_count == 2
        assert summary.eligible_count == 2
        assert summary.skipped_count == 0
        assert summary.uploaded_count == 2
        assert summary.failed_count == 0
        assert len(summary.uploaded_files) == 2
        assert mock_http.request.call_count == 2
        first_call = mock_http.request.call_args_list[0]
        second_call = mock_http.request.call_args_list[1]
        assert first_call[0][1] == "/archives/buckets/apitestmybucket/files//incoming/"
        assert first_call[1]["files"]["file"][0] == "a.txt"
        assert second_call[0][1] == "/archives/buckets/apitestmybucket/files//incoming/nested/"
        assert second_call[1]["files"]["file"][0] == "b.txt"

    def test_upload_archive_directory_non_recursive(self, tmp_path: Path):
        """Test non-recursive directory upload only uploads top-level files."""
        src_dir = tmp_path / "data"
        nested_dir = src_dir / "nested"
        nested_dir.mkdir(parents=True)
        (src_dir / "top.txt").write_text("top", encoding="utf-8")
        (nested_dir / "deep.txt").write_text("deep", encoding="utf-8")

        mock_http = MagicMock()
        mock_http.request.return_value = {"archiveFile": SAMPLE_ARCHIVE_FILE}
        resource = ArchiveBucketsResource(mock_http)

        summary = resource.upload_directory(
            bucket_name="apitestmybucket",
            remote_path="/",
            local_directory=src_dir,
            recursive=False,
        )

        assert summary.scanned_count == 1
        assert summary.eligible_count == 1
        assert summary.skipped_count == 0
        assert summary.uploaded_count == 1
        assert summary.failed_count == 0
        assert len(summary.uploaded_files) == 1
        call_args = mock_http.request.call_args
        assert call_args[0][1] == "/archives/buckets/apitestmybucket/files//"
        assert call_args[1]["files"]["file"][0] == "top.txt"

    def test_upload_archive_directory_preflight_skips_invalid_name(self, tmp_path: Path):
        """Test preflight skips invalid filenames and uploads valid files."""
        src_dir = tmp_path / "data"
        src_dir.mkdir(parents=True)
        (src_dir / "good.txt").write_text("ok", encoding="utf-8")
        (src_dir / "bad name.txt").write_text("bad", encoding="utf-8")

        mock_http = MagicMock()
        mock_http.request.return_value = {"archiveFile": SAMPLE_ARCHIVE_FILE}
        resource = ArchiveBucketsResource(mock_http)

        summary = resource.upload_directory(
            bucket_name="apitestmybucket",
            remote_path="/",
            local_directory=src_dir,
            recursive=False,
        )

        assert summary.scanned_count == 2
        assert summary.eligible_count == 1
        assert summary.skipped_count == 1
        assert summary.uploaded_count == 1
        assert summary.failed_count == 0
        assert mock_http.request.call_count == 1
        skipped = summary.skipped_files[0]
        assert skipped.local_path.endswith("bad name.txt")
        assert skipped.error_type == "ValueError"
        assert "spaces are not allowed" in skipped.reason

    def test_upload_archive_directory_dry_run_reports_preflight_only(self, tmp_path: Path):
        """Test dry run performs scan/validation but skips network uploads."""
        src_dir = tmp_path / "data"
        src_dir.mkdir(parents=True)
        (src_dir / "good.txt").write_text("ok", encoding="utf-8")

        mock_http = MagicMock()
        resource = ArchiveBucketsResource(mock_http)

        summary = resource.upload_directory(
            bucket_name="apitestmybucket",
            remote_path="/",
            local_directory=src_dir,
            recursive=False,
            dry_run=True,
        )

        assert summary.dry_run is True
        assert summary.scanned_count == 1
        assert summary.eligible_count == 1
        assert summary.uploaded_count == 0
        assert summary.failed_count == 0
        assert summary.skipped_count == 0
        mock_http.request.assert_not_called()

    def test_upload_archive_directory_strict_aborts_on_preflight_skips(self, tmp_path: Path):
        """Test strict mode aborts upload phase when preflight finds invalid files."""
        src_dir = tmp_path / "data"
        src_dir.mkdir(parents=True)
        (src_dir / "good.txt").write_text("ok", encoding="utf-8")
        (src_dir / "bad name.txt").write_text("bad", encoding="utf-8")

        mock_http = MagicMock()
        resource = ArchiveBucketsResource(mock_http)

        summary = resource.upload_directory(
            bucket_name="apitestmybucket",
            remote_path="/",
            local_directory=src_dir,
            recursive=False,
            strict=True,
        )

        assert summary.strict is True
        assert summary.aborted is True
        assert summary.scanned_count == 2
        assert summary.eligible_count == 1
        assert summary.skipped_count == 1
        assert summary.uploaded_count == 0
        assert summary.failed_count == 0
        mock_http.request.assert_not_called()

    def test_upload_archive_directory_continues_when_one_file_fails(self, tmp_path: Path):
        """Test directory upload continues and reports failures instead of failing fast."""
        src_dir = tmp_path / "data"
        src_dir.mkdir(parents=True)
        (src_dir / "a.txt").write_text("a", encoding="utf-8")
        (src_dir / "b.txt").write_text("b", encoding="utf-8")

        def request_side_effect(*args, **kwargs):
            filename = kwargs["files"]["file"][0]
            if filename == "a.txt":
                raise NotFoundError(message="Unknown error")
            return {"archiveFile": {**SAMPLE_ARCHIVE_FILE, "name": filename}}

        mock_http = MagicMock()
        mock_http.request.side_effect = request_side_effect
        resource = ArchiveBucketsResource(mock_http)

        summary = resource.upload_directory(
            bucket_name="apitestmybucket",
            remote_path="/",
            local_directory=src_dir,
            recursive=False,
        )

        assert summary.uploaded_count == 1
        assert summary.failed_count == 1
        assert summary.skipped_count == 0
        assert summary.total_count == 2
        assert summary.has_failures is True
        assert summary.uploaded_files[0].name == "b.txt"
        failure = summary.failed_files[0]
        assert failure.local_path.endswith("a.txt")
        assert failure.remote_path == "/"
        assert failure.error_type == "NotFoundError"
        assert "Archive upload target not found" in failure.reason

    def test_upload_archive_directory_not_found(self):
        """Test missing source directory raises FileNotFoundError."""
        mock_http = MagicMock()
        resource = ArchiveBucketsResource(mock_http)

        with pytest.raises(FileNotFoundError):
            resource.upload_directory(
                bucket_name="apitestmybucket",
                remote_path="/",
                local_directory="/tmp/does-not-exist-dir-123",
            )

        mock_http.request.assert_not_called()

    def test_upload_archive_directory_requires_directory(self, tmp_path: Path):
        """Test directory upload rejects file paths."""
        not_dir = tmp_path / "single.txt"
        not_dir.write_text("hello", encoding="utf-8")

        mock_http = MagicMock()
        resource = ArchiveBucketsResource(mock_http)

        with pytest.raises(NotADirectoryError):
            resource.upload_directory(
                bucket_name="apitestmybucket",
                remote_path="/",
                local_directory=not_dir,
            )

        mock_http.request.assert_not_called()

    def test_upload_archive_directory_returns_failure_summary_on_not_found(self, tmp_path: Path):
        """Test directory upload reports 404 errors in failure summary."""
        src_dir = tmp_path / "data"
        src_dir.mkdir(parents=True)
        (src_dir / "top.txt").write_text("top", encoding="utf-8")

        mock_http = MagicMock()
        mock_http.request.side_effect = NotFoundError(message="Unknown error")
        resource = ArchiveBucketsResource(mock_http)

        summary = resource.upload_directory(
            bucket_name="missing-bucket",
            remote_path="/",
            local_directory=src_dir,
        )

        assert summary.uploaded_count == 0
        assert summary.failed_count == 1
        assert summary.skipped_count == 0
        failure = summary.failed_files[0]
        assert failure.local_path.endswith("top.txt")
        assert failure.remote_path == "/"
        assert failure.error_type == "NotFoundError"
        assert "Archive upload target not found" in failure.reason
        assert "bucket_name='missing-bucket'" in failure.reason

    def test_download_archive_file_as_bytes(self):
        """Test downloading archive file as bytes."""
        mock_http = MagicMock()
        mock_http.get_bytes.return_value = b"hello archive"
        resource = ArchiveBucketsResource(mock_http)

        content = resource.download_file(
            bucket_name="apitestmybucket",
            remote_path="folder/test.txt",
        )

        assert content == b"hello archive"
        mock_http.get_bytes.assert_called_with("/archives/download/apitestmybucket/folder/test.txt")

    def test_download_archive_file_to_destination(self, tmp_path: Path):
        """Test downloading archive file directly to local destination."""
        mock_http = MagicMock()
        mock_http.get_bytes.return_value = b"hello archive"
        resource = ArchiveBucketsResource(mock_http)

        destination = tmp_path / "downloads" / "test.txt"
        result = resource.download_file(
            bucket_name="apitestmybucket",
            remote_path="test.txt",
            local_path=destination,
        )

        assert isinstance(result, Path)
        assert result == destination
        assert destination.read_bytes() == b"hello archive"

    def test_copy_archive_file_between_buckets(self):
        """Test copying archive file between buckets."""
        mock_http = MagicMock()
        mock_http.get_bytes.return_value = b"hello archive"
        mock_http.request.return_value = {"archiveFile": SAMPLE_ARCHIVE_FILE}
        resource = ArchiveBucketsResource(mock_http)

        copied = resource.copy_file(
            source_bucket_name="source-bucket",
            source_path="folder/source.txt",
            destination_bucket_name="target-bucket",
            destination_path="/",
            destination_filename="copied.txt",
        )

        assert copied.id == 5338
        mock_http.get_bytes.assert_called_with("/archives/download/source-bucket/folder/source.txt")
        call_args = mock_http.request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/archives/buckets/target-bucket/files//"
        assert call_args[1]["files"]["file"][0] == "copied.txt"

    def test_get_archive_file_details(self):
        """Test fetching archive file details by ID."""
        mock_http = MagicMock()
        mock_http.get.return_value = {"archiveFile": SAMPLE_ARCHIVE_FILE}
        resource = ArchiveBucketsResource(mock_http)

        file_obj = resource.get_file(5338)

        assert file_obj.id == 5338
        mock_http.get.assert_called_with("/archives/files/5338")

    def test_delete_archive_file(self):
        """Test deleting archive file by ID."""
        mock_http = MagicMock()
        mock_http.delete.return_value = {"success": True}
        resource = ArchiveBucketsResource(mock_http)

        deleted = resource.delete_file(5338)

        assert deleted is True
        mock_http.delete.assert_called_with("/archives/files/5338")
