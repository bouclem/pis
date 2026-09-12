# pis — Python Install Shit

`pis` is a tiny `pip` alternative. Packages live **inside the pis repo itself**
under `packages/<name>/`, and `pis install <name>` fetches them from there.

> Mostly for fun. Some parts are genuinely useful. No custom user-uploaded
> packages yet — only the built-in "pis thing" packages that ship in the repo.

## Install pis itself

```bash
pip install -e .
```

Or just run it without installing:

```bash
python -m pis --help
```

## Commands

```bash
pis install <name>        # fetch & install a package from the repo
pis install <name> -f     # force reinstall even if version matches
pis install <name> -p     # show a download progress bar
pis install <name> --no-cache  # skip cache, always download
pis install <name> --offline   # use cache only, never download
pis uninstall <name>      # remove an installed package
pis list                  # list installed packages
pis search [query]        # list available packages in the repo (substring filter)
pis update                # update all packages + pis itself
pis update <name>         # update a single package
pis update --all          # update all installed packages only
pis update --offline      # update using cache only
pis info <name>           # show a package's manifest details from the repo
pis build <name>          # build a package zip + update index.json (run in repo root)
pis init <name>           # scaffold a new package folder + pis.toml + build
pis run <pkg> <script>    # run a script declared in an installed package
pis cache list            # list cached zips
pis cache clear [name]    # clear cache (optionally for one package)
pis doctor                # diagnose install / pth / path / bin issues
pis --version
pis --no-color            # disable colored output
```

## How install works (no GitHub API)

pis fetches packages via `raw.githubusercontent.com` — **zero GitHub API calls,
no rate limits**. Each package folder contains a pre-built `<name>.zip`:

1. `pis install <name>` downloads `packages/<name>/<name>.zip` via raw URL
2. Extracts it, reads `pis.toml`, verifies checksums (if declared)
3. Installs dependencies recursively, then the package itself
4. Registers in `~/.pis/installed.json` and writes `pis.pth` for importability

`pis search` reads `packages/index.json` via raw URL (also no API).

`pis build <name>` (run in the repo root) creates the zip and updates
`index.json` — run it before committing a new or updated package.

## Where things live

```
~/.pis/
  packages/        <- installed package folders
  bin/             <- script wrappers for entry points
  cache/           <- cached downloaded zips
  installed.json   <- registry of installed packages + metadata
```

A `pis.pth` file is also dropped into the user's site-packages so installed
packages become importable from any Python session. If that fails (permissions),
add `~/.pis/packages` to your `PYTHONPATH` manually.

Script wrappers are written to `~/.pis/bin/` — add it to your PATH to run
declared scripts directly.

## Package format

Each package is a folder under `packages/<name>/` containing a `pis.toml`:

```toml
[package]
name = "hello"
version = "0.1.0"
description = "a tiny sample pis package"
dependencies = ["foo>=1.0,<2.0"]  # optional version constraints

# Optional: verify file integrity after install
[checksums]
"hello.py" = "sha256hex..."

# Optional: declare runnable scripts (entry points)
[scripts]
greet = "hello:main"
```

Plus whatever Python files make up the package, a `CHANGELOG.md` for the
package's own history, and a pre-built `<name>.zip` (created by
`pis build <name>`). Use `pis init <name>` to scaffold a new package with
all the boilerplate.

## Requirements

- Python 3.11+ (uses `tomllib`; falls back to `tomli` if installed)
- No third-party dependencies — stdlib only

## License

MIT
