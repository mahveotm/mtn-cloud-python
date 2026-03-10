"""
MTN Cloud Client
================

Main client class for interacting with MTN Cloud.
"""

from typing import Any

from mtn_cloud.config import MTNCloudConfig
from mtn_cloud.http import HTTPClient
from mtn_cloud.models.user import User
from mtn_cloud.resources.clouds import CloudsResource
from mtn_cloud.resources.groups import GroupsResource
from mtn_cloud.resources.instances import InstancesResource
from mtn_cloud.resources.networks import NetworksResource
from mtn_cloud.resources.plans import PlansResource


class MTNCloud:
    """
    MTN Cloud client for interacting with the Morpheus API.

    This is the main entry point for the SDK. Initialize with your
    API token or credentials to start making API calls.

    Example:
        ```python
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

        # Create an instance
        instance = cloud.instances.create(
            name="my-app",
            cloud_id=1,
            group_id=1,
            instance_type_code="MTN-CS10",
            layout_id=327,
            plan_id=6923,
        )

        # Use as context manager
        with MTNCloud(token="xxx") as cloud:
            instances = cloud.instances.list()
        ```

    Attributes:
        instances: Manage compute instances
        networks: Manage networks
        groups: Manage groups (sites)
        clouds: Manage clouds (zones)
        plans: Manage service plans

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
        self._networks: NetworksResource | None = None
        self._groups: GroupsResource | None = None
        self._clouds: CloudsResource | None = None
        self._plans: PlansResource | None = None

    @property
    def instances(self) -> InstancesResource:
        """
        Access the instances resource manager.

        Example:
            ```python
            # List instances
            instances = cloud.instances.list()

            # Create instance
            instance = cloud.instances.create(...)

            # Get instance
            instance = cloud.instances.get(123)
            ```
        """
        if self._instances is None:
            self._instances = InstancesResource(self._http)
        return self._instances

    @property
    def networks(self) -> NetworksResource:
        """
        Access the networks resource manager.

        Example:
            ```python
            # List networks
            networks = cloud.networks.list()

            # Get network
            network = cloud.networks.get(123)
            ```
        """
        if self._networks is None:
            self._networks = NetworksResource(self._http)
        return self._networks

    @property
    def groups(self) -> GroupsResource:
        """
        Access the groups resource manager.

        Example:
            ```python
            # List groups
            groups = cloud.groups.list()

            # Get group
            group = cloud.groups.get(1)
            ```
        """
        if self._groups is None:
            self._groups = GroupsResource(self._http)
        return self._groups

    @property
    def clouds(self) -> CloudsResource:
        """
        Access the clouds resource manager.

        Example:
            ```python
            # List clouds
            clouds = cloud.clouds.list()

            # Get cloud
            c = cloud.clouds.get(1)
            ```
        """
        if self._clouds is None:
            self._clouds = CloudsResource(self._http)
        return self._clouds

    @property
    def plans(self) -> PlansResource:
        """
        Access the service plans resource manager.

        Example:
            ```python
            # List plans
            plans = cloud.plans.list()

            # Get plan
            plan = cloud.plans.get(6923)
            ```
        """
        if self._plans is None:
            self._plans = PlansResource(self._http)
        return self._plans

    def whoami(self) -> User:
        """
        Get the current authenticated user.

        Returns:
            Current user information

        Example:
            ```python
            user = cloud.whoami()
            print(f"Logged in as: {user.username}")
            print(f"Email: {user.email}")
            ```
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
            ```python
            if cloud.ping():
                print("Connected!")
            ```
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
