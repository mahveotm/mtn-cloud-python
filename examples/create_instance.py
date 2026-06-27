"""
MTN Cloud SDK - Create Instance Example
=======================================

Discover the IDs an instance needs (all permission-safe), then provision.

Run with:
    export MTN_CLOUD_TOKEN="your-token"
    python examples/create_instance.py
"""

from mtn_cloud import MTNCloud


def main() -> None:
    cloud = MTNCloud()

    print("MTN Cloud - Create Instance Example")
    print("=" * 50)

    # 1. Discover provisioning inputs.
    group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
    itype = cloud.instance_types.get_by_code("MTN-CS10")
    pools = cloud.instances.list_resource_pools(group=group.name)
    plans = cloud.instances.list_service_plans(
        zone_id=group.cloud_ids[0],
        layout_id=itype.default_layout_id,
        group_id=group.id,
    )

    print(f"group={group.id} cloud_id={group.cloud_ids[0]} layout={itype.default_layout_id}")
    print("pools:", [(p.code, p.name) for p in pools[:3]])
    print("plans:", [(p["id"], p["name"]) for p in plans[:3]])

    if not pools or not plans:
        print("\nNo resource pool or service plan available. Create a project first.")
        return

    # 2. Provision. Uncomment to actually create an instance.
    # instance = cloud.instances.create(
    #     name="sdk-demo-01",
    #     cloud=group.name,
    #     type=itype.code,
    #     group=group.name,
    #     layout=itype.default_layout_id,
    #     plan=plans[0]["id"],
    #     resource_pool_id=pools[0].code,
    #     availability_zone="Lagos-AZ-1-fd1",
    #     security_group="default",
    #     labels=["demo", "sdk-example"],
    # )
    # instance = cloud.instances.wait_until_running(instance.id, timeout=600)
    # print(f"ready: {instance.id} {instance.name} {instance.primary_ip}")

    print("\nDone. Uncomment the create block to provision for real.")


if __name__ == "__main__":
    main()
