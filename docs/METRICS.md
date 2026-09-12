# METRICS — pis

Track project metrics over time. Compare to previous state, flag regressions.

| Date       | Version | Python files | LOC (pis/) | Tests | Deps | Packages in repo |
|------------|---------|--------------|-----------|-------|------|-------------------|
| 2026-09-12 | 0.0.1   | 8            | ~330      | 0     | 0    | 1 (hello)         |
| 2026-09-12 | 0.0.2   | 11           | ~560      | 0     | 0    | 1 (hello)         |
| 2026-09-12 | 0.0.3   | 13           | ~720      | 0     | 0    | 1 (hello)         |
| 2026-09-12 | 0.0.4   | 15           | ~900      | 0     | 0    | 1 (hello)         |
| 2026-09-12 | 0.0.5   | 18           | ~1100     | 0     | 0    | 1 (hello)         |
| 2026-09-12 | 0.0.6   | 19           | ~1300     | 0     | 0    | 1 (hello)         |

## Notes
- LOC measured as source lines in `pis/` (excluding `packages/` and docs).
- Dependencies: 0 third-party (stdlib only).
- v0.0.2 added: searcher.py, updater.py; github.py grew (list_packages, progress).
- v0.0.3 added: info.py, builder.py; github.py rewritten (raw URLs, no API);
  manifest.py refactored (parse_manifest_text); .gitignore added.
- v0.0.3 removed GitHub API dependency entirely — all fetches via raw URLs.
- v0.0.4 added: initer.py; cli.py grew (init, run, error handling);
  installer.py grew (script wrappers); github.py (NotFoundError, NetworkError).
- v0.0.5 added: colors.py, constraints.py, cacher.py; installer.py grew (cache,
  constraints); cli.py grew (cache subcommand, --no-color).
- v0.0.6 added: doctor.py; updater.py grew (self-update, offline); cli.py grew
  (doctor, --offline, update no-args = all + self).
- Tests: none yet — see TODO.md (add pytest suite for v0.0.7).
