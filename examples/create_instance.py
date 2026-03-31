"""
MTN Cloud SDK - Create Instance Example
=======================================

This example shows how to create and manage an instance.

Run with:
    export MTN_CLOUD_TOKEN="your-token"
    python examples/create_instance.py
"""

from mtn_cloud import MTNCloud
from mtn_cloud.models.instance import InstanceNetwork, InstanceVolume


def main():
    cloud = MTNCloud()

    print("MTN Cloud - Create Instance Example")
    print("=" * 50)

    # First, let's discover available resources
    print("\n1. Discovering available resources...")

    groups = cloud.groups.list()
    networks = cloud.networks.list()

    if not groups:
        print("❌ No groups available. Contact your admin.")
        return

    # Use first available group
    group = groups[0]
    network = networks[0] if networks else None

    print(f"   Group: {group.name} (ID: {group.id})")
    if network:
        print(f"   Network: {network.name} (ID: {network.id})")

    # Build instance configuration
    print("\n2. Preparing instance configuration...")

    instance_name = "mtn-cloud-sdk-demo"

    # NOTE: You'll need to adjust these values for your environment
    # These are example values - get real ones from your MTN Cloud console
    _volumes = [
        InstanceVolume(
            name="root",
            size=20,  # 20 GB
            storage_type=11,
            datastore_id="auto",
            root_volume=True,
        ),
    ]

    _network_interfaces = []
    if network:
        _network_interfaces.append(
            InstanceNetwork(
                network_id=f"network-{network.id}",
                # ip_address="192.168.100.50",  # Optional: static IP
            )
        )

    print(f"   Instance name: {instance_name}")
    print("   Root volume: 20GB")

    # Create the instance
    print("\n3. Creating instance...")
    print("   (This is a demo - uncomment the code below to actually create)")

    # UNCOMMENT THE FOLLOWING TO ACTUALLY CREATE AN INSTANCE:
    # --------------------------------------------------------
    # try:
    #     instance = cloud.instances.create(
    #         name=instance_name,
    #         cloud=zone.name,  # e.g., "MTNNG_CLOUD_AZ_1"
    #         type="MTN-CS10",  # Adjust for your environment
    #         group=group.name,  # e.g., "MTNNG_CLOUD_AZ_1"
    #         layout=327,  # Adjust for your environment
    #         plan=6923,  # Adjust for your environment
    #         resource_pool_id="pool-214",  # Your resource pool
    #         availability_zone="Lagos-AZ-1-fd1",  # Your availability zone
    #         security_group="default",
    #         os_external_network_id="public-network-01",
    #         volumes=_volumes,
    #         network_interfaces=_network_interfaces,
    #         labels=["demo", "sdk-example"],
    #     )
    #
    #     print(f"   ✅ Instance created: {instance.name} (ID: {instance.id})")
    #     print(f"   Status: {instance.status}")
    #
    #     # Wait for it to be running
    #     print("\n4. Waiting for instance to be running...")
    #     instance = cloud.instances.wait_until_running(instance.id, timeout=300)
    #     print(f"   ✅ Instance is now: {instance.status}")
    #     print(f"   IP Address: {instance.primary_ip}")
    #
    #     # Optionally stop and delete
    #     # print("\n5. Cleaning up...")
    #     # instance.stop()
    #     # instance.delete()
    #     # print("   ✅ Instance deleted")
    #
    # except MTNCloudError as e:
    #     print(f"   ❌ Failed: {e}")
    # --------------------------------------------------------

    print("\n" + "=" * 50)
    print("Demo complete!")
    print("Uncomment the creation code to actually create an instance.")
    print("=" * 50)


if __name__ == "__main__":
    main()
