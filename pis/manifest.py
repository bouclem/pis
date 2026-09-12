"""Parse pis.toml manifests for packages.

A pis.toml is intentionally tiny. Recognized keys (under [package]):

    name        = "hello"            # required, package name
    version     = "0.1.0"            # required
    description = "a fun package"    # optional
    dependencies = ["foo", "bar>=1.0"]  # optional, pis package names
                                         # with optional version constraints

Optional [checksums] table (filename -> sha256 hex):
    [checksums]
    "hello.py" = "abc123..."

Optional [scripts] table (script name -> "module:function"):
    [scripts]
    greet = "hello:main"

Unknown keys are ignored (forward-compatible). Missing required keys raise
ManifestError with a clear message.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pis.constraints import Dependency, parse_dependency

try:  # Python 3.11+
    import tomllib  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - older Python fallback
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError as e:
        raise RuntimeError(
            "pis needs Python 3.11+ (tomllib) or the 'tomli' package."
        ) from e


MANIFEST_NAME = "pis.toml"

REQUIRED_KEYS = ("name", "version")


class ManifestError(Exception):
    """Raised when a pis.toml is missing, malformed, or incomplete."""


def _parse_toml_data(data: dict, source: str) -> dict[str, Any]:
    """Validate raw TOML data and return the manifest dict.

    *source* is used in error messages (file path or "<remote>").
    """
    # Flatten the [package] table if present, else use the top level.
    table = data.get("package", data)

    missing = [k for k in REQUIRED_KEYS if k not in table]
    if missing:
        raise ManifestError(
            f"{source} is missing required key(s): {', '.join(missing)}"
        )

    # parse dependencies into Dependency objects (with version constraints)
    raw_deps = list(table.get("dependencies", []))
    deps: list[Dependency] = []
    for d in raw_deps:
        deps.append(parse_dependency(d))

    return {
        "name": str(table["name"]),
        "version": str(table["version"]),
        "description": str(table.get("description", "")),
        "dependencies": deps,
        "checksums": dict(data.get("checksums", {})),
        "scripts": dict(data.get("scripts", {})),
    }


def parse_manifest_text(text: str) -> dict[str, Any]:
    """Parse a pis.toml from a string (e.g. fetched via raw URL)."""
    try:
        data = tomllib.loads(text)
    except Exception as exc:
        raise ManifestError(f"failed to parse manifest: {exc}") from exc
    return _parse_toml_data(data, "<remote>")


def load_manifest(pkg_dir: Path) -> dict[str, Any]:
    """Read and validate pis.toml from *pkg_dir*.

    Returns a dict with at least: name, version, description, dependencies.
    """
    manifest_path = pkg_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        raise ManifestError(
            f"no {MANIFEST_NAME} found in {pkg_dir}"
        )

    with manifest_path.open("rb") as fh:
        try:
            data = tomllib.load(fh)
        except Exception as exc:  # tomllib raises TOMLDecodeError
            raise ManifestError(f"failed to parse {manifest_path}: {exc}") from exc

    return _parse_toml_data(data, str(manifest_path))
