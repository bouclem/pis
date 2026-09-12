"""Build a package zip and update the repo's index.json.

`pis build <name>`:
  1. Reads packages/<name>/pis.toml from the local repo working copy.
  2. Zips all files in packages/<name>/ (except <name>.zip itself) into
     packages/<name>/<name>.zip.
  3. Updates packages/index.json to include <name>.

This is run locally (in the repo working copy) before committing/pushing.
"""

from __future__ import annotations

import json
from pathlib import Path
import zipfile

from pis.config import PACKAGES_SUBDIR
from pis.manifest import ManifestError, load_manifest


class BuildError(Exception):
    pass


# Files/patterns to exclude from the zip.
_EXCLUDE = {".gitkeep", "index.json"}
_EXCLUDE_DIRS = {"__pycache__"}


def build(name: str, repo_root: Path | None = None) -> Path:
    """Build <name>.zip from packages/<name>/ and update index.json.

    *repo_root* defaults to the current working directory.
    Returns the path to the created zip.
    """
    if repo_root is None:
        repo_root = Path.cwd()

    pkg_dir = repo_root / PACKAGES_SUBDIR / name
    if not pkg_dir.is_dir():
        raise BuildError(f"package folder not found: {pkg_dir}")

    # validate manifest
    try:
        manifest = load_manifest(pkg_dir)
    except ManifestError as exc:
        raise BuildError(str(exc)) from exc

    if manifest["name"] != name:
        raise BuildError(
            f"manifest name '{manifest['name']}' != folder name '{name}'"
        )

    zip_name = f"{name}.zip"
    zip_path = pkg_dir / zip_name

    # collect files to zip (everything except the zip itself + excludes)
    files: list[Path] = []
    for f in sorted(pkg_dir.rglob("*")):
        if f.is_file():
            # skip files inside excluded directories
            parts = f.relative_to(pkg_dir).parts
            if any(p in _EXCLUDE_DIRS for p in parts):
                continue
            rel = f.relative_to(pkg_dir).as_posix()
            if rel == zip_name or rel in _EXCLUDE:
                continue
            files.append(f)

    if not files:
        raise BuildError(f"no files to zip in {pkg_dir}")

    # write zip
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            rel = f.relative_to(pkg_dir).as_posix()
            zf.write(f, arcname=rel)
    print(f"  built {zip_path} ({len(files)} file(s))")

    # update index.json
    _update_index(repo_root, name)
    return zip_path


def _update_index(repo_root: Path, name: str) -> None:
    """Add *name* to packages/index.json (create if missing, keep sorted)."""
    index_path = repo_root / PACKAGES_SUBDIR / "index.json"
    if index_path.is_file():
        try:
            with index_path.open("r", encoding="utf-8") as fh:
                index = json.load(fh)
        except (json.JSONDecodeError, OSError):
            index = {"packages": []}
    else:
        index = {"packages": []}

    pkgs = index.get("packages", [])
    if not isinstance(pkgs, list):
        pkgs = []
    if name not in pkgs:
        pkgs.append(name)
        pkgs.sort()
    index["packages"] = pkgs

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    print(f"  updated {index_path} ({len(pkgs)} package(s))")
