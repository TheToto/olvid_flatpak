#!/usr/bin/env python3
"""Check Olvid's RSS feed for a new Linux desktop release and update Flatpak files."""

from __future__ import annotations

import argparse
import email.utils
import hashlib
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

RSS_URL = "https://olvid.io/rss/en.xml"
TARBALL_URL_TEMPLATE = "https://static.olvid.io/linux/olvid-{version}.tar.gz"
ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT_DIR / "io.olvid.Olvid.yml"
METAINFO_PATH = ROOT_DIR / "io.olvid.Olvid.metainfo.xml"


def fetch_latest_rss_release() -> tuple[str, str]:
    """Return (version, iso_date) for the latest Windows/Linux release in Olvid RSS."""
    req = urllib.request.Request(RSS_URL, headers={"User-Agent": "olvid-flatpak-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        xml_bytes = resp.read()

    root = ET.fromstring(xml_bytes)
    for item in root.findall("./channel/item"):
        guid = (item.findtext("guid") or "").strip()
        if guid.startswith("windows_"):
            version = guid.removeprefix("windows_").strip()
            pub_date_raw = (item.findtext("pubDate") or "").strip()
            iso_date = ""
            if pub_date_raw:
                dt = email.utils.parsedate_to_datetime(pub_date_raw)
                iso_date = dt.date().isoformat()
            return version, iso_date

    raise RuntimeError("No item with guid starting with 'windows_' found in RSS feed")


def read_current_version(manifest_text: str) -> str:
    """Extract current version from the tarball URL in io.olvid.Olvid.yml."""
    match = re.search(
        r"url:\s*https://static\.olvid\.io/linux/olvid-([0-9A-Za-z._-]+)\.tar\.gz",
        manifest_text,
    )
    if not match:
        raise RuntimeError(f"Could not find Olvid tarball URL in {MANIFEST_PATH}")
    return match.group(1)


def compute_tarball_sha256(url: str) -> str:
    """Stream-download tarball and return its hex SHA256 digest."""
    req = urllib.request.Request(url, headers={"User-Agent": "olvid-flatpak-updater/1.0"})
    digest = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=120) as resp:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def update_manifest(manifest_text: str, new_version: str, new_sha256: str) -> str:
    """Replace the tarball url and sha256 in io.olvid.Olvid.yml."""
    new_url = TARBALL_URL_TEMPLATE.format(version=new_version)
    updated, url_count = re.subn(
        r"(url:\s*)https://static\.olvid\.io/linux/olvid-[0-9A-Za-z._-]+\.tar\.gz",
        rf"\g<1>{new_url}",
        manifest_text,
        count=1,
    )
    if url_count != 1:
        raise RuntimeError("Failed to update tarball URL in manifest")

    updated, sha_count = re.subn(
        r"(sha256:\s*)[0-9a-fA-F]{64}",
        rf"\g<1>{new_sha256}",
        updated,
        count=1,
    )
    if sha_count != 1:
        raise RuntimeError("Failed to update sha256 in manifest")

    return updated


def update_metainfo(metainfo_text: str, new_version: str, iso_date: str) -> str:
    """Prepend a <release> entry to io.olvid.Olvid.metainfo.xml if not already present."""
    if re.search(rf'<release\s+version="{re.escape(new_version)}"', metainfo_text):
        return metainfo_text

    date_attr = f' date="{iso_date}"' if iso_date else ""
    release_tag = f'    <release version="{new_version}"{date_attr} />'
    updated, count = re.subn(
        r"(<releases>\s*\n)",
        rf"\g<1>{release_tag}\n",
        metainfo_text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Failed to insert <release> into metainfo XML")
    return updated


def write_github_output(updated: bool, old_version: str, new_version: str) -> None:
    """Write step outputs to $GITHUB_OUTPUT when running in GitHub Actions."""
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(f"updated={'true' if updated else 'false'}\n")
        f.write(f"old_version={old_version}\n")
        f.write(f"new_version={new_version}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Check for updates without modifying files")
    parser.add_argument("--version", help="Override target version instead of reading RSS")
    parser.add_argument("--force", action="store_true", help="Update files even if version matches current")
    parser.add_argument("--github-output", action="store_true", help="Write outputs to $GITHUB_OUTPUT")
    args = parser.parse_args()

    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    current_version = read_current_version(manifest_text)

    if args.version:
        target_version = args.version.strip()
        target_date = ""
    else:
        target_version, target_date = fetch_latest_rss_release()

    if target_version == current_version and not args.force:
        print(f"Already up to date: {current_version}")
        if args.github_output:
            write_github_output(False, current_version, target_version)
        return 0

    print(f"Update available: {current_version} -> {target_version} (date: {target_date or 'unknown'})")
    if args.dry_run:
        if args.github_output:
            write_github_output(True, current_version, target_version)
        return 0

    tarball_url = TARBALL_URL_TEMPLATE.format(version=target_version)
    print(f"Downloading {tarball_url} to compute SHA256...")
    sha256 = compute_tarball_sha256(tarball_url)
    print(f"SHA256: {sha256}")

    MANIFEST_PATH.write_text(update_manifest(manifest_text, target_version, sha256), encoding="utf-8")
    metainfo_text = METAINFO_PATH.read_text(encoding="utf-8")
    METAINFO_PATH.write_text(update_metainfo(metainfo_text, target_version, target_date), encoding="utf-8")

    print(f"Updated {MANIFEST_PATH.name} and {METAINFO_PATH.name} to {target_version}")
    if args.github_output:
        write_github_output(True, current_version, target_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
