"""Models for MTN Cloud snapshots."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from mtn_cloud.models.base import BaseModel, Resource


class Snapshot(Resource):
    """
    MTN Cloud instance snapshot.

    Snapshots capture the disk state of an instance at a point in time.
    They are accessed via the instance they belong to.

    Example:
        snap = cloud.instances.create_snapshot(instance_id=123, name="pre-upgrade")
        cloud.instances.list_snapshots(instance_id=123)
        cloud.instances.revert_snapshot(instance_id=123, snapshot_id=snap.id)
    """

    description: str | None = None
    status: str | None = None
    snapshot_type: str | None = Field(default=None, alias="snapshotType")
    snapshot_created: datetime | None = Field(default=None, alias="snapshotCreated")
    current: bool | None = None
    external_id: str | None = Field(default=None, alias="externalId")
    state: dict[str, Any] | None = None
    datastore: dict[str, Any] | None = None
    zone: dict[str, Any] | None = None
    instance: dict[str, Any] | None = None

    @property
    def cloud_id(self) -> int | None:
        if self.zone:
            return self.zone.get("id")
        return None


class SnapshotCreate(BaseModel):
    """Payload builder for creating a snapshot."""

    name: str
    description: str | None = None

    def to_api_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": self.name}
        if self.description is not None:
            payload["description"] = self.description
        return {"snapshot": payload}
