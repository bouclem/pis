# LESSONS — pis

Cumulative mistakes, patterns, and insights. Read before starting work.
Add an entry whenever you learn something new.

## 2026-09-12 — initial build
- GitHub archive zipball's top folder is named `<owner>-<repo>-<sha>`, not a
  fixed name. Always locate `packages/<name>/` by path segment, not by prefix.
- `tomllib` is stdlib only on Python 3.11+. Provide a `tomli` fallback so older
  Pythons aren't silently broken — but declare `requires-python = ">=3.11"` in
  pyproject so the happy path is clear.
- Writing a `.pth` into user site-packages is the simplest dependency-free
  way to make a custom package dir importable. `site.getusersitepackages()`
  gives the path; mkdir + write are best-effort (may fail on permissions).

## 2026-09-12 — v0.0.2 (search, update, progress)
- The GitHub contents API (`/repos/{owner}/{repo}/contents/{path}`) returns a
  JSON array of entries for a folder; filter `type == "dir"` for subfolders.
  Unauthenticated rate limit is 60/hr — fine for a fun tool, but worth noting.
- For download progress without third-party libs: read in chunks (8192 bytes),
  use `Content-Length` header for total, write a `\r`-prefixed bar to stderr.
  When total is unknown (chunked transfer), just show running byte count.
- `update` needs the repo version without a full install — extract to a
  separate `.staging-update` dir, read the manifest, then clean up. Reusing
  the same `.staging` dir as `install` would race if update calls install.

## 2026-09-12 — v0.0.3 (no API, per-package zip, info, checksums, build)
- `raw.githubusercontent.com` serves individual files with no rate limit and
  no auth. It's the right choice for a dependency-free tool that needs to
  avoid the GitHub API's 60/hr unauthenticated limit.
- Per-package pre-built zips avoid downloading the whole repo. The trade-off:
  a build step (`pis build`) is needed before pushing. Worth it — keeps
  install fast and simple.
- `__pycache__` dirs creep into zips if you `rglob` without filtering. Always
  exclude `__pycache__` (and `.pyc` files) when building package archives.
- `tomllib.loads(str)` parses TOML from a string (vs `tomllib.load(file)`).
  Useful for remote manifests fetched as text — no temp file needed.
- `index.json` is simpler than an API call for listing available packages.
  The build command maintains it automatically so it can't drift.
