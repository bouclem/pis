"""Search available packages in the pis repo via index.json (no API)."""

from __future__ import annotations

from pis.github import FetchError, fetch_index


class SearchError(Exception):
    pass


def search(query: str = "") -> int:
    """List packages in the repo whose name contains *query*.

    Empty query lists everything. Returns the number of matches shown.
    Reads packages/index.json via raw URL — zero GitHub API calls.
    """
    try:
        all_pkgs = fetch_index()
    except FetchError as exc:
        raise SearchError(str(exc)) from exc

    q = query.lower()
    matches = [p for p in all_pkgs if q in p.lower()] if q else all_pkgs

    if not matches:
        if query:
            print(f"  no packages matching '{query}'")
        else:
            print("  no packages in the repo")
        return 0

    print(f"  {'Name':<30}  Available")
    print("  " + "-" * 42)
    for name in sorted(matches):
        print(f"  {name:<30}  yes")
    print(f"\n  {len(matches)} package(s) found")
    return len(matches)
