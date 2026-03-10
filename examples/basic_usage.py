"""
MTN Cloud SDK - Example Usage
=============================

This example demonstrates common operations with the MTN Cloud SDK.

Run with:
    export MTN_CLOUD_TOKEN="your-token"
    python examples/basic_usage.py
"""

from mtn_cloud import MTNCloud, MTNCloudError


def main():
    # Initialize client
    # Token can be passed directly or via MTN_CLOUD_TOKEN env var
    cloud = MTNCloud()

    # Check connection
    print("=" * 50)
    print("MTN Cloud SDK - Basic Usage Example")
    print("=" * 50)

    try:
        user = cloud.whoami()
        print(f"\n✅ Connected as: {user.username}")
        print(f"   Email: {user.email}")
    except MTNCloudError as e:
        print(f"\n❌ Connection failed: {e}")
        return

    # List available resources
    print("\n" + "-" * 50)
    print("Available Resources")
    print("-" * 50)

    # Groups
    groups = cloud.groups.list()
    print(f"\n📁 Groups ({len(groups)}):")
    for group in groups[:5]:
        print(f"   - {group.name} (ID: {group.id})")

    # Service Plans
    plans = cloud.plans.list()
    print(f"\n📦 Service Plans ({len(plans)}):")
    for plan in plans[:5]:
        cores = plan.cores or "N/A"
        memory = f"{plan.memory_gb:.1f}GB" if plan.memory_gb else "N/A"
        print(f"   - {plan.name} ({cores} cores, {memory} RAM)")

    # Instances
    print("\n" + "-" * 50)
    print("Your Instances")
    print("-" * 50)

    instances = cloud.instances.list()
    if instances:
        print(f"\n🖥️  Found {len(instances)} instance(s):")
        for instance in instances:
            status_icon = "🟢" if instance.is_running else "🔴"
            ip = instance.primary_ip or "No IP"
            print(f"   {status_icon} {instance.name}")
            print(f"      ID: {instance.id}")
            print(f"      Status: {instance.status}")
            print(f"      IP: {ip}")
    else:
        print("\n📭 No instances found.")
        print("   Create one with cloud.instances.create(...)")

    # Networks
    print("\n" + "-" * 50)
    print("Available Networks")
    print("-" * 50)

    networks = cloud.networks.list()
    print(f"\n🌐 Networks ({len(networks)}):")
    for network in networks[:5]:
        cidr = network.cidr or "N/A"
        print(f"   - {network.name} ({cidr})")

    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
