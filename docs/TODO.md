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

## v0.0.4 (done)
- [x] `pis init <name>` — scaffold a new package folder + pis.toml
- [x] friendly error handling (404, network) instead of raw tracebacks
- [x] entry points / `[scripts]` table in pis.toml
- [x] `pis run <pkg> <script>` — execute declared scripts
- [x] script wrappers in ~/.pis/bin/ after install

## v0.0.5 (next)
- [ ] custom repo support (multiple sources, not just bouclem/pis)
- [ ] version constraints in dependencies (e.g. "foo>=1.0")
- [ ] offline cache of downloaded zips
- [ ] `pis doctor` — diagnose install / pth / path issues

## Maybe / fun
- [ ] `pis shitlist` — easter egg command
- [ ] colorful output (ANSI, with --no-color flag)
