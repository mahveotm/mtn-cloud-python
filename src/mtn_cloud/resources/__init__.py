"""Public resource manager exports for MTN Cloud API endpoints."""

from mtn_cloud.resources.archive_buckets import ArchiveBucketsResource
from mtn_cloud.resources.base import BaseResource
from mtn_cloud.resources.clouds import CloudsResource
from mtn_cloud.resources.groups import GroupsResource
from mtn_cloud.resources.instances import InstancesResource
from mtn_cloud.resources.networks import NetworksResource
from mtn_cloud.resources.plans import PlansResource
from mtn_cloud.resources.storage_buckets import StorageBucketsResource

__all__ = [
    "BaseResource",
    "InstancesResource",
    "NetworksResource",
    "GroupsResource",
    "CloudsResource",
    "PlansResource",
    "StorageBucketsResource",
    "ArchiveBucketsResource",
]
