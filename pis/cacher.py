"""Offline cache for downloaded package zips.

Zips are cached at ~/.pis/cache/<name>-<version>.zip. On install, pis checks
the cache first — if a matching version is present, it uses the cached zip
instead of re-downloading.

`pis cache list`  — show cached zips
`pis cache clear` — remove all cached zips
`pis cache clear <name>` — remove cached zips for one package
"""

from __future__ import annotations

from pathlib import Path

from pis.config import CACHE_DIR


def cache_path(name: str, version: str) -> Path:
    """Return the cache path for a specific package + version."""
    return CACHE_DIR / f"{name}-{version}.zip"


def get_cached(name: str, version: str) -> Path | None:
    """Return the cached zip path if it exists, else None."""
    p = cache_path(name, version)
    return p if p.is_file() else None


def set_cached(name: str, version: str, data: bytes) -> Path:
    """Write zip bytes to cache and return the path."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = cache_path(name, version)
    p.write_bytes(data)
    return p


def list_cache() -> list[tuple[str, str, int]]:
    """List cached zips. Returns (name, version, size_bytes) tuples."""
    if not CACHE_DIR.is_dir():
        return []
    results: list[tuple[str, str, int]] = []
    for f in sorted(CACHE_DIR.iterdir()):
        if f.is_file() and f.name.endswith(".zip"):
            # name format: <name>-<version>.zip
            stem = f.stem  # e.g. "hello-0.1.0"
            # split on last dash to separate name and version
            if "-" in stem:
                name, version = stem.rsplit("-", 1)
            else:
                name, version = stem, ""
            results.append((name, version, f.stat().st_size))
    return results


def clear_cache(name: str | None = None) -> int:
    """Clear cache. If *name* given, only clear that package. Returns count removed."""
    if not CACHE_DIR.is_dir():
        return 0
    removed = 0
    for f in CACHE_DIR.iterdir():
        if not f.is_file() or not f.name.endswith(".zip"):
            continue
        if name is None or f.name.startswith(f"{name}-"):
            f.unlink()
            removed += 1
    return removed
