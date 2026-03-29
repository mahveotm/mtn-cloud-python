"""
MTN Cloud SDK - List Storage and Archive Buckets
================================================

Run with:
    export MTN_CLOUD_TOKEN="your-token"
    python examples/list_storage_buckets.py
"""

from mtn_cloud import MTNCloud, MTNCloudError


def main() -> None:
    cloud = MTNCloud()

    print("MTN Cloud - List Storage and Archive Buckets")
    print("=" * 60)

    try:
        storage_buckets = cloud.storage_buckets.list()
        print(f"\nStorage Buckets ({len(storage_buckets)}):")
        for bucket in storage_buckets:
            print(
                "  - "
                f"id={bucket.id}, "
                f"name={bucket.name}, "
                f"provider={bucket.provider_type}, "
                f"bucketName={bucket.bucket_name}"
            )

        archive_buckets = cloud.archive_buckets.list()
        print(f"\nArchive Buckets ({len(archive_buckets)}):")
        for bucket in archive_buckets:
            provider = bucket.storage_provider.name if bucket.storage_provider else "N/A"
            print(
                "  - "
                f"id={bucket.id}, "
                f"name={bucket.name}, "
                f"visibility={bucket.visibility}, "
                f"storageProvider={provider}, "
                f"fileCount={bucket.file_count}"
            )
    except MTNCloudError as exc:
        print(f"\nAPI error: {exc}")


if __name__ == "__main__":
    main()
