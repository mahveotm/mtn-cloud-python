"""Create an MTN router from existing networks; optionally delete it afterward."""

import argparse
import json

from mtn_cloud import MTNCloud, MTNCloudError


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", default="MTNNG_CLOUD_AZ_1")
    parser.add_argument("--resource-pool", required=True)
    parser.add_argument("--internal-network", required=True)
    parser.add_argument("--external-network", default="public-network-01")
    parser.add_argument("--name", default="app-router")
    parser.add_argument("--cloud-id", type=int)
    parser.add_argument(
        "--delete-after",
        action="store_true",
        help="Delete this newly created router after validation, including on provisioning failure.",
    )
    args = parser.parse_args()

    with MTNCloud() as cloud:  # Reads MTN_CLOUD_TOKEN
        group = cloud.groups.get_by_name(args.group)
        cloud_id = args.cloud_id
        if cloud_id is None:
            if len(group.cloud_ids) != 1:
                raise ValueError("Select a cloud explicitly with --cloud-id.")
            cloud_id = group.cloud_ids[0]
        public = cloud.routers.get_external_network(
            args.external_network,
            group=args.group,
            resource_pool=args.resource_pool,
            cloud_id=cloud_id,
        )
        pool = cloud.instances.get_resource_pool(
            args.resource_pool, group_id=group.id, cloud_id=cloud_id
        )
        internal = cloud.networks.get_by_name(args.internal_network, cloud_id=cloud_id)
        internal = cloud.networks.get(internal.id)
        if internal.zone_pool is None or internal.zone_pool.id != pool.id:
            raise ValueError("The internal network must belong to the selected resource pool.")
        subnets = cloud.networks.list_subnets(internal.id)
        router_id = None
        try:
            router = cloud.routers.create(
                name=args.name,
                group_id=group.id,
                cloud_id=cloud_id,
                resource_pool_id=pool.id,
                external_network_id=public.id,
                internal_subnet_ids=[subnet.id for subnet in subnets],
            )
            router_id = router.id
            print(f"Submitted router: {router_id}", flush=True)
            router = cloud.routers.wait_until_ready(router_id)
            # Confirm the subsequent API read agrees with the requested gateway
            # and internal network, not just that a local record was accepted.
            router = cloud.routers.get(router_id)
            if (
                router.status not in {"ok", "available", "active"}
                or not router.external_id
                or router.external_network is None
                or router.external_network.id != public.id
                or not any(i.network and i.network.id == internal.id for i in router.interfaces)
            ):
                raise RuntimeError(f"Router {router_id} does not match the requested topology.")
            print(
                json.dumps(
                    {
                        "router_id": router.id,
                        "status": router.status,
                        "backend_id": router.external_id,
                        "external_network_id": public.id,
                        "external_network_name": public.name,
                        "external_ip": router.external_ip,
                        "internal_subnet_ids": [s.id for s in subnets],
                    }
                ),
                flush=True,
            )
        except MTNCloudError as exc:
            # A successful POST followed by a failed read still has a cleanup ID.
            if router_id is None and exc.response:
                router_id = exc.response.get("router_id")
            raise
        finally:
            if args.delete_after and router_id is not None:
                cloud.routers.delete(router_id)
                cloud.routers.wait_until_deleted(router_id)
                print(f"Deleted router: {router_id}", flush=True)


if __name__ == "__main__":
    main()
