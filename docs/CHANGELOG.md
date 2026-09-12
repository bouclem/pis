# CHANGELOG — pis

All notable changes to pis. Dates in YYYY-MM-DD.

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
