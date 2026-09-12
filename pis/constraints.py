"""Parse and check version constraints for pis dependencies.

Supported formats in pis.toml dependencies:
    "foo"           # any version
    "foo>=1.0"      # at least 1.0
    "foo==2.0"      # exactly 2.0
    "foo>1.0"       # greater than 1.0
    "foo<2.0"       # less than 2.0
    "foo<=1.5"      # at most 1.5
    "foo!=1.2"      # not 1.2
    "foo>=1.0,<2.0" # at least 1.0 and less than 2.0

Versions are compared as tuples of integers split on dots.
(e.g. "1.2.3" -> (1, 2, 3))
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Constraint:
    """A single version constraint: operator + version."""
    op: str       # one of: >=, <=, ==, >, <, !=
    version: str


@dataclass
class Dependency:
    """A parsed dependency: name + list of constraints."""
    name: str
    constraints: list[Constraint]


def parse_dependency(dep: str) -> Dependency:
    """Parse a dependency string like 'foo>=1.0,<2.0' into a Dependency."""
    # match name (letters, digits, hyphens, underscores) then optional constraints
    m = re.match(r"^([a-zA-Z0-9_-]+)\s*(.*)$", dep.strip())
    if not m:
        raise ValueError(f"invalid dependency: {dep!r}")
    name = m.group(1)
    rest = m.group(2).strip()

    if not rest:
        return Dependency(name=name, constraints=[])

    constraints: list[Constraint] = []
    for part in rest.split(","):
        part = part.strip()
        if not part:
            continue
        cm = re.match(r"^(>=|<=|==|!=|>|<)\s*(.+)$", part)
        if not cm:
            raise ValueError(f"invalid constraint: {part!r}")
        constraints.append(Constraint(op=cm.group(1), version=cm.group(2).strip()))

    return Dependency(name=name, constraints=constraints)


def _version_tuple(v: str) -> tuple[int, ...]:
    """Convert '1.2.3' -> (1, 2, 3). Non-numeric parts become 0."""
    parts: list[int] = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def check_version(version: str, dep: Dependency) -> bool:
    """Check if *version* satisfies all constraints in *dep*."""
    if not dep.constraints:
        return True

    v = _version_tuple(version)
    for c in dep.constraints:
        cv = _version_tuple(c.version)
        if c.op == ">=":
            if not v >= cv:
                return False
        elif c.op == "<=":
            if not v <= cv:
                return False
        elif c.op == "==":
            if v != cv:
                return False
        elif c.op == "!=":
            if v == cv:
                return False
        elif c.op == ">":
            if not v > cv:
                return False
        elif c.op == "<":
            if not v < cv:
                return False
    return True


def format_dep(dep: Dependency) -> str:
    """Format a Dependency back to string form."""
    if not dep.constraints:
        return dep.name
    parts = [f"{c.op}{c.version}" for c in dep.constraints]
    return f"{dep.name}{','.join(parts)}"
