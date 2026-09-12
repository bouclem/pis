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
  manifest.py    parse + validate pis.toml (file or text)
  github.py      raw URL fetchers: package zip, manifest, index; checksums
  installer.py   fetch -> extract -> checksums -> deps -> install -> register -> pth
  uninstaller.py remove package + registry entry
  lister.py      print installed packages table
  searcher.py    search packages/ via index.json (raw URL)
  updater.py     compare installed vs repo version, reinstall if newer
  info.py        show a package's manifest from the repo
  builder.py     build per-package zip + update index.json
  cli.py        argparse dispatch (install/uninstall/list/search/update/info/build)
  __main__.py   `python -m pis` entry
packages/
  index.json      list of available package names
  hello/          sample package (pis.toml + hello.py + hello.zip)
```

## Install flow

1. `ensure_dirs()` creates `~/.pis/packages/`.
2. `fetch_package_zip(name)` downloads `packages/<name>/<name>.zip` via raw URL
   and extracts it to a staging dir.
3. `load_manifest()` reads + validates `pis.toml`.
4. `verify_checksums()` checks sha256 of listed files if `[checksums]` present.
5. Dependencies are installed recursively first (cycle-guarded).
6. Staged folder moves to `~/.pis/packages/<name>/`.
7. Registry (`~/.pis/installed.json`) updated with metadata.
8. `pis.pth` written to user site-packages (best-effort) for importability.

## Build flow (for package authors)

1. Create `packages/<name>/` with `pis.toml` + source files.
2. Run `pis build <name>` (in repo root) — creates `<name>.zip` and updates
   `packages/index.json`.
3. Commit + push.

## Direction

- v0.0.1: install / uninstall / list, in-repo packages only.
- v0.0.2: search, update, download progress.
- v0.0.3: no-API fetch (raw URLs), per-package zips, info, checksums, build.
- Future (see TODO.md): init, entry points, custom repos, version constraints.
