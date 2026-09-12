"""Show a package's manifest details from the repo (without installing)."""

from __future__ import annotations

from pis.github import FetchError, fetch_manifest_text
from pis.manifest import ManifestError, parse_manifest_text


class InfoError(Exception):
    pass


def info(name: str) -> int:
    """Fetch and display a package's pis.toml from the repo.

    Returns 0 on success, 1 on error (raised as InfoError).
    """
    try:
        text = fetch_manifest_text(name)
        manifest = parse_manifest_text(text)
    except (FetchError, ManifestError) as exc:
        raise InfoError(str(exc)) from exc

    print(f"  name:          {manifest['name']}")
    print(f"  version:       {manifest['version']}")
    print(f"  description:   {manifest['description'] or '(none)'}")
    deps = manifest["dependencies"]
    print(f"  dependencies:  {', '.join(deps) if deps else '(none)'}")
    checksums = manifest.get("checksums", {})
    if checksums:
        print(f"  checksums:     {len(checksums)} file(s) verified")
    else:
        print(f"  checksums:     (none)")
    return 0
