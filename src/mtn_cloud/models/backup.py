"""Models for MTN Cloud backups."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from mtn_cloud.models.base import BaseModel, Resource


class BackupResult(BaseModel):
    """A single backup execution result."""

    id: int
    backup_id: int | None = Field(default=None, alias="backupId")
    backup_name: str | None = Field(default=None, alias="backupName")
    status: str | None = None
    size_in_mb: float | None = Field(default=None, alias="sizeInMb")
    duration_millis: int | None = Field(default=None, alias="durationMillis")
    start_date: datetime | None = Field(default=None, alias="startDate")
    end_date: datetime | None = Field(default=None, alias="endDate")
    error_message: str | None = Field(default=None, alias="errorMessage")
    config: dict[str, Any] | None = None

    def __str__(self) -> str:
        return f"BackupResult(id={self.id}, status={self.status})"

    def __repr__(self) -> str:
        return str(self)


class Backup(Resource):
    """
    MTN Cloud backup.

    Represents a configured backup job for an instance or storage target.

    Example:
        backups = cloud.backups.list()
        for b in backups:
            print(f"{b.name}: {b.status}")
    """

    backup_type: str | None = Field(default=None, alias="backupType")
    status: str | None = None
    enabled: bool | None = None
    retention_count: int | None = Field(default=None, alias="retentionCount")
    scheduled: bool | None = None
    cron_expression: str | None = Field(default=None, alias="cronExpression")
    last_status: str | None = Field(default=None, alias="lastStatus")
    last_success: datetime | None = Field(default=None, alias="lastSuccess")
    last_run: datetime | None = Field(default=None, alias="lastRun")
    next_fire: datetime | None = Field(default=None, alias="nextFire")
    server: dict[str, Any] | None = None
    instance: dict[str, Any] | None = None
    container: dict[str, Any] | None = None
    job: dict[str, Any] | None = None
    storage_provider: dict[str, Any] | None = Field(default=None, alias="storageProvider")
    site: dict[str, Any] | None = None

    @property
    def instance_id(self) -> int | None:
        if self.instance:
            return self.instance.get("id")
        return None

    @property
    def server_id(self) -> int | None:
        if self.server:
            return self.server.get("id")
        return None


class BackupJob(BaseModel):
    """A backup job definition (schedule/group of backups)."""

    id: int
    name: str | None = None
    code: str | None = None
    retention_count: int | None = Field(default=None, alias="retentionCount")
    cron_expression: str | None = Field(default=None, alias="cronExpression")
    enabled: bool | None = None
    last_status: str | None = Field(default=None, alias="lastStatus")
    last_run: datetime | None = Field(default=None, alias="lastRun")
    next_fire: datetime | None = Field(default=None, alias="nextFire")

    def __str__(self) -> str:
        return f"BackupJob(id={self.id}, name={self.name!r})"

    def __repr__(self) -> str:
        return str(self)
