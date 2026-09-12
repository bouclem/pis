"""Install packages from the pis repo into ~/.pis/packages/.

Install flow:
  1. Make sure local dirs exist.
  2. If already installed at the same version, skip (unless --force).
  3. Download the per-package zip (packages/<name>/<name>.zip) via raw URL.
  4. Extract + read the package's pis.toml manifest.
  5. Verify checksums if declared in the manifest.
  6. Recursively install dependencies first.
  7. Register the package in installed.json.
  8. Best-effort: drop a pis.pth into user site-packages so packages are
     importable from a normal Python session.
"""

from __future__ import annotations

import json
import site
import sys
from pathlib import Path

from pis.config import BIN_DIR, PACKAGES_DIR, REGISTRY_FILE, ensure_dirs, PTH_NAME
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

    Failures (no user site dir, permission denied) are non-fatal — we just
    print a warning. The packages still live on disk and can be added to
    PYTHONPATH manually.
    """
    user_site = site.getusersitepackages()
    if not user_site:
        print("  ! could not determine user site-packages; skipping .pth")
        return
    pth_path = Path(user_site) / PTH_NAME
    try:
        Path(user_site).mkdir(parents=True, exist_ok=True)
        pth_path.write_text(str(PACKAGES_DIR) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"  ! could not write {pth_path}: {exc}")
        print(f"  ! add this to PYTHONPATH manually: {PACKAGES_DIR}")


# --- install ----------------------------------------------------------------

def install(
    name: str,
    force: bool = False,
    _seen: set | None = None,
    progress: bool = False,
) -> bool:
    """Install *name* from the repo. Returns True if installed, False if
    skipped (already present at same version and not forced).

    *force* re-downloads even if the version matches.
    *_seen* guards against dependency cycles.
    *progress* shows a download progress bar.
    """
    if _seen is None:
        _seen = set()
    if name in _seen:
        return False
    _seen.add(name)

    ensure_dirs()
    reg = _load_registry()

    # fetch + extract into a temp staging area first
    staging = PACKAGES_DIR / ".staging"
    if staging.exists():
        _rm_tree(staging)
    staging.mkdir(parents=True)

    print(f"  fetching '{name}' from repo...")
    try:
        pkg_dir = fetch_package_zip(name, staging, progress=progress)
    except FetchError as exc:
        _rm_tree(staging)
        raise InstallError(str(exc)) from exc

    try:
        manifest = load_manifest(pkg_dir)
    except ManifestError as exc:
        _rm_tree(staging)
        raise InstallError(str(exc)) from exc

    # verify checksums if declared in the manifest
    if manifest.get("checksums"):
        try:
            verify_checksums(pkg_dir, manifest["checksums"])
        except FetchError as exc:
            _rm_tree(staging)
            raise InstallError(f"checksum verification failed: {exc}") from exc
        print(f"  checksums verified ({len(manifest['checksums'])} file(s))")

    # already installed?
    existing = reg.get(name)
    if existing and existing.get("version") == manifest["version"] and not force:
        print(f"  {name}=={manifest['version']} already installed (skip)")
        _rm_tree(staging)
        return False

    # dependencies first
    for dep in manifest["dependencies"]:
        if dep not in reg or (force and dep not in _seen):
            print(f"  dependency: {dep}")
            install(dep, force=force, _seen=_seen, progress=progress)
            reg = _load_registry()  # refresh after dep install

    # move staged folder into place
    final_dir = PACKAGES_DIR / name
    if final_dir.exists():
        _rm_tree(final_dir)
    pkg_dir.rename(final_dir)
    _rm_tree(staging)

    reg[name] = {
        "version": manifest["version"],
        "description": manifest["description"],
        "dependencies": manifest["dependencies"],
        "scripts": manifest.get("scripts", {}),
    }
    _save_registry(reg)
    _ensure_pth()
    _write_script_wrappers(name, manifest.get("scripts", {}))

    print(f"  installed {name}=={manifest['version']}")
    return True


# --- script wrappers --------------------------------------------------------

def _write_script_wrappers(pkg_name: str, scripts: dict[str, str]) -> None:
    """Write executable wrappers for declared [scripts] into ~/.pis/bin/.

    Each script is a small .py file that imports the package and calls the
    target function. On Windows, a .bat wrapper is also created.
    """
    if not scripts:
        return
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    for script_name, target in scripts.items():
        # target format: "module:function"
        if ":" not in target:
            print(f"  ! invalid script '{script_name}': {target} (expected module:function)")
            continue
        module, func = target.split(":", 1)
        py_wrapper = BIN_DIR / f"{script_name}.py"
        py_content = (
            f"import sys\n"
            f"from {module} import {func}\n"
            f"sys.exit({func}())\n"
        )
        py_wrapper.write_text(py_content, encoding="utf-8")

        # .bat wrapper for Windows
        bat_wrapper = BIN_DIR / f"{script_name}.bat"
        bat_content = (
            f"@echo off\n"
            f'python "{py_wrapper}" %*\n'
        )
        bat_wrapper.write_text(bat_content, encoding="utf-8")

        # .sh wrapper for Unix
        sh_wrapper = BIN_DIR / script_name
        sh_content = (
            f"#!/bin/sh\n"
            f'exec python "{py_wrapper}" "$@"\n'
        )
        sh_wrapper.write_text(sh_content, encoding="utf-8")

        print(f"  script: {script_name} -> {target}")
    print(f"  ! add {BIN_DIR} to your PATH to run scripts directly")


def _rm_tree(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        for child in path.iterdir():
            _rm_tree(child)
        path.rmdir()
    else:
        path.unlink()
