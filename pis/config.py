"""Central configuration and path constants for pis.

All filesystem state lives under PIS_HOME (~/.pis on every OS):
  ~/.pis/
    packages/         <- installed package folders live here
    bin/              <- script wrappers for entry points
    installed.json    <- registry of installed packages + metadata
    pis.pth           <- (copied to user site-packages) makes packages importable
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Repository --------------------------------------------------------------
# The GitHub repo that holds the in-repo package store.
# Packages live at <repo>/packages/<name>/...
REPO_OWNER = "bouclem"
REPO_NAME = "pis"
REPO_REF = "main"  # branch / tag / sha to fetch from

# Subfolder inside the repo where packages live.
PACKAGES_SUBDIR = "packages"

# --- Raw file URLs (no GitHub API, no rate limits) ---------------------------
# raw.githubusercontent.com serves individual files directly. We use it to
# fetch per-package zips, manifests, and the package index — zero API calls.
RAW_BASE = (
    f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{REPO_REF}"
)

# Per-package pre-built zip: packages/<name>/<name>.zip
def raw_package_zip_url(name: str) -> str:
    return f"{RAW_BASE}/{PACKAGES_SUBDIR}/{name}/{name}.zip"

# Per-package manifest: packages/<name>/pis.toml
def raw_manifest_url(name: str) -> str:
    return f"{RAW_BASE}/{PACKAGES_SUBDIR}/{name}/pis.toml"

# Package index: packages/index.json (lists all available package names)
RAW_INDEX_URL = f"{RAW_BASE}/{PACKAGES_SUBDIR}/index.json"

# --- Local filesystem -------------------------------------------------------
PIS_HOME = Path(os.getenv("PIS_HOME", Path.home() / ".pis"))
PACKAGES_DIR = PIS_HOME / "packages"
BIN_DIR = PIS_HOME / "bin"
REGISTRY_FILE = PIS_HOME / "installed.json"

# Name of the .pth file we drop into the user's site-packages so that
# packages installed under PACKAGES_DIR become importable.
PTH_NAME = "pis.pth"

# User-agent sent with GitHub requests (GitHub asks for one).
USER_AGENT = "pis/0.0.4 (+https://github.com/bouclem/pis)"


def ensure_dirs() -> None:
    """Create PIS_HOME, PACKAGES_DIR, and BIN_DIR if they don't exist yet."""
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    BIN_DIR.mkdir(parents=True, exist_ok=True)


def registry_path() -> Path:
    return REGISTRY_FILE
