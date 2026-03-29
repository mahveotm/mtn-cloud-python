"""
MTN Cloud SDK - S3-Compatible Storage + Archive Upload Example
==============================================================

This example shows the full flow:
1) Create an S3-compatible storage bucket provider
2) Create an archive bucket using that storage provider
3) Upload a file into the archive bucket
4) List files from the archive bucket

Run with:
    export MTN_CLOUD_TOKEN="your-token"
    export MTN_S3_ACCESS_KEY="your-access-key"
    export MTN_S3_SECRET_KEY="your-secret-key"
    export MTN_S3_ENDPOINT="https://ps1csp-s3.ict.mtn.com.ng:9021"
    export MTN_S3_BUCKET_NAME="my-app-objects"
    python examples/storage_archive_s3.py

Optional env:
    MTN_STORAGE_NAME="my-s3-storage"
    MTN_ARCHIVE_BUCKET_NAME="my-app-archives-<unique>"
    MTN_CREATE_BUCKET="true"  # true/false
    MTN_UPLOAD_FILE="./backup.sql"
"""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

from mtn_cloud import MTNCloud, MTNCloudError


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_upload_file() -> tuple[Path, bool]:
    """
    Resolve upload file from env.

    Returns:
        (path, should_cleanup)
    """
    explicit = os.getenv("MTN_UPLOAD_FILE", "").strip()
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"MTN_UPLOAD_FILE does not exist: {path}")
        return path, False

    tmp_dir = Path(tempfile.gettempdir())
    tmp_path = tmp_dir / f"mtn-cloud-upload-{int(time.time())}.txt"
    tmp_path.write_text(
        f"MTN Cloud SDK test upload generated at {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        encoding="utf-8",
    )
    return tmp_path, True


def main() -> None:
    print("MTN Cloud - S3-Compatible Storage and Archive Upload Example")
    print("=" * 70)

    try:
        access_key = _required_env("MTN_S3_ACCESS_KEY")
        secret_key = _required_env("MTN_S3_SECRET_KEY")
        endpoint = _required_env("MTN_S3_ENDPOINT")
        bucket_name = _required_env("MTN_S3_BUCKET_NAME")
    except ValueError as exc:
        print(f"Configuration error: {exc}")
        return

    create_bucket = _env_bool("MTN_CREATE_BUCKET", default=True)
    suffix = str(int(time.time()))
    storage_name = os.getenv("MTN_STORAGE_NAME", f"s3-storage-{suffix}").strip()
    archive_bucket_name = os.getenv("MTN_ARCHIVE_BUCKET_NAME", f"archives-{suffix}").strip()

    upload_path: Path | None = None
    should_cleanup = False
    try:
        upload_path, should_cleanup = _resolve_upload_file()
    except FileNotFoundError as exc:
        print(f"Configuration error: {exc}")
        return

    cloud = MTNCloud()

    try:
        print("\n1) Creating S3-compatible storage bucket provider...")
        storage_bucket = cloud.storage_buckets.create(
            name=storage_name,
            bucket_name=bucket_name,
            access_key=access_key,
            secret_key=secret_key,
            endpoint=endpoint,
            create_bucket=create_bucket,
        )
        print(f"   Storage bucket created: id={storage_bucket.id}, name={storage_bucket.name}")

        print("\n2) Creating archive bucket...")
        archive_bucket = cloud.archive_buckets.create(
            name=archive_bucket_name,
            storage_provider_id=storage_bucket.id,
            visibility="private",
            is_public=False,
        )
        print(f"   Archive bucket created: id={archive_bucket.id}, name={archive_bucket.name}")

        print("\n3) Uploading file...")
        uploaded = cloud.archive_buckets.upload_file(
            bucket_name=archive_bucket.name or archive_bucket_name,
            remote_path="/",
            local_path=upload_path,
        )
        print(f"   Uploaded: id={uploaded.id}, name={uploaded.name}, path={uploaded.file_path}")

        print("\n4) Listing files...")
        files = cloud.archive_buckets.list_files(
            bucket_name=archive_bucket.name or archive_bucket_name,
            remote_path="/",
            full_tree=True,
        )
        print(f"   Found {len(files)} file(s)")
        for item in files[:10]:
            print(f"   - {item.name} ({item.file_path})")

        print("\nDone.")
    except MTNCloudError as exc:
        print(f"MTN Cloud API error: {exc}")
    finally:
        if should_cleanup and upload_path and upload_path.exists():
            try:
                upload_path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    main()
