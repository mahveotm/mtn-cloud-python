"""Client entry point for interacting with MTN Cloud."""

from typing import Any

from mtn_cloud.config import MTNCloudConfig
from mtn_cloud.http import HTTPClient
from mtn_cloud.models.user import User
from mtn_cloud.resources.archive_buckets import ArchiveBucketsResource
from mtn_cloud.resources.clouds import CloudsResource
from mtn_cloud.resources.groups import GroupsResource
from mtn_cloud.resources.instance_types import InstanceTypesResource
from mtn_cloud.resources.instances import InstancesResource
from mtn_cloud.resources.networks import NetworksResource
from mtn_cloud.resources.plans import PlansResource
from mtn_cloud.resources.storage_buckets import StorageBucketsResource


class MTNCloud:
    """
    MTN Cloud client for interacting with the MTN Cloud API.

    This is the main entry point for the SDK. Initialize with your
    API token or credentials to start making API calls.

    Example:
        from mtn_cloud import MTNCloud

        # Initialize with token
        cloud = MTNCloud(token="your-api-token")

        # Or with username/password
        cloud = MTNCloud(
            username="user@example.com",
            password="your-password",
        )

        # List instances
        for instance in cloud.instances.list():
            print(f"{instance.name}: {instance.status}")

        # Create an instance on MTN Cloud
        instance = cloud.instances.create(
            name="MyInstanceName",
            cloud="MTNNG_CLOUD_AZ_1",
            type="MTN-CS10",
            group="MTNNG_CLOUD_AZ_1",
            layout=327,
            plan=6923,
            resource_pool_id="pool-214",
        )

        # Use as context manager
        with MTNCloud(token="xxx") as cloud:
            instances = cloud.instances.list()

    Attributes:
        instances: Manage compute instances
        instance_types: Discover available instance types
        networks: Manage networks
        clouds: Manage clouds/zones
        groups: Manage groups (sites)
        plans: Manage service plans
        storage_buckets: Manage storage buckets and file shares
        archive_buckets: Manage archive buckets and files

    Environment Variables:
        MTN_CLOUD_TOKEN: API access token
        MTN_CLOUD_URL: API URL (default: https://console.cloud.mtn.ng)
        MTN_CLOUD_TIMEOUT: Request timeout in seconds
    """

    def __init__(
        self,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        url: str | None = None,
        timeout: float | None = None,
        verify_ssl: bool = True,
        config: MTNCloudConfig | None = None,
    ) -> None:
        """
        Initialize the MTN Cloud client.

        Args:
            token: API access token
            username: Username for authentication
            password: Password for authentication
            url: API base URL (default: https://console.cloud.mtn.ng)
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
            config: Full configuration object (overrides other args)
        """
        # Build config from arguments or use provided config
        if config:
            self._config = config
        else:
            config_kwargs: dict[str, Any] = {}

            if token:
                config_kwargs["token"] = token
            if username:
                config_kwargs["username"] = username
            if password:
                config_kwargs["password"] = password
            if url:
                config_kwargs["url"] = url
            if timeout:
                config_kwargs["timeout"] = timeout
            if not verify_ssl:
                config_kwargs["verify_ssl"] = verify_ssl

            self._config = MTNCloudConfig(**config_kwargs)

        # Initialize HTTP client
        self._http = HTTPClient(self._config)

        # Initialize resource managers
        self._instances: InstancesResource | None = None
        self._instance_types: InstanceTypesResource | None = None
        self._networks: NetworksResource | None = None
        self._clouds: CloudsResource | None = None
        self._groups: GroupsResource | None = None
        self._plans: PlansResource | None = None
        self._storage_buckets: StorageBucketsResource | None = None
        self._archive_buckets: ArchiveBucketsResource | None = None

    @property
    def instances(self) -> InstancesResource:
        """
        Access the instances resource manager.

        Example:
            # List instances
            instances = cloud.instances.list()

            # Create instance
            instance = cloud.instances.create(...)

            # Get instance
            instance = cloud.instances.get(123)
        """
        if self._instances is None:
            self._instances = InstancesResource(self._http)
        return self._instances

    @property
    def instance_types(self) -> InstanceTypesResource:
        """
        Access the instance types resource manager.

        Instance types define the OS or application templates available
        for provisioning on MTN Cloud.

        Example:
            # List all instance types
            instance_types = cloud.instance_types.list()

            # List OS types only
            os_types = cloud.instance_types.list_os()

            # Get by code
            centos = cloud.instance_types.get_by_code("MTN-CS10")
            print(f"Layout ID: {centos.default_layout_id}")
        """
        if self._instance_types is None:
            self._instance_types = InstanceTypesResource(self._http)
        return self._instance_types

    @property
    def networks(self) -> NetworksResource:
        """
        Access the networks resource manager.

        Example:
            # List networks
            networks = cloud.networks.list()

            # Get network
            network = cloud.networks.get(123)
        """
        if self._networks is None:
            self._networks = NetworksResource(self._http)
        return self._networks

    @property
    def groups(self) -> GroupsResource:
        """
        Access the groups resource manager.

        Example:
            # List groups
            groups = cloud.groups.list()

            # Get group
            group = cloud.groups.get(1)
        """
        if self._groups is None:
            self._groups = GroupsResource(self._http)
        return self._groups

    @property
    def clouds(self) -> CloudsResource:
        """
        Access the clouds (zones) resource manager.

        Example:
            clouds = cloud.clouds.list_openstack()
        """
        if self._clouds is None:
            self._clouds = CloudsResource(self._http)
        return self._clouds

    @property
    def plans(self) -> PlansResource:
        """
        Access the service plans resource manager.

        Example:
            # List plans
            plans = cloud.plans.list()

            # Get plan
            plan = cloud.plans.get(6923)
        """
        if self._plans is None:
            self._plans = PlansResource(self._http)
        return self._plans

    @property
    def storage_buckets(self) -> StorageBucketsResource:
        """
        Access the storage buckets resource manager.

        Example:
            storage_buckets = cloud.storage_buckets.list()
            bucket = cloud.storage_buckets.create_s3(
                name="my-s3-store",
                bucket_name="my-objects",
                access_key="AKIA...",
                secret_key="...",
                endpoint="https://s3.example.com",
            )
        """
        if self._storage_buckets is None:
            self._storage_buckets = StorageBucketsResource(self._http)
        return self._storage_buckets

    @property
    def archive_buckets(self) -> ArchiveBucketsResource:
        """
        Access the archive buckets resource manager.

        Example:
            archive_buckets = cloud.archive_buckets.list()
            files = cloud.archive_buckets.list_files(
                bucket_name="my-archive",
                remote_path="/",
            )
        """
        if self._archive_buckets is None:
            self._archive_buckets = ArchiveBucketsResource(self._http)
        return self._archive_buckets

    def whoami(self) -> User:
        """
        Get the current authenticated user.

        Returns:
            Current user information

        Example:
            user = cloud.whoami()
            print(f"Logged in as: {user.username}")
            print(f"Email: {user.email}")
        """
        response = self._http.get("/whoami")
        user_data = response.get("user", response)
        return User.model_validate(user_data)

    def ping(self) -> bool:
        """
        Check if the API is reachable and authentication is valid.

        Returns:
            True if connection is successful

        Example:
            if cloud.ping():
                print("Connected!")
        """
        try:
            self.whoami()
            return True
        except Exception:
            return False

    @property
    def config(self) -> MTNCloudConfig:
        """Get the current configuration."""
        return self._config

    @property
    def api_url(self) -> str:
        """Get the API URL."""
        return self._config.api_url

    def close(self) -> None:
        """Close the HTTP session."""
        self._http.close()

    def __enter__(self) -> "MTNCloud":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        return f"<MTNCloud url={self._config.url!r}>"
