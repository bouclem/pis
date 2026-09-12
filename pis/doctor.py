"""pis doctor — diagnose install / pth / path / bin issues.

Runs a series of checks and reports each as OK / WARN / FAIL with
suggestions for fixing problems.
"""

from __future__ import annotations

import json
import os
import site
import sys
from pathlib import Path

from pis import colors
from pis.config import BIN_DIR, PACKAGES_DIR, REGISTRY_FILE, PTH_NAME


class DoctorError(Exception):
    pass


def doctor() -> int:
    """Run all diagnostic checks. Returns count of failures."""
    failures = 0
    warnings = 0

    print(colors.header("  pis doctor — diagnostics"))
    print()

    # 1. PIS_HOME dirs exist
    failures += _check_dir(PACKAGES_DIR, "packages dir")
    failures += _check_dir(BIN_DIR, "bin dir")

    # 2. registry is valid
    reg_ok, reg = _check_registry()
    if reg_ok:
        print(colors.success(f"  [OK]   registry ({len(reg)} package(s))"))
    else:
        print(colors.error(f"  [FAIL] registry is invalid or missing"))
        failures += 1
        reg = {}

    # 3. pis.pth in site-packages
    warnings += _check_pth()

    # 4. ~/.pis/bin on PATH
    warnings += _check_bin_path()

    # 5. installed packages exist on disk
    if reg:
        for name in sorted(reg):
            pkg_dir = PACKAGES_DIR / name
            if pkg_dir.is_dir():
                print(colors.success(f"  [OK]   {name}/ on disk"))
            else:
                print(colors.error(f"  [FAIL] {name}/ missing from disk"))
                failures += 1
    else:
        print(colors.dim("  [--]   no installed packages to check"))

    # summary
    print()
    if failures:
        print(colors.error(f"  {failures} failure(s), {warnings} warning(s)"))
    elif warnings:
        print(colors.warning(f"  all checks passed, {warnings} warning(s)"))
    else:
        print(colors.success("  all checks passed, no issues found"))

    return failures


def _check_dir(path: Path, label: str) -> int:
    if path.is_dir():
        print(colors.success(f"  [OK]   {label}: {path}"))
        return 0
    else:
        print(colors.error(f"  [FAIL] {label} missing: {path}"))
        return 1


def _check_registry() -> tuple[bool, dict]:
    if not REGISTRY_FILE.is_file():
        return False, {}
    try:
        with REGISTRY_FILE.open("r", encoding="utf-8") as fh:
            reg = json.load(fh)
        if not isinstance(reg, dict):
            return False, {}
        return True, reg
    except (json.JSONDecodeError, OSError):
        return False, {}


def _check_pth() -> int:
    user_site = site.getusersitepackages()
    if not user_site:
        print(colors.warning(f"  [WARN] could not determine user site-packages"))
        return 1
    pth_path = Path(user_site) / PTH_NAME
    if not pth_path.is_file():
        print(colors.warning(f"  [WARN] {PTH_NAME} not in site-packages"))
        print(colors.dim(f"        run `pis install <any-package>` to create it"))
        return 1
    content = pth_path.read_text(encoding="utf-8").strip()
    if str(PACKAGES_DIR) in content:
        print(colors.success(f"  [OK]   {PTH_NAME} -> {PACKAGES_DIR}"))
        return 0
    else:
        print(colors.warning(f"  [WARN] {PTH_NAME} points to: {content}"))
        print(colors.dim(f"        expected: {PACKAGES_DIR}"))
        return 1


def _check_bin_path() -> int:
    bin_str = str(BIN_DIR)
    path_parts = os.environ.get("PATH", "").split(os.pathsep)
    if bin_str in path_parts:
        print(colors.success(f"  [OK]   {BIN_DIR} on PATH"))
        return 0
    else:
        print(colors.warning(f"  [WARN] {BIN_DIR} not on PATH"))
        print(colors.dim(f"        add it to PATH to run pis scripts directly"))
        return 1
