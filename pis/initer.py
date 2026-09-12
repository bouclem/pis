"""Scaffold a new pis package.

`pis init <name>` creates packages/<name>/ with:
  - pis.toml      (manifest with name, version 0.1.0, description)
  - __init__.py   (exposes the package)
  - <name>.py     (starter module with a main() function)

Then runs `pis build <name>` to create the zip + update index.json.
"""

from __future__ import annotations

from pathlib import Path

from pis.builder import BuildError, build
from pis.config import PACKAGES_SUBDIR


class InitError(Exception):
    pass


_INIT_PY = '''\
"""{name} — a pis package."""

from .{name} import main

__all__ = ["main"]
'''

_MODULE_PY = '''\
"""{name} — starter module."""


def main() -> int:
    print("hello from {name}!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

_MANIFEST_TOML = """\
[package]
name = "{name}"
version = "0.1.0"
description = "{description}"
dependencies = []
"""


def init(
    name: str,
    description: str = "",
    repo_root: Path | None = None,
    skip_build: bool = False,
) -> Path:
    """Create a new package scaffold at packages/<name>/.

    *repo_root* defaults to the current working directory.
    *skip_build* skips the automatic `pis build` step.
    Returns the path to the created package folder.
    """
    if repo_root is None:
        repo_root = Path.cwd()

    pkg_dir = repo_root / PACKAGES_SUBDIR / name
    if pkg_dir.exists():
        raise InitError(f"package folder already exists: {pkg_dir}")

    pkg_dir.mkdir(parents=True, exist_ok=True)

    # pis.toml
    (pkg_dir / "pis.toml").write_text(
        _MANIFEST_TOML.format(name=name, description=description),
        encoding="utf-8",
    )

    # __init__.py
    (pkg_dir / "__init__.py").write_text(
        _INIT_PY.format(name=name), encoding="utf-8"
    )

    # starter module
    (pkg_dir / f"{name}.py").write_text(
        _MODULE_PY.format(name=name), encoding="utf-8"
    )

    print(f"  created {pkg_dir}")
    print(f"    - pis.toml")
    print(f"    - __init__.py")
    print(f"    - {name}.py")

    if not skip_build:
        try:
            build(name, repo_root=repo_root)
        except BuildError as exc:
            print(f"  ! build failed: {exc}")
            print(f"  ! run 'pis build {name}' manually after fixing issues")

    return pkg_dir
