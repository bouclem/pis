"""List installed pis packages."""

from __future__ import annotations

from pis.installer import _load_registry


def list_installed() -> int:
    """Print installed packages. Returns count printed."""
    reg = _load_registry()
    if not reg:
        print("  no packages installed")
        return 0

    # column widths
    name_w = max(len(n) for n in reg) | len("Name")
    ver_w = max(len(v.get("version", "")) for v in reg.values()) | len("Version")

    header = f"  {'Name':<{name_w}}  {'Version':<{ver_w}}  Description"
    print(header)
    print("  " + "-" * (name_w + ver_w + 16))
    for name in sorted(reg):
        meta = reg[name]
        ver = meta.get("version", "")
        desc = meta.get("description", "")
        print(f"  {name:<{name_w}}  {ver:<{ver_w}}  {desc}")
    return len(reg)
