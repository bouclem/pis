"""Uninstall packages from ~/.pis/packages/."""

from __future__ import annotations

from pathlib import Path

from pis.config import PACKAGES_DIR, REGISTRY_FILE
from pis.installer import _load_registry, _rm_tree, _save_registry


class UninstallError(Exception):
    pass


def uninstall(name: str) -> bool:
    """Remove *name* from disk and the registry. Returns True if removed."""
    reg = _load_registry()

    pkg_dir = PACKAGES_DIR / name
    removed_from_disk = False
    if pkg_dir.exists():
        _rm_tree(pkg_dir)
        removed_from_disk = True

    removed_from_reg = False
    if name in reg:
        del reg[name]
        _save_registry(reg)
        removed_from_reg = True

    if not removed_from_disk and not removed_from_reg:
        raise UninstallError(f"'{name}' is not installed")

    print(f"  uninstalled {name}")
    return True
