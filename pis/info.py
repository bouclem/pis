"""Show a package's manifest details from the repo (without installing)."""

from __future__ import annotations

from pathlib import Path

from pis import colors
from pis.github import FetchError, fetch_manifest_text
from pis.manifest import ManifestError, parse_manifest_text


class InfoError(Exception):
    pass


def info(name: str, show_changelog: bool = True) -> int:
    """Fetch and display a package's pis.toml from the repo.

    If *show_changelog* is True and the package has a CHANGELOG.md installed
    locally, show recent entries.
    """
    try:
        text = fetch_manifest_text(name)
        manifest = parse_manifest_text(text)
    except (FetchError, ManifestError) as exc:
        raise InfoError(str(exc)) from exc

    print(colors.header(f"  {manifest['name']}"))
    print(f"  version:       {manifest['version']}")
    print(f"  description:   {manifest['description'] or '(none)'}")
    from pis.constraints import format_dep
    deps = manifest["dependencies"]
    dep_strs = [format_dep(d) for d in deps]
    print(f"  dependencies:  {', '.join(dep_strs) if dep_strs else '(none)'}")
    checksums = manifest.get("checksums", {})
    if checksums:
        print(f"  checksums:     {len(checksums)} file(s) verified")
    else:
        print(f"  checksums:     (none)")
    scripts = manifest.get("scripts", {})
    if scripts:
        print(f"  scripts:")
        for sname, target in scripts.items():
            print(f"    {sname:<16} -> {target}")
    else:
        print(f"  scripts:       (none)")

    # show changelog if available locally
    if show_changelog:
        from pis.config import PACKAGES_DIR
        changelog_path = PACKAGES_DIR / name / "CHANGELOG.md"
        if changelog_path.is_file():
            print()
            _print_changelog(changelog_path)

    return 0


def _print_changelog(path: Path, max_lines: int = 20) -> None:
    """Print the first few lines of a package's CHANGELOG.md."""
    print(colors.header("  CHANGELOG:"))
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines[:max_lines]:
        print(f"  {line}")
    if len(lines) > max_lines:
        print(f"  ... ({len(lines) - max_lines} more lines)")
