"""
MTN Cloud SDK - Copy Archive File Between Buckets
=================================================

This copies an existing archive file from one archive bucket/path to another.

Run with:
    export MTN_CLOUD_TOKEN="your-token"
    export MTN_SOURCE_ARCHIVE_BUCKET="source-bucket-name"
    export MTN_SOURCE_FILE_PATH="folder/file.txt"
    export MTN_TARGET_ARCHIVE_BUCKET="target-bucket-name"
    python examples/copy_archive_file.py

Optional env:
    MTN_TARGET_FILE_PATH="/"           # destination path in target bucket
    MTN_TARGET_FILENAME="copied.txt"   # override destination filename
"""

from __future__ import annotations

import os

from mtn_cloud import MTNCloud, MTNCloudError


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


def main() -> None:
    print("MTN Cloud - Copy Archive File Between Buckets")
    print("=" * 60)

    try:
        source_bucket_name = _required_env("MTN_SOURCE_ARCHIVE_BUCKET")
        source_file_path = _required_env("MTN_SOURCE_FILE_PATH")
        destination_bucket_name = _required_env("MTN_TARGET_ARCHIVE_BUCKET")
    except ValueError as exc:
        print(f"Configuration error: {exc}")
        return

    destination_path = os.getenv("MTN_TARGET_FILE_PATH", "/").strip() or "/"
    destination_filename = os.getenv("MTN_TARGET_FILENAME", "").strip() or None

    cloud = MTNCloud()

    try:
        copied = cloud.archive_buckets.copy_file(
            source_bucket_name=source_bucket_name,
            source_path=source_file_path,
            destination_bucket_name=destination_bucket_name,
            destination_path=destination_path,
            destination_filename=destination_filename,
        )
        print("Copy completed.")
        print(f"  id={copied.id}")
        print(f"  name={copied.name}")
        print(f"  filePath={copied.file_path}")
    except MTNCloudError as exc:
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
