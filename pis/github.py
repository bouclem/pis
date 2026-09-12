"""Raw GitHub file fetchers (no API, no rate limits).

pis fetches packages via raw.githubusercontent.com URLs:
  - Per-package zip:   packages/<name>/<name>.zip
  - Manifest:          packages/<name>/pis.toml
  - Package index:     packages/index.json

All downloads go through the shared `_download()` helper with optional
progress reporting.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable

from pis.config import (
    PACKAGES_SUBDIR,
    RAW_INDEX_URL,
    USER_AGENT,
    raw_manifest_url,
    raw_package_zip_url,
)


class FetchError(Exception):
    """Raised when a file can't be downloaded or read."""


class NotFoundError(FetchError):
    """Raised when a file returns 404 (package not found in repo)."""


class NetworkError(FetchError):
    """Raised when a download fails due to network issues."""


# Progress callback type: (bytes_downloaded, total_bytes_or_None) -> None
ProgressFn = Callable[[int, int | None], None]


def _download(url: str, progress: ProgressFn | None = None) -> bytes:
    """Download *url* and return bytes. Calls *progress* if given.

    Raises NotFoundError on 404, NetworkError on connection failures.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = resp.headers.get("Content-Length")
            total_int = int(total) if total else None
            buf = io.BytesIO()
            downloaded = 0
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                buf.write(chunk)
                downloaded += len(chunk)
                if progress:
                    progress(downloaded, total_int)
            return buf.getvalue()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise NotFoundError(f"not found: {url}") from exc
        raise NetworkError(f"HTTP {exc.code} from {url}") from exc
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        raise NetworkError(
            f"could not reach {url} (check your connection): {exc}"
        ) from exc


def _print_progress(downloaded: int, total: int | None) -> None:
    """Simple progress bar printed to stderr."""
    if total:
        pct = downloaded * 100 // total
        bar_len = 30
        filled = bar_len * pct // 100
        bar = "=" * filled + "-" * (bar_len - filled)
        sys.stderr.write(f"\r  [{bar}] {pct:3d}% ({downloaded} bytes)")
        sys.stderr.flush()
        if downloaded >= total:
            sys.stderr.write("\n")
    else:
        sys.stderr.write(f"\r  downloaded {downloaded} bytes...")
        sys.stderr.flush()


# --- Package zip ------------------------------------------------------------

def fetch_package_zip(
    name: str, dest: Path, progress: bool = False
) -> Path:
    """Download <name>.zip from the repo and extract it into *dest*.

    The zip contains the package folder contents (pis.toml + source files).
    Returns the path to the extracted package folder (dest/<name>/).
    Raises FetchError on download or zip errors.
    """
    url = raw_package_zip_url(name)
    cb = _print_progress if progress else None
    data = _download(url, progress=cb)

    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise FetchError(f"downloaded {name}.zip is not a valid zip") from exc

    pkg_dir = dest / name
    pkg_dir.mkdir(parents=True, exist_ok=True)

    for member in zf.namelist():
        # skip directory entries
        if member.endswith("/"):
            continue
        # strip any leading folder (zip may contain <name>/ prefix or not)
        parts = member.split("/")
        # if first part is the package name, strip it
        if parts and parts[0] == name:
            rel_parts = parts[1:]
        else:
            rel_parts = parts
        if not rel_parts:
            continue
        rel = "/".join(rel_parts)
        out_path = pkg_dir / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(member) as src, open(out_path, "wb") as dst:
            dst.write(src.read())

    if not (pkg_dir / "pis.toml").is_file():
        raise FetchError(
            f"extracted zip for '{name}' has no pis.toml"
        )
    return pkg_dir


# --- Manifest ---------------------------------------------------------------

def fetch_manifest_text(name: str) -> str:
    """Fetch a package's pis.toml as text (for `pis info`)."""
    data = _download(raw_manifest_url(name))
    return data.decode("utf-8")


# --- Index ------------------------------------------------------------------

def fetch_index() -> list[str]:
    """Fetch packages/index.json from the repo. Returns list of package names."""
    data = _download(RAW_INDEX_URL)
    try:
        obj = json.loads(data)
    except json.JSONDecodeError as exc:
        raise FetchError("could not parse index.json") from exc
    if not isinstance(obj, dict):
        raise FetchError("index.json is not a JSON object")
    pkgs = obj.get("packages", [])
    if not isinstance(pkgs, list):
        raise FetchError("index.json 'packages' is not a list")
    return [str(p) for p in pkgs]


# --- Checksum verification --------------------------------------------------

def verify_checksums(pkg_dir: Path, checksums: dict[str, str]) -> None:
    """Verify that files in *pkg_dir* match their declared sha256 checksums.

    *checksums* maps relative filename -> expected sha256 hex string.
    Raises FetchError on any mismatch. Files not in *checksums* are skipped.
    """
    for rel_path, expected_sha in checksums.items():
        file_path = pkg_dir / rel_path
        if not file_path.is_file():
            raise FetchError(
                f"checksum: file '{rel_path}' listed in checksums not found"
            )
        actual = _sha256(file_path)
        if actual != expected_sha.lower():
            raise FetchError(
                f"checksum mismatch for '{rel_path}': "
                f"expected {expected_sha}, got {actual}"
            )


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
