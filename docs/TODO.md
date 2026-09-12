# TODO — pis

## v0.0.1 (done)
- [x] install <name> (fetch from repo, extract, deps, register)
- [x] uninstall <name>
- [x] list
- [x] pis.toml manifest parsing
- [x] pis.pth for importability

## v0.0.2 (done)
- [x] `pis search [query]`
- [x] `pis update <name>` / `pis update --all`
- [x] progress indicator during download (`install --progress`)

## v0.0.3 (done)
- [x] `pis info <name>`
- [x] checksum / integrity verification (`[checksums]` table)
- [x] no GitHub API — all fetches via raw.githubusercontent.com
- [x] per-package zip (no whole-repo download)
- [x] `pis build <name>` — build zip + update index.json
- [x] `packages/index.json` for search (no API)

## v0.0.4 (done)
- [x] `pis init <name>` — scaffold a new package folder
- [x] friendly error handling (404, network)
- [x] entry points / `[scripts]` table in pis.toml
- [x] `pis run <pkg> <script>`
- [x] script wrappers in ~/.pis/bin/

## v0.0.5 (done)
- [x] version constraints in dependencies (e.g. "foo>=1.0")
- [x] offline cache (`pis cache list` / `pis cache clear`)
- [x] colorful output (ANSI, `--no-color` flag)
- [x] per-package CHANGELOG.md (independent of pis changelog)

## v0.0.6 (next)
- [ ] custom repo support (multiple sources, not just bouclem/pis)
- [ ] `pis doctor` — diagnose install / pth / path / bin issues
- [ ] offline mode (use cache only, never download)

## Maybe / fun
- [ ] `pis shitlist` — easter egg command
- [ ] `pis doctor` — diagnose install / pth / path issues
