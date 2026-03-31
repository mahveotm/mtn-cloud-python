"""Resource manager for MTN Cloud instances."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Dict, List

from mtn_cloud.exceptions import NotFoundError, TimeoutError
from mtn_cloud.models.instance import (
    Instance,
    InstanceCreate,
    InstanceNetwork,
    InstanceUpdate,
    InstanceVolume,
)
from mtn_cloud.resources.base import BaseResource

if TYPE_CHECKING:
    pass


class InstancesResource(BaseResource[Instance]):
    """
    Manage MTN Cloud instances.

    Example:
        # List instances
        instances = cloud.instances.list()

        # Get instance
        instance = cloud.instances.get(123)

        # Create MTN Cloud instance
        instance = cloud.instances.create(
            name="MyInstanceName",
            cloud="MTNNG_CLOUD_AZ_1",
            type="MTN-CS10",
            group="MTNNG_CLOUD_AZ_1",
            layout=327,
            plan=6923,
            resource_pool_id="pool-214",
            availability_zone="Lagos-AZ-1-fd1",
            security_group="default",
            os_external_network_id="public-network-01",
        )

        # Instance actions
        cloud.instances.stop(123)
        cloud.instances.start(123)
        cloud.instances.restart(123)

        # Delete instance
        cloud.instances.delete(123)
    """

    _path = "/instances"
    _model = Instance
    _name = "instance"
    _list_key = "instances"
    _item_key = "instance"

    def _parse_item(self, data: dict[str, Any]) -> Instance:
        """Parse instance and bind resource manager."""
        instance = super()._parse_item(data)
        instance._set_resource(self)
        return instance

    def _parse_list(self, data: dict[str, Any]) -> list[Instance]:
        """Parse instance list and bind resource manager."""
        instances = super()._parse_list(data)
        for instance in instances:
            instance._set_resource(self)
        return instances

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        name: str | None = None,
        status: str | None = None,
        cloud_id: int | None = None,
        group_id: int | None = None,
        labels: list[str] | None = None,
        **filters: Any,
    ) -> list[Instance]:
        """
        List instances.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            sort: Field to sort by
            direction: Sort direction ('asc' or 'desc')
            phrase: Search phrase
            name: Filter by name
            status: Filter by status
            cloud_id: Filter by cloud ID
            group_id: Filter by group ID
            labels: Filter by labels
            **filters: Additional filters

        Returns:
            List of instances
        """
        if name:
            filters["name"] = name
        if status:
            filters["status"] = status
        if cloud_id:
            filters["zoneId"] = cloud_id
        if group_id:
            filters["siteId"] = group_id
        if labels:
            filters["labels"] = ",".join(labels)

        return super().list(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        )

    def get(self, instance_id: int) -> Instance:
        """
        Get an instance by ID.

        Args:
            instance_id: Instance ID

        Returns:
            Instance object

        Raises:
            NotFoundError: If instance not found
        """
        return super().get(instance_id)

    def get_by_name(self, name: str) -> Instance:
        """
        Get an instance by name.

        Args:
            name: Instance name

        Returns:
            Instance object

        Raises:
            NotFoundError: If instance not found
        """
        instances = self.list(name=name, max_results=1)
        if not instances:
            raise NotFoundError(
                resource_type="Instance",
                message=f"Instance with name '{name}' not found",
            )
        return instances[0]

    def create(
        self,
        name: str,
        *,
        cloud: str,
        type: str,
        group: str,
        layout: int,
        plan: int,
        resource_pool_id: str,
        description: str | None = None,
        environment: str | None = None,
        labels: List[str] | None = None,
        tags: Dict[str, str] | None = None,
        copies: int = 1,
        layout_size: int = 1,
        # MTN Cloud config options
        availability_zone: str | None = None,
        security_group: str = "default",
        os_external_network_id: str | None = None,
        create_user: bool = True,
        # Automation options
        workflow_id: int | None = None,
        shutdown_days: int | None = None,
        expire_days: int | None = None,
        create_backup: bool | None = None,
        security_groups: List[str] | None = None,
        ports: List[Dict[str, Any]] | None = None,
        volumes: List[InstanceVolume | Dict[str, Any]] | None = None,
        network_interfaces: List[InstanceNetwork | Dict[str, Any]] | None = None,
        options: Dict[str, Any] | None = None,
    ) -> Instance:
        """
        Create a new instance on MTN Cloud.

        Based on the Morpheus API specification for instance provisioning.

        Args:
            name: Instance name (required)
            cloud: Cloud name (e.g., 'MTNNG_CLOUD_AZ_1')
            type: Instance Type code (e.g., 'MTN-CS10')
            group: Group name (e.g., 'MTNNG_CLOUD_AZ_1') - will be resolved to ID automatically
            layout: Layout ID (e.g., 327)
            plan: Service plan ID (e.g., 6923)
            resource_pool_id: Resource pool ID (e.g., 'pool-214')
            description: Instance description
            environment: Environment code
            labels: Labels (keywords) list
            tags: Metadata tags dict (e.g., {"env": "prod"})
            copies: Number of copies to provision
            layout_size: Multiply factor of containers/vms
            availability_zone: Availability zone (e.g., 'Lagos-AZ-1-fd1')
            security_group: Security group name (default: 'default')
            os_external_network_id: External network for floating IP (e.g., 'public-network-01')
            create_user: Create your user on the instance (default: True)
            workflow_id: Automation workflow ID
            shutdown_days: Automation shutdown days
            expire_days: Automation expiration days
            create_backup: Create backups
            security_groups: List of security group names
            ports: Exposed ports (list of {name, port} dicts)
            volumes: List of volumes to attach
            network_interfaces: List of network interfaces
            options: Additional options

        Returns:
            Created instance

        Example:
            # MTN Cloud instance creation
            instance = cloud.instances.create(
                name="MyInstanceName",
                cloud="MTNNG_CLOUD_AZ_1",
                type="MTN-CS10",
                group="MTNNG_CLOUD_AZ_1",
                layout=327,
                plan=6923,
                resource_pool_id="pool-214",
                availability_zone="Lagos-AZ-1-fd1",
                security_group="default",
                os_external_network_id="public-network-01",
                volumes=[
                    InstanceVolume(name="root", size=10, storage_type=11),
                ],
                network_interfaces=[
                    InstanceNetwork(network_id="network-298", ip_address="192.168.100.40"),
                ],
            )
        """
        # Resolve group name to group ID
        group_id = self._resolve_group_id(group)

        # Convert volume dicts to models
        converted_volumes: list[InstanceVolume] = []
        if volumes is not None:
            for v in volumes:
                if isinstance(v, dict):
                    converted_volumes.append(InstanceVolume.model_validate(v))
                else:
                    converted_volumes.append(v)

        # Convert network dicts to models
        converted_network_interfaces: list[InstanceNetwork] = []
        if network_interfaces is not None:
            for n in network_interfaces:
                if isinstance(n, dict):
                    converted_network_interfaces.append(InstanceNetwork.model_validate(n))
                else:
                    converted_network_interfaces.append(n)

        # Build create model for MTN Cloud
        create_model = InstanceCreate(
            name=name,
            cloud=cloud,
            type=type,
            group_id=group_id,
            layout=layout,
            plan=plan,
            description=description,
            environment=environment,
            labels=labels or [],
            tags=tags or {},
            copies=copies,
            layout_size=layout_size,
            resource_pool_id=resource_pool_id,
            availability_zone=availability_zone,
            security_group=security_group,
            os_external_network_id=os_external_network_id,
            create_user=create_user,
            workflow_id=workflow_id,
            shutdown_days=shutdown_days,
            expire_days=expire_days,
            create_backup=create_backup,
            security_groups=security_groups,
            ports=ports,
            volumes=converted_volumes,
            network_interfaces=converted_network_interfaces,
            options=options or {},
        )

        payload = create_model.to_api_payload()
        return self._create(payload)

    def _resolve_group_id(self, group_name: str) -> int:
        """
        Resolve a group name to its ID.

        Args:
            group_name: Group name (e.g., 'MTNNG_CLOUD_AZ_1')

        Returns:
            Group ID

        Raises:
            NotFoundError: If group not found
        """
        # Import here to avoid circular imports
        from mtn_cloud.resources.groups import GroupsResource

        groups_resource = GroupsResource(self._http)
        group = groups_resource.get_by_name(group_name)
        return group.id

    def update(
        self,
        instance_id: int,
        name: str | None = None,
        description: str | None = None,
        labels: List[str] | None = None,
    ) -> Instance:
        """
        Update an instance.

        Args:
            instance_id: Instance ID
            name: New name
            description: New description
            labels: New labels

        Returns:
            Updated instance
        """
        update_model = InstanceUpdate(
            name=name,
            description=description,
            labels=labels,
        )
        payload = update_model.to_api_payload()
        return self._update(instance_id, payload)

    def delete(
        self,
        instance_id: int,
        preserve_volumes: bool = False,
        force: bool = False,
    ) -> bool:
        """
        Delete an instance.

        Args:
            instance_id: Instance ID
            preserve_volumes: Keep volumes after deletion
            force: Force delete

        Returns:
            True if deleted successfully
        """
        params = {}
        if preserve_volumes:
            params["preserveVolumes"] = "on"
        if force:
            params["force"] = "on"

        return self._delete(instance_id, params=params)

    # Instance Actions
    def start(self, instance_id: int) -> Instance:
        """
        Start an instance.

        Args:
            instance_id: Instance ID

        Returns:
            Updated instance
        """
        path = f"{self._path}/{instance_id}/start"
        self._http.put(path)
        return self.get(instance_id)

    def stop(self, instance_id: int) -> Instance:
        """
        Stop an instance.

        Args:
            instance_id: Instance ID

        Returns:
            Updated instance
        """
        path = f"{self._path}/{instance_id}/stop"
        self._http.put(path)
        return self.get(instance_id)

    def restart(self, instance_id: int) -> Instance:
        """
        Restart an instance.

        Args:
            instance_id: Instance ID

        Returns:
            Updated instance
        """
        path = f"{self._path}/{instance_id}/restart"
        self._http.put(path)
        return self.get(instance_id)

    def suspend(self, instance_id: int) -> Instance:
        """
        Suspend an instance.

        Args:
            instance_id: Instance ID

        Returns:
            Updated instance
        """
        path = f"{self._path}/{instance_id}/suspend"
        self._http.put(path)
        return self.get(instance_id)

    def resize(
        self,
        instance_id: int,
        plan_id: int,
    ) -> Instance:
        """
        Resize an instance to a different service plan.

        Args:
            instance_id: Instance ID
            plan_id: New service plan ID

        Returns:
            Updated instance
        """
        path = f"{self._path}/{instance_id}/resize"
        payload = {"instance": {"plan": {"id": plan_id}}}
        self._http.put(path, json=payload)
        return self.get(instance_id)

    def wait_for_status(
        self,
        instance_id: int,
        target_status: str,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> Instance:
        """
        Wait for an instance to reach a specific status.

        Args:
            instance_id: Instance ID
            target_status: Target status to wait for
            timeout: Maximum wait time in seconds
            poll_interval: Time between status checks

        Returns:
            Instance in target status

        Raises:
            TimeoutError: If timeout is reached
        """
        target_status = target_status.lower()
        start_time = time.time()

        while True:
            instance = self.get(instance_id)
            current_status = instance.status.lower()

            if current_status == target_status:
                return instance

            if current_status == "failed":
                raise RuntimeError(
                    f"Instance {instance_id} entered failed state: {instance.status_message}"
                )

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Timeout waiting for instance {instance_id} to reach status '{target_status}'. "
                    f"Current status: '{current_status}'",
                    timeout=timeout,
                )

            time.sleep(poll_interval)

    def wait_until_running(
        self,
        instance_id: int,
        timeout: int = 300,
    ) -> Instance:
        """
        Wait for an instance to be running.

        Args:
            instance_id: Instance ID
            timeout: Maximum wait time in seconds

        Returns:
            Running instance
        """
        return self.wait_for_status(instance_id, "running", timeout=timeout)

    def wait_until_stopped(
        self,
        instance_id: int,
        timeout: int = 300,
    ) -> Instance:
        """
        Wait for an instance to be stopped.

        Args:
            instance_id: Instance ID
            timeout: Maximum wait time in seconds

        Returns:
            Stopped instance
        """
        return self.wait_for_status(instance_id, "stopped", timeout=timeout)

    def get_console(self, instance_id: int) -> dict[str, Any]:
        """
        Get console access information for an instance.

        Args:
            instance_id: Instance ID

        Returns:
            Console access info (URL, credentials)
        """
        path = f"{self._path}/{instance_id}/console"
        return self._http.get(path)

    def get_history(
        self,
        instance_id: int,
        max_results: int | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Get instance history/events.

        Args:
            instance_id: Instance ID
            max_results: Maximum results

        Returns:
            List of history events
        """
        path = f"{self._path}/{instance_id}/history"
        params: Dict[str, Any] = {}
        if max_results:
            params["max"] = max_results

        response = self._http.get(path, params=params)
        result: List[Dict[str, Any]] = response.get("processes", [])
        return result
