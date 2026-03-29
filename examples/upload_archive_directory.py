"""
MTN Cloud SDK - Upload an Entire Local Directory to Archive Bucket
==================================================================

Run with:
    export MTN_CLOUD_TOKEN="your-token"
    export MTN_ARCHIVE_BUCKET="my-existing-archive-bucket"
    export MTN_UPLOAD_DIR="./local-folder-to-upload"
    python examples/upload_archive_directory.py

Optional env:
    MTN_UPLOAD_DEST_PATH="/"      # destination path inside archive bucket
    MTN_UPLOAD_RECURSIVE="true"   # true/false
    MTN_UPLOAD_DRY_RUN="false"    # true/false (preflight only)
    MTN_UPLOAD_STRICT="false"     # true/false (abort upload if preflight skips exist)
"""

from __future__ import annotations

import os
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


def main() -> None:
    print("MTN Cloud - Upload Directory to Archive Bucket")
    print("=" * 60)

    try:
        bucket_name = _required_env("MTN_ARCHIVE_BUCKET")
        upload_dir = Path(_required_env("MTN_UPLOAD_DIR")).expanduser().resolve()
    except ValueError as exc:
        print(f"Configuration error: {exc}")
        return

    upload_dest_path = os.getenv("MTN_UPLOAD_DEST_PATH", "/").strip() or "/"
    recursive = _env_bool("MTN_UPLOAD_RECURSIVE", default=True)
    dry_run = _env_bool("MTN_UPLOAD_DRY_RUN", default=False)
    strict = _env_bool("MTN_UPLOAD_STRICT", default=False)

    cloud = MTNCloud()

    try:
        upload_summary = cloud.archive_buckets.upload_directory(
            bucket_name=bucket_name,
            remote_path=upload_dest_path,
            local_directory=upload_dir,
            recursive=recursive,
            dry_run=dry_run,
            strict=strict,
        )
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"Input error: {exc}")
        return
    except MTNCloudError as exc:
        print(f"API error: {exc}")
        return

    print(
        f"Scanned {upload_summary.scanned_count}, "
        f"eligible {upload_summary.eligible_count}, "
        f"skipped {upload_summary.skipped_count}, "
        f"uploaded {upload_summary.uploaded_count}, "
        f"failed {upload_summary.failed_count}."
    )
    if upload_summary.aborted:
        print("Upload phase aborted by strict preflight policy.")

    if upload_summary.uploaded_files:
        print("Uploaded files:")
    for item in upload_summary.uploaded_files[:20]:
        print(f"  - {item.name} ({item.file_path})")

    if upload_summary.skipped_files:
        print("Skipped files (preflight):")
    for skipped in upload_summary.skipped_files[:20]:
        print(f"  - {skipped.local_path} -> {skipped.remote_path} | {skipped.reason}")

    if upload_summary.failed_files:
        print("Failed files:")
    for failed in upload_summary.failed_files[:20]:
        print(f"  - {failed.local_path} -> {failed.remote_path} | {failed.reason}")


if __name__ == "__main__":
    main()
