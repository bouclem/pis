"""Update installed packages and pis itself to the latest repo version.

`pis update <name>` checks the repo's current version of *name* (by fetching
its pis.toml via raw URL) and reinstalls if the version differs.

`pis update` (no args) updates all installed packages AND pis itself.
`pis update --all` updates all installed packages only.
"""

from __future__ import annotations

import subprocess
import sys

from pis import colors
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


def update(
    name: str,
    force: bool = False,
    offline: bool = False,
) -> bool:
    """Update a single package. Returns True if updated, False if up-to-date.

    *force* reinstalls even if versions match (re-download).
    *offline* uses cache only, never downloads.
    """
    reg = _load_registry()
    if name not in reg:
        raise UpdateError(f"'{name}' is not installed")

    installed_ver = reg[name].get("version", "")
    print(colors.info(f"  checking {name} (installed: {installed_ver})..."))

    try:
        repo_ver = _get_repo_version(name)
    except UpdateError as exc:
        raise UpdateError(f"could not fetch repo version for {name}: {exc}") from exc

    if repo_ver == installed_ver and not force:
        print(colors.dim(f"  {name} is already up to date ({installed_ver})"))
        return False

    print(colors.info(f"  updating {name} {installed_ver} -> {repo_ver}"))
    try:
        install(name, force=True, offline=offline)
    except InstallError as exc:
        raise UpdateError(str(exc)) from exc
    return True


def update_all(offline: bool = False) -> int:
    """Update every installed package. Returns count of packages updated."""
    reg = _load_registry()
    if not reg:
        print(colors.dim("  no packages installed"))
        return 0

    updated = 0
    for name in sorted(reg):
        try:
            if update(name, offline=offline):
                updated += 1
        except UpdateError as exc:
            print(colors.warning(f"  ! {exc}"))
    print(f"\n  {updated} package(s) updated")
    return updated


def update_default(offline: bool = False) -> int:
    """Default update: all packages + pis itself.

    Called when `pis update` is run with no arguments.
    """
    pkg_updated = update_all(offline=offline)

    # self-update pis
    print(colors.info("  checking pis manager version..."))
    try:
        self_updated = _self_update(offline=offline)
    except UpdateError as exc:
        print(colors.warning(f"  ! could not self-update: {exc}"))
        self_updated = 0

    return pkg_updated + self_updated


def _self_update(offline: bool = False) -> int:
    """Check if pis itself has a new version and self-update.

    Compares the installed pis version against the repo's pyproject.toml.
    If newer, runs `pip install` from the repo URL.
    """
    from pis import __version__
    from pis.config import REPO_OWNER, REPO_NAME

    # fetch pyproject.toml from repo to check version
    raw_url = (
        f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/pyproject.toml"
    )
    try:
        from pis.github import _download
        data = _download(raw_url)
        text = data.decode("utf-8")
    except FetchError as exc:
        raise UpdateError(f"could not fetch pyproject.toml: {exc}") from exc

    # extract version from pyproject.toml
    import re
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        raise UpdateError("could not parse version from pyproject.toml")
    repo_ver = m.group(1)

    if repo_ver == __version__:
        print(colors.dim(f"  pis is already up to date ({__version__})"))
        return 0

    if offline:
        raise UpdateError(
            f"pis {repo_ver} available but offline mode is on"
        )

    print(colors.info(f"  updating pis {__version__} -> {repo_ver}"))
    repo_url = f"git+https://github.com/{REPO_OWNER}/{REPO_NAME}.git"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", repo_url],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise UpdateError(f"pip install failed: {result.stderr.strip()}")
        print(colors.success(f"  pis updated to {repo_ver}"))
        print(colors.dim("  restart your shell to use the new version"))
        return 1
    except FileNotFoundError as exc:
        raise UpdateError(f"pip not found: {exc}") from exc
