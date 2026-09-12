# CHANGELOG — pis

All notable changes to the pis package manager. Dates in YYYY-MM-DD.
Package-specific changes are tracked in each package's own CHANGELOG.md.

## 0.0.6 — 2026-09-12
- `pis doctor` — diagnose install / pth / path / bin issues. Checks: dirs
  exist, registry is valid, pis.pth points to right path, ~/.pis/bin on PATH,
  installed packages exist on disk. Reports OK/WARN/FAIL with suggestions.
- `pis install --offline` / `pis update --offline` — use cache only, never
  download. Errors with a clear message if not cached.
- `pis update` (no args) now updates all installed packages AND pis itself.
  Checks the repo's pyproject.toml for a newer pis version and self-updates
  via `pip install --upgrade git+...`. Use `pis update --all` for packages only.
- New file: `pis/doctor.py`.

## 0.0.5 — 2026-09-12
- Version constraints in dependencies: `dependencies = ["foo>=1.0,<2.0"]`.
  Supports `>=`, `<=`, `==`, `>`, `<`, `!=`, comma-separated. pis checks
  installed and fetched versions against constraints, aborts on mismatch.
- Offline cache: downloaded zips cached in `~/.pis/cache/<name>-<version>.zip`.
  `pis install` uses cache automatically; `--no-cache` forces re-download.
  New `pis cache list` / `pis cache clear [name]` commands.
- Colorful output: ANSI colors for success/error/info/warning messages.
  Auto-detects terminal support; `--no-color` flag or `NO_COLOR` env var
  disables. New `pis/colors.py` module.
- Per-package CHANGELOG.md: each package can have its own `CHANGELOG.md`,
  included in the zip by `pis build`. `pis info` shows it if installed locally.
- Dependencies in manifest now parsed as `Dependency` objects with constraints.
  Registry stores them as formatted strings (e.g. `"foo>=1.0"`).
- New files: `pis/colors.py`, `pis/constraints.py`, `pis/cacher.py`.

## 0.0.4 — 2026-09-12
- `pis init <name> [--description] [--no-build]` — scaffold a new package
  folder with `pis.toml`, `__init__.py`, and a starter module. Runs `pis build`
  automatically unless `--no-build` is passed.
- `pis run <pkg> <script>` — execute a script declared in an installed
  package's `[scripts]` table. Imports the target `module:function` and calls it.
- Entry points / `[scripts]` table in `pis.toml`: `greet = "hello:main"`.
  After install, pis writes wrapper scripts (`.py`, `.bat`, `.sh`) into
  `~/.pis/bin/` so declared scripts are runnable directly if `~/.pis/bin` is
  on PATH.
- Friendly error handling: 404 → "package '<name>' not found in the repo",
  network errors → "could not reach the repo (check your connection)".
  No more raw tracebacks for common failures.
- `pis info <name>` now shows declared scripts.
- Added `~/.pis/bin/` directory for script wrappers.
- New files: `pis/initer.py`.

## 0.0.3 — 2026-09-12
- **No GitHub API**: switched from the API zipball endpoint to
  `raw.githubusercontent.com` for all fetches. Zero API calls, no rate limits.
- Per-package zip: each package ships a pre-built `<name>.zip` in its folder.
  `pis install` downloads only that zip (not the whole repo).
- `pis build <name>` — builds a package zip from its source folder and updates
  `packages/index.json` automatically. Excludes `__pycache__`, `.gitkeep`,
  `index.json`, and the zip itself.
- `pis info <name>` — fetch and display a package's manifest (name, version,
  description, dependencies, checksums) from the repo without installing.
- `pis search` now reads `packages/index.json` via raw URL (no API).
- Checksum verification: `pis.toml` may include an optional `[checksums]`
  table (filename → sha256 hex). After extraction, pis verifies each listed
  file and aborts install on mismatch.
- `pis update` now fetches only the manifest (via raw URL) to check version,
  instead of downloading the whole zipball.
- Added `.gitignore`.
- Refactored manifest.py: shared `_parse_toml_data()` + new
  `parse_manifest_text()` for remote manifest parsing.

## 0.0.2 — 2026-09-12
- `pis search [query]` — list available packages in the repo (now via
  index.json, was GitHub contents API in original 0.0.2).
- `pis update [name] [--all] [--force]` — compare installed version against
  the repo's current version and reinstall if newer. `--all` updates every
  installed package; `--force` reinstalls even if the version is unchanged.
- Download progress bar (`pis install --progress` / `-p`).

## 0.0.1 — 2026-09-12
- Initial release.
- `pis install <name> [--force]` — fetch from bouclem/pis repo, extract
  `packages/<name>/`, install dependencies recursively, register in
  `~/.pis/installed.json`, write `pis.pth` to user site-packages.
- `pis uninstall <name>` — remove package + registry entry.
- `pis list` — table of installed packages.
- `pis.toml` manifest format (`[package]` table: name, version, description,
  dependencies).
- Sample package `hello`.
- Stdlib only (no third-party deps). Requires Python 3.11+.
