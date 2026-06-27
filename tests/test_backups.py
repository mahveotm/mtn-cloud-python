"""Tests for backup resources."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from mtn_cloud.resources.backups import BackupsResource

SAMPLE_BACKUP = {
    "id": 42,
    "name": "nightly-instance",
    "backupType": "instance",
    "status": "ok",
    "enabled": True,
    "instance": {"id": 123},
    "server": {"id": 55},
}

SAMPLE_BACKUP_RESULT = {
    "id": 77,
    "backupId": 42,
    "backupName": "nightly-instance",
    "status": "succeeded",
    "sizeInMb": 12.5,
}

SAMPLE_BACKUP_JOB = {
    "id": 8,
    "name": "nightly",
    "code": "nightly",
    "retentionCount": 7,
    "cronExpression": "0 0 * * *",
    "enabled": True,
}


@pytest.fixture
def resource(mock_http: MagicMock) -> BackupsResource:
    """Return a backups resource backed by a mocked HTTP client."""
    return BackupsResource(mock_http)


class TestBackupsResource:
    """Tests for BackupsResource."""

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 42),
            ("name", "nightly-instance"),
            ("backup_type", "instance"),
            ("instance_id", 123),
            ("server_id", 55),
        ],
    )
    def test_list_backup_field(
        self,
        resource: BackupsResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse listed backup fields."""
        mock_http.get.return_value = {"backups": [SAMPLE_BACKUP]}

        assert getattr(resource.list()[0], field) == expected

    def test_get_backup_path(self, resource: BackupsResource, mock_http: MagicMock) -> None:
        """Call the expected backup detail endpoint."""
        mock_http.get.return_value = {"backup": SAMPLE_BACKUP}

        resource.get(42)

        mock_http.get.assert_called_with("/backups/42")

    def test_delete_backup(self, resource: BackupsResource, mock_http: MagicMock) -> None:
        """Delete a backup configuration."""
        mock_http.delete.return_value = {"success": True}

        assert resource.delete(42) is True
        mock_http.delete.assert_called_with("/backups/42", params=None)

    def test_execute_backup_path(self, resource: BackupsResource, mock_http: MagicMock) -> None:
        """Call the expected backup execution endpoint."""
        mock_http.post.return_value = {"success": True}

        resource.execute(42)

        mock_http.post.assert_called_with("/backups/42/execute")

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 77),
            ("backup_id", 42),
            ("status", "succeeded"),
            ("size_in_mb", 12.5),
        ],
    )
    def test_list_result_field(
        self,
        resource: BackupsResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse backup execution result fields."""
        mock_http.get.return_value = {"results": [SAMPLE_BACKUP_RESULT]}

        assert getattr(resource.list_results(42, max_results=1)[0], field) == expected

    def test_list_results_request(self, resource: BackupsResource, mock_http: MagicMock) -> None:
        """Send expected backup result list request."""
        mock_http.get.return_value = {"results": [SAMPLE_BACKUP_RESULT]}

        resource.list_results(42, max_results=1)

        mock_http.get.assert_called_with("/backups/42/results", params={"max": 1})

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("id", 8),
            ("name", "nightly"),
            ("cron_expression", "0 0 * * *"),
        ],
    )
    def test_list_job_field(
        self,
        resource: BackupsResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse backup job fields."""
        mock_http.get.return_value = {"jobs": [SAMPLE_BACKUP_JOB]}

        assert getattr(resource.list_jobs(max_results=1, offset=2)[0], field) == expected

    def test_list_jobs_request(self, resource: BackupsResource, mock_http: MagicMock) -> None:
        """Send expected backup job list request."""
        mock_http.get.return_value = {"jobs": [SAMPLE_BACKUP_JOB]}

        resource.list_jobs(max_results=1, offset=2)

        mock_http.get.assert_called_with("/backups/jobs", params={"max": 1, "offset": 2})

    def test_get_job_path(self, resource: BackupsResource, mock_http: MagicMock) -> None:
        """Call the expected backup job detail endpoint."""
        mock_http.get.return_value = {"job": SAMPLE_BACKUP_JOB}

        resource.get_job(8)

        mock_http.get.assert_called_with("/backups/jobs/8")

    def test_execute_job_path(self, resource: BackupsResource, mock_http: MagicMock) -> None:
        """Call the expected backup job execution endpoint."""
        mock_http.post.return_value = {"success": True}

        resource.execute_job(8)

        mock_http.post.assert_called_with("/backups/jobs/8/execute")
