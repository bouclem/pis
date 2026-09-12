"""Update installed packages to their latest repo version.

`pis update <name>` checks the repo's current version of *name* (by fetching
its pis.toml via raw URL) and reinstalls if the version differs.

`pis update --all` iterates over every installed package.
"""

from __future__ import annotations

from pis.github import FetchError, fetch_manifest_text
from pis.installer import InstallError, _load_registry, install
from pis.manifest import ManifestError, parse_manifest_text


class UpdateError(Exception):
    pass


def _get_repo_version(name: str) -> str:
    """Fetch the package's pis.toml from the repo and return its version."""
    try:
        text = fetch_manifest_text(name)
        manifest = parse_manifest_text(text)
    except (FetchError, ManifestError) as exc:
        raise UpdateError(str(exc)) from exc
    return manifest["version"]


def update(name: str, force: bool = False) -> bool:
    """Update a single package. Returns True if updated, False if up-to-date.

    *force* reinstalls even if versions match (re-download).
    """
    reg = _load_registry()
    if name not in reg:
        raise UpdateError(f"'{name}' is not installed")

    installed_ver = reg[name].get("version", "")
    print(f"  checking {name} (installed: {installed_ver})...")

    try:
        repo_ver = _get_repo_version(name)
    except UpdateError as exc:
        raise UpdateError(f"could not fetch repo version for {name}: {exc}") from exc

    if repo_ver == installed_ver and not force:
        print(f"  {name} is already up to date ({installed_ver})")
        return False

    print(f"  updating {name} {installed_ver} -> {repo_ver}")
    try:
        install(name, force=True)
    except InstallError as exc:
        raise UpdateError(str(exc)) from exc
    return True


def update_all() -> int:
    """Update every installed package. Returns count of packages updated."""
    reg = _load_registry()
    if not reg:
        print("  no packages installed")
        return 0

    updated = 0
    for name in sorted(reg):
        try:
            if update(name):
                updated += 1
        except UpdateError as exc:
            print(f"  ! {exc}")
    print(f"\n  {updated} package(s) updated")
    return updated
