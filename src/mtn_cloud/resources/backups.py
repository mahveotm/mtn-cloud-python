"""Resource manager for MTN Cloud backups."""

from __future__ import annotations

from typing import Any, List

from mtn_cloud.models.backup import Backup, BackupJob, BackupResult
from mtn_cloud.resources.base import BaseResource


class BackupsResource(BaseResource[Backup]):
    """
    Manage instance and storage backups.

    Backup jobs are defined in the console and executed on a schedule.
    This resource lets you list backups, check job status, and retrieve
    execution results.

    Example:
        # List all configured backups
        for backup in cloud.backups.list():
            print(f"{backup.name}: last run {backup.last_run}")

        # List backup jobs
        for job in cloud.backups.list_jobs():
            print(f"{job.name}: {job.cron_expression}")

        # Get execution results for a backup
        results = cloud.backups.list_results(backup_id=42)
    """

    _path = "/backups"
    _model = Backup
    _name = "backup"
    _list_key = "backups"
    _item_key = "backup"

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        **filters: Any,
    ) -> list[Backup]:
        """
        List backups.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            phrase: Search phrase
            **filters: Additional filters

        Returns:
            List of backups
        """
        return super().list(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        )

    def get(self, backup_id: int) -> Backup:
        """
        Get a backup by ID.

        Args:
            backup_id: Backup ID

        Returns:
            Backup object
        """
        return super().get(backup_id)

    def delete(self, backup_id: int) -> bool:
        """
        Delete a backup configuration.

        Args:
            backup_id: Backup ID

        Returns:
            True if deleted
        """
        return self._delete(backup_id)

    def execute(self, backup_id: int) -> dict[str, Any]:
        """
        Trigger an immediate backup execution.

        Args:
            backup_id: Backup ID

        Returns:
            Execution status response
        """
        path = f"{self._path}/{backup_id}/execute"
        return self._http.post(path)

    def list_results(
        self,
        backup_id: int,
        max_results: int | None = None,
    ) -> List[BackupResult]:
        """
        List execution results for a backup.

        Args:
            backup_id: Backup ID
            max_results: Maximum number of results

        Returns:
            List of backup results
        """
        path = f"{self._path}/{backup_id}/results"
        params: dict[str, Any] = {}
        if max_results is not None:
            params["max"] = max_results
        response = self._http.get(path, params=params or None)
        return [BackupResult.model_validate(r) for r in response.get("results", [])]

    def list_jobs(
        self,
        max_results: int | None = None,
        offset: int = 0,
    ) -> List[BackupJob]:
        """
        List backup jobs (schedules).

        Args:
            max_results: Maximum number of results
            offset: Pagination offset

        Returns:
            List of backup jobs
        """
        params: dict[str, Any] = {}
        if max_results is not None:
            params["max"] = max_results
        if offset:
            params["offset"] = offset
        response = self._http.get("/backups/jobs", params=params or None)
        return [BackupJob.model_validate(j) for j in response.get("jobs", [])]

    def get_job(self, job_id: int) -> BackupJob:
        """
        Get a backup job by ID.

        Args:
            job_id: Backup job ID

        Returns:
            Backup job
        """
        response = self._http.get(f"/backups/jobs/{job_id}")
        return BackupJob.model_validate(response.get("job", response))

    def execute_job(self, job_id: int) -> dict[str, Any]:
        """
        Execute a backup job immediately.

        Args:
            job_id: Backup job ID

        Returns:
            Execution status response
        """
        return self._http.post(f"/backups/jobs/{job_id}/execute")
