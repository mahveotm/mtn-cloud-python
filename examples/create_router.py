"""Create an MTN router using existing networks and a resource pool."""

from mtn_cloud import MTNCloud

with MTNCloud() as cloud:  # Reads MTN_CLOUD_TOKEN
    group = cloud.groups.get_by_name("MTNNG_CLOUD_AZ_1")
    if len(group.cloud_ids) != 1:
        raise ValueError("Select a cloud explicitly for this group.")
    cloud_id = group.cloud_ids[0]

    pool = cloud.instances.get_resource_pool("my-project", group_id=group.id, cloud_id=cloud_id)
    public = cloud.networks.get_by_name("public-network-01", cloud_id=cloud_id)
    internal = cloud.networks.get_by_name("app-net", cloud_id=cloud_id)
    internal = cloud.networks.get(internal.id)
    if internal.zone_pool is None or internal.zone_pool.id != pool.id:
        raise ValueError("The internal network must belong to the selected resource pool.")
    subnets = cloud.networks.list_subnets(internal.id)

    router = cloud.routers.create(
        name="app-router",
        group_id=group.id,
        cloud_id=cloud_id,
        resource_pool_id=pool.id,
        external_network_id=public.id,
        internal_subnet_ids=[subnet.id for subnet in subnets],
    )
    print("Submitted router:", router.id)
    router = cloud.routers.wait_until_ready(router.id)
    print(router.id, router.status, router.external_ip)

    # When no longer needed:
    # cloud.routers.delete(router.id)
    # cloud.routers.wait_until_deleted(router.id)
