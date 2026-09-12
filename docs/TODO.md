# TODO — pis

## v0.0.1 (done)
- [x] install <name> (fetch from repo, extract, deps, register)
- [x] uninstall <name>
- [x] list
- [x] pis.toml manifest parsing
- [x] sample package: hello
- [x] pis.pth for importability

## v0.0.2 (done)
- [x] `pis search [query]` — list available packages in the repo
- [x] `pis update <name>` / `pis update --all`
- [x] progress indicator during download (`install --progress`)

## v0.0.3 (done)
- [x] `pis info <name>` — show manifest details from the repo
- [x] checksum / integrity verification (`[checksums]` table in pis.toml)
- [x] no GitHub API — all fetches via raw.githubusercontent.com
- [x] per-package zip (no whole-repo download)
- [x] `pis build <name>` — build zip + update index.json
- [x] `packages/index.json` for search (no API)

## v0.0.4 (next)
- [ ] handle GitHub raw fetch errors (404, network) with friendly messages
- [ ] `pis init <name>` — scaffold a new package folder + pis.toml
- [ ] entry points / console scripts (like [project.scripts])
- [ ] custom repo support (multiple sources, not just bouclem/pis)
- [ ] version constraints in dependencies (e.g. "foo>=1.0")
- [ ] offline cache of downloaded zips

## Maybe / fun
- [ ] `pis shitlist` — easter egg command
- [ ] colorful output (ANSI, with --no-color flag)
- [ ] `pis doctor` — diagnose install / pth / path issues
