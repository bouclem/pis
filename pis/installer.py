"""Install packages from the pis repo into ~/.pis/packages/.

Install flow:
  1. Make sure local dirs exist.
  2. If already installed at the same version, skip (unless --force).
  3. Download the per-package zip (packages/<name>/<name>.zip) via raw URL.
     Uses cache if available (unless --no-cache).
  4. Extract + read the package's pis.toml manifest.
  5. Verify checksums if declared in the manifest.
  6. Check version constraints on dependencies.
  7. Recursively install dependencies first.
  8. Register the package in installed.json.
  9. Best-effort: drop a pis.pth into user site-packages.
 10. Write script wrappers to ~/.pis/bin/.
"""

from __future__ import annotations

import json
import site
import sys
from pathlib import Path

from pis import colors
from pis.config import BIN_DIR, PACKAGES_DIR, REGISTRY_FILE, ensure_dirs, PTH_NAME
from pis.constraints import Dependency, check_version, format_dep
from pis.github import FetchError, fetch_package_zip, verify_checksums
from pis.manifest import ManifestError, load_manifest


class InstallError(Exception):
    pass


# --- registry helpers -------------------------------------------------------

def _load_registry() -> dict:
    if not REGISTRY_FILE.is_file():
        return {}
    try:
        with REGISTRY_FILE.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_registry(reg: dict) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REGISTRY_FILE.open("w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, sort_keys=True)


# --- pth handling -----------------------------------------------------------

def _ensure_pth() -> None:
    """Best-effort: write pis.pth into the user site-packages so that
    packages installed under PACKAGES_DIR become importable.
    """
    user_site = site.getusersitepackages()
    if not user_site:
        print(colors.warning("  ! could not determine user site-packages; skipping .pth"))
        return
    pth_path = Path(user_site) / PTH_NAME
    try:
        Path(user_site).mkdir(parents=True, exist_ok=True)
        pth_path.write_text(str(PACKAGES_DIR) + "\n", encoding="utf-8")
    except OSError as exc:
        print(colors.warning(f"  ! could not write {pth_path}: {exc}"))
        print(colors.warning(f"  ! add this to PYTHONPATH manually: {PACKAGES_DIR}"))


# --- install ----------------------------------------------------------------

def install(
    name: str,
    force: bool = False,
    _seen: set | None = None,
    progress: bool = False,
    use_cache: bool = True,
    parent_dep: Dependency | None = None,
) -> bool:
    """Install *name* from the repo. Returns True if installed, False if
    skipped (already present at same version and not forced).

    *force* re-downloads even if the version matches.
    *_seen* guards against dependency cycles.
    *progress* shows a download progress bar.
    *use_cache* uses cached zips when available.
    *parent_dep* is the Dependency object from the parent's manifest (for
    version constraint checking).
    """
    if _seen is None:
        _seen = set()
    if name in _seen:
        return False
    _seen.add(name)

    ensure_dirs()
    reg = _load_registry()

    # if this is a dependency, check version constraint against installed
    if parent_dep and parent_dep.constraints and name in reg:
        installed_ver = reg[name].get("version", "")
        if installed_ver and not check_version(installed_ver, parent_dep):
            raise InstallError(
                f"installed {name}=={installed_ver} does not satisfy "
                f"{format_dep(parent_dep)}"
            )

    # fetch + extract into a temp staging area first
    staging = PACKAGES_DIR / ".staging"
    if staging.exists():
        _rm_tree(staging)
    staging.mkdir(parents=True)

    print(colors.info(f"  fetching '{name}' from repo..."))
    try:
        pkg_dir = fetch_package_zip(
            name, staging,
            progress=progress,
            use_cache=use_cache,
            cached_version=None,  # don't know version yet
        )
    except FetchError as exc:
        _rm_tree(staging)
        raise InstallError(str(exc)) from exc

    try:
        manifest = load_manifest(pkg_dir)
    except ManifestError as exc:
        _rm_tree(staging)
        raise InstallError(str(exc)) from exc

    # if this is a dependency, check version constraint against fetched version
    if parent_dep and parent_dep.constraints:
        if not check_version(manifest["version"], parent_dep):
            _rm_tree(staging)
            raise InstallError(
                f"{name}=={manifest['version']} does not satisfy "
                f"{format_dep(parent_dep)}"
            )

    # verify checksums if declared in the manifest
    if manifest.get("checksums"):
        try:
            verify_checksums(pkg_dir, manifest["checksums"])
        except FetchError as exc:
            _rm_tree(staging)
            raise InstallError(f"checksum verification failed: {exc}") from exc
        print(colors.success(f"  checksums verified ({len(manifest['checksums'])} file(s))"))

    # already installed?
    existing = reg.get(name)
    if existing and existing.get("version") == manifest["version"] and not force:
        print(colors.dim(f"  {name}=={manifest['version']} already installed (skip)"))
        _rm_tree(staging)
        return False

    # dependencies first (with version constraint checking)
    for dep in manifest["dependencies"]:
        dep_name = dep.name
        if dep_name not in reg or (force and dep_name not in _seen):
            dep_label = format_dep(dep) if dep.constraints else dep_name
            print(colors.info(f"  dependency: {dep_label}"))
            install(
                dep_name,
                force=force,
                _seen=_seen,
                progress=progress,
                use_cache=use_cache,
                parent_dep=dep,
            )
            reg = _load_registry()

    # move staged folder into place
    final_dir = PACKAGES_DIR / name
    if final_dir.exists():
        _rm_tree(final_dir)
    pkg_dir.rename(final_dir)
    _rm_tree(staging)

    # serialize dependencies as strings for the registry
    reg_deps = [format_dep(d) for d in manifest["dependencies"]]

    reg[name] = {
        "version": manifest["version"],
        "description": manifest["description"],
        "dependencies": reg_deps,
        "scripts": manifest.get("scripts", {}),
    }
    _save_registry(reg)
    _ensure_pth()
    _write_script_wrappers(name, manifest.get("scripts", {}))

    print(colors.success(f"  installed {name}=={manifest['version']}"))
    return True


# --- script wrappers --------------------------------------------------------

def _write_script_wrappers(pkg_name: str, scripts: dict[str, str]) -> None:
    """Write executable wrappers for declared [scripts] into ~/.pis/bin/."""
    if not scripts:
        return
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    for script_name, target in scripts.items():
        if ":" not in target:
            print(colors.warning(f"  ! invalid script '{script_name}': {target}"))
            continue
        module, func = target.split(":", 1)
        py_wrapper = BIN_DIR / f"{script_name}.py"
        py_content = (
            f"import sys\n"
            f"from {module} import {func}\n"
            f"sys.exit({func}())\n"
        )
        py_wrapper.write_text(py_content, encoding="utf-8")

        bat_wrapper = BIN_DIR / f"{script_name}.bat"
        bat_content = f"@echo off\npython \"{py_wrapper}\" %*\n"
        bat_wrapper.write_text(bat_content, encoding="utf-8")

        sh_wrapper = BIN_DIR / script_name
        sh_content = f"#!/bin/sh\nexec python \"{py_wrapper}\" \"$@\"\n"
        sh_wrapper.write_text(sh_content, encoding="utf-8")

        print(colors.info(f"  script: {script_name} -> {target}"))
    print(colors.warning(f"  ! add {BIN_DIR} to your PATH to run scripts directly"))


def _rm_tree(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        for child in path.iterdir():
            _rm_tree(child)
        path.rmdir()
    else:
        path.unlink()
