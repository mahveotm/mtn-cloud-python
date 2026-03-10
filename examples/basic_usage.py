"""
MTN Cloud SDK - Example Usage
=============================

This example demonstrates common operations with the MTN Cloud SDK.

Run with:
    export MTN_CLOUD_TOKEN="your-token"
    python examples/basic_usage.py
"""

from mtn_cloud import MTNCloud, MTNCloudError, NotFoundError


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
        print(f"   Ping: {'OK' if cloud.ping() else 'Failed'}")
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

    # Filtered list examples
    print("\n" + "-" * 50)
    print("Filtered Examples")
    print("-" * 50)

    running_instances = cloud.instances.list(status="running", max_results=5)
    print(f"\n▶️  Running instances (top 5): {len(running_instances)}")
    for instance in running_instances:
        print(f"   - {instance.name} ({instance.status})")

    # Safe lookups by name (using discovered values)
    print("\n" + "-" * 50)
    print("Lookup Examples")
    print("-" * 50)

    if networks:
        sample_network_name = networks[0].name
        try:
            network = cloud.networks.get_by_name(sample_network_name)
            print(f"🔎 Network lookup succeeded: {network.name} (ID: {network.id})")
        except NotFoundError:
            print(f"⚠️  Network lookup failed for: {sample_network_name}")

    # Discover instance types by category
    print("\n" + "-" * 50)
    print("Instance Type Categories")
    print("-" * 50)

    os_types = cloud.instance_types.list_os()
    db_types = cloud.instance_types.list_databases()
    web_types = cloud.instance_types.list_web()

    print(f"\n💿 OS templates: {len(os_types)}")
    print(f"🗃️  Database templates: {len(db_types)}")
    print(f"🌍 Web templates: {len(web_types)}")

    if os_types:
        print("\nTop OS templates:")
        for item in os_types[:3]:
            print(f"   - {item.name} [{item.code}]")

    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
