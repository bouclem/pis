"""pis command-line interface.

Usage:
    pis install <name> [--force] [--progress]
    pis uninstall <name>
    pis list
    pis search [query]
    pis update [name] [--all] [--force]
    pis info <name>
    pis build <name>
    pis init <name> [--description <desc>] [--no-build]
    pis run <pkg> <script>
    pis --version
"""

from __future__ import annotations

import argparse
import json
import sys

from pis import __version__
from pis.builder import BuildError, build
from pis.config import REGISTRY_FILE
from pis.github import FetchError, NetworkError, NotFoundError
from pis.info import InfoError, info
from pis.initer import InitError, init
from pis.installer import InstallError, install
from pis.lister import list_installed
from pis.searcher import SearchError, search
from pis.uninstaller import UninstallError, uninstall
from pis.updater import UpdateError, update, update_all


class RunError(Exception):
    pass


def _run_script(pkg: str, script: str) -> int:
    """Execute a declared script from an installed package.

    Looks up the script in the installed registry, imports the target
    module:function, and calls it.
    """
    if not REGISTRY_FILE.is_file():
        raise RunError("no packages installed")
    try:
        with REGISTRY_FILE.open("r", encoding="utf-8") as fh:
            reg = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        raise RunError(f"could not read registry: {exc}") from exc

    if pkg not in reg:
        raise RunError(f"'{pkg}' is not installed")
    scripts = reg[pkg].get("scripts", {})
    if script not in scripts:
        raise RunError(
            f"'{pkg}' has no script '{script}'. "
            f"available: {', '.join(scripts) or '(none)'}"
        )

    target = scripts[script]
    if ":" not in target:
        raise RunError(f"invalid script target '{target}' (expected module:function)")

    module_name, func_name = target.split(":", 1)
    try:
        mod = __import__(module_name, fromlist=[func_name])
        func = getattr(mod, func_name)
    except ImportError as exc:
        raise RunError(f"could not import '{module_name}': {exc}") from exc
    except AttributeError as exc:
        raise RunError(f"'{module_name}' has no function '{func_name}'") from exc

    result = func()
    return result if isinstance(result, int) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pis",
        description=(
            "pis — Python Install Shit. "
            "A tiny pip alternative with an in-repo package store."
        ),
    )
    parser.add_argument(
        "-V", "--version", action="version",
        version=f"pis {__version__}",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # install
    p_install = sub.add_parser(
        "install", help="install a package from the pis repo"
    )
    p_install.add_argument("name", help="package name")
    p_install.add_argument(
        "-f", "--force", action="store_true",
        help="reinstall even if the same version is already installed",
    )
    p_install.add_argument(
        "-p", "--progress", action="store_true",
        help="show a download progress bar",
    )

    # uninstall
    p_uninstall = sub.add_parser(
        "uninstall", help="remove an installed package"
    )
    p_uninstall.add_argument("name", help="package name")

    # list
    sub.add_parser("list", help="list installed packages")

    # search
    p_search = sub.add_parser(
        "search", help="search available packages in the repo"
    )
    p_search.add_argument(
        "query", nargs="?", default="",
        help="search string (substring match); empty lists all",
    )

    # update
    p_update = sub.add_parser(
        "update", help="update a package (or all) to the latest repo version"
    )
    p_update.add_argument(
        "name", nargs="?", help="package name (omit with --all for everything)"
    )
    p_update.add_argument(
        "-a", "--all", action="store_true",
        help="update all installed packages",
    )
    p_update.add_argument(
        "-f", "--force", action="store_true",
        help="reinstall even if the version is unchanged",
    )

    # info
    p_info = sub.add_parser(
        "info", help="show a package's manifest details from the repo"
    )
    p_info.add_argument("name", help="package name")

    # build
    p_build = sub.add_parser(
        "build", help="build a package zip + update index.json (run in repo root)"
    )
    p_build.add_argument("name", help="package name")

    # init
    p_init = sub.add_parser(
        "init", help="scaffold a new package folder + pis.toml"
    )
    p_init.add_argument("name", help="package name")
    p_init.add_argument(
        "-d", "--description", default="",
        help="package description",
    )
    p_init.add_argument(
        "--no-build", action="store_true",
        help="skip the automatic build step",
    )

    # run
    p_run = sub.add_parser(
        "run", help="run a script declared in an installed package"
    )
    p_run.add_argument("pkg", help="package name")
    p_run.add_argument("script", help="script name (from [scripts] in pis.toml)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "install":
            install(args.name, force=args.force, progress=args.progress)
        elif args.command == "uninstall":
            uninstall(args.name)
        elif args.command == "list":
            list_installed()
        elif args.command == "search":
            search(args.query)
        elif args.command == "update":
            if args.all:
                update_all()
            elif args.name:
                update(args.name, force=args.force)
            else:
                parser.error("update requires a package name or --all")
        elif args.command == "info":
            info(args.name)
        elif args.command == "build":
            build(args.name)
        elif args.command == "init":
            init(args.name, description=args.description, skip_build=args.no_build)
        elif args.command == "run":
            return _run_script(args.pkg, args.script)
        else:  # pragma: no cover - argparse enforces required subcommand
            parser.print_help()
            return 1
        return 0
    except InstallError as exc:
        _print_error("install", exc)
        return 1
    except UninstallError as exc:
        _print_error("uninstall", exc)
        return 1
    except SearchError as exc:
        _print_error("search", exc)
        return 1
    except UpdateError as exc:
        _print_error("update", exc)
        return 1
    except InfoError as exc:
        _print_error("info", exc)
        return 1
    except BuildError as exc:
        _print_error("build", exc)
        return 1
    except InitError as exc:
        _print_error("init", exc)
        return 1
    except RunError as exc:
        _print_error("run", exc)
        return 1
    except KeyboardInterrupt:
        print("\npis: interrupted", file=sys.stderr)
        return 130


def _print_error(cmd: str, exc: Exception) -> None:
    """Print a friendly error message, translating known fetch errors."""
    msg = str(exc)
    # translate fetch sub-errors
    if isinstance(exc, (InstallError, SearchError, UpdateError, InfoError)):
        if isinstance(exc.__cause__, NotFoundError):
            pkg = _extract_pkg_name(exc)
            if pkg:
                msg = f"package '{pkg}' not found in the repo"
            else:
                msg = "requested resource not found in the repo"
        elif isinstance(exc.__cause__, NetworkError):
            msg = f"could not reach the repo (check your connection): {exc.__cause__}"
    print(f"pis: {cmd} error: {msg}", file=sys.stderr)


def _extract_pkg_name(exc: Exception) -> str:
    """Try to extract a package name from an error message."""
    msg = str(exc)
    # common patterns: "package 'foo' not found", "not found: .../packages/foo/foo.zip"
    import re
    m = re.search(r"packages/([^/]+)/", msg)
    if m:
        return m.group(1)
    m = re.search(r"'([^']+)'", msg)
    if m:
        return m.group(1)
    return ""


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
