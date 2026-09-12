# PROJECT — pis

## What it is

`pis` (Python Install Shit) is a minimal pip alternative. Unlike pip, the
package store lives **inside the pis GitHub repo** (`bouclem/pis`) under
`packages/<name>/`. `pis install <name>` downloads a pre-built per-package
zip via `raw.githubusercontent.com` (no GitHub API, no rate limits), extracts
it, and installs it under `~/.pis/packages/`.

## Goals

- Fun first, useful second.
- Zero third-party dependencies (stdlib only).
- Zero GitHub API calls — all fetches via `raw.githubusercontent.com`.
- Simple enough for a junior dev to read end-to-end.
- No custom user-uploaded packages (for now) — only built-in repo packages.

## Architecture

```
pis/
  config.py      constants: repo, raw URLs, paths, dirs
  colors.py      ANSI color helpers (auto-detect, --no-color)
  constraints.py parse + check version constraints (>=, <=, ==, >, <, !=)
  cacher.py      offline cache for downloaded zips
  manifest.py    parse + validate pis.toml (file or text)
  github.py      raw URL fetchers: package zip, manifest, index; checksums
  installer.py   fetch -> cache -> extract -> checksums -> constraints -> deps -> install -> register -> pth -> scripts
  uninstaller.py remove package + registry entry
  lister.py      print installed packages table
  searcher.py    search packages/ via index.json (raw URL)
  updater.py     compare installed vs repo version, reinstall if newer
  info.py        show a package's manifest + changelog from the repo
  builder.py     build per-package zip + update index.json
  initer.py      scaffold a new package folder + pis.toml + build
  cli.py        argparse dispatch (install/uninstall/list/search/update/info/build/init/run/cache)
  __main__.py   `python -m pis` entry
packages/
  index.json      list of available package names
  hello/          sample package (pis.toml + __init__.py + hello.py + CHANGELOG.md + hello.zip)
```

## Install flow

1. `ensure_dirs()` creates `~/.pis/packages/`, `~/.pis/bin/`, `~/.pis/cache/`.
2. `fetch_package_zip(name)` checks cache first, then downloads
   `packages/<name>/<name>.zip` via raw URL and extracts to staging.
3. `load_manifest()` reads + validates `pis.toml`.
4. `verify_checksums()` checks sha256 of listed files if `[checksums]` present.
5. Version constraints on dependencies are checked against installed/fetched versions.
6. Dependencies are installed recursively first (cycle-guarded).
7. Staged folder moves to `~/.pis/packages/<name>/`.
8. Registry (`~/.pis/installed.json`) updated with metadata + scripts.
9. `pis.pth` written to user site-packages (best-effort) for importability.
10. Script wrappers written to `~/.pis/bin/` for declared `[scripts]`.

## Build flow (for package authors)

1. `pis init <name>` — scaffolds `packages/<name>/` with pis.toml, __init__.py,
   starter module, and runs `pis build` automatically.
2. `pis build <name>` — creates `<name>.zip` (includes CHANGELOG.md) and
   updates `packages/index.json`.
3. Commit + push.

## Package changelogs

Each package has its own `CHANGELOG.md` in its folder, independent of the pis
manager's changelog. `pis build` includes it in the zip. `pis info` shows it
if the package is installed locally.

## Direction

- v0.0.1: install / uninstall / list, in-repo packages only.
- v0.0.2: search, update, download progress.
- v0.0.3: no-API fetch (raw URLs), per-package zips, info, checksums, build.
- v0.0.4: init, entry points (scripts), friendly error handling.
- v0.0.5: version constraints, offline cache, colorful output, per-package changelogs.
- Future (see TODO.md): custom repos, doctor, offline mode.
