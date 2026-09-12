"""pis command-line interface.

Usage:
    pis install <name> [--force] [--progress] [--no-cache] [--offline]
    pis uninstall <name>
    pis list
    pis search [query]
    pis update [name] [--all] [--force] [--offline]
    pis info <name>
    pis build <name>
    pis init <name> [--description <desc>] [--no-build]
    pis run <pkg> <script>
    pis cache list|clear [name]
    pis doctor
    pis --version [--no-color]
"""

from __future__ import annotations

import argparse
import json
import sys

from pis import __version__, colors
from pis.builder import BuildError, build
from pis.cacher import clear_cache, list_cache
from pis.config import REGISTRY_FILE
from pis.doctor import DoctorError, doctor
from pis.github import FetchError, NetworkError, NotFoundError
from pis.info import InfoError, info
from pis.initer import InitError, init
from pis.installer import InstallError, install
from pis.lister import list_installed
from pis.searcher import SearchError, search
from pis.uninstaller import UninstallError, uninstall
from pis.updater import UpdateError, update, update_all, update_default


class RunError(Exception):
    pass


def _run_script(pkg: str, script: str) -> int:
    """Execute a declared script from an installed package."""
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
    parser.add_argument(
        "--no-color", action="store_true",
        help="disable colored output",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # install
    p_install = sub.add_parser("install", help="install a package from the pis repo")
    p_install.add_argument("name", help="package name")
    p_install.add_argument("-f", "--force", action="store_true",
        help="reinstall even if the same version is already installed")
    p_install.add_argument("-p", "--progress", action="store_true",
        help="show a download progress bar")
    p_install.add_argument("--no-cache", action="store_true",
        help="skip cache and always download")
    p_install.add_argument("--offline", action="store_true",
        help="use cache only, never download")

    # uninstall
    p_uninstall = sub.add_parser("uninstall", help="remove an installed package")
    p_uninstall.add_argument("name", help="package name")

    # list
    sub.add_parser("list", help="list installed packages")

    # search
    p_search = sub.add_parser("search", help="search available packages in the repo")
    p_search.add_argument("query", nargs="?", default="",
        help="search string (substring match); empty lists all")

    # update
    p_update = sub.add_parser("update",
        help="update a package, all packages, or pis itself")
    p_update.add_argument("name", nargs="?",
        help="package name (omit to update all + pis itself)")
    p_update.add_argument("-a", "--all", action="store_true",
        help="update all installed packages only")
    p_update.add_argument("-f", "--force", action="store_true",
        help="reinstall even if the version is unchanged")
    p_update.add_argument("--offline", action="store_true",
        help="use cache only, never download")

    # info
    p_info = sub.add_parser("info",
        help="show a package's manifest details from the repo")
    p_info.add_argument("name", help="package name")

    # build
    p_build = sub.add_parser("build",
        help="build a package zip + update index.json (run in repo root)")
    p_build.add_argument("name", help="package name")

    # init
    p_init = sub.add_parser("init", help="scaffold a new package folder + pis.toml")
    p_init.add_argument("name", help="package name")
    p_init.add_argument("-d", "--description", default="", help="package description")
    p_init.add_argument("--no-build", action="store_true",
        help="skip the automatic build step")

    # run
    p_run = sub.add_parser("run", help="run a script declared in an installed package")
    p_run.add_argument("pkg", help="package name")
    p_run.add_argument("script", help="script name (from [scripts] in pis.toml)")

    # cache
    p_cache = sub.add_parser("cache", help="manage the zip cache")
    p_cache_sub = p_cache.add_subparsers(dest="cache_cmd", required=True)
    p_cache_sub.add_parser("list", help="list cached zips")
    p_cache_clear = p_cache_sub.add_parser("clear", help="clear cache")
    p_cache_clear.add_argument("name", nargs="?", help="only clear cache for this package")

    # doctor
    sub.add_parser("doctor", help="diagnose install / pth / path / bin issues")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # init colors
    colors.init(no_color=getattr(args, "no_color", False))

    try:
        if args.command == "install":
            install(args.name, force=args.force, progress=args.progress,
                    use_cache=not args.no_cache, offline=args.offline)
        elif args.command == "uninstall":
            uninstall(args.name)
        elif args.command == "list":
            list_installed()
        elif args.command == "search":
            search(args.query)
        elif args.command == "update":
            if args.all:
                update_all(offline=args.offline)
            elif args.name:
                update(args.name, force=args.force, offline=args.offline)
            else:
                # no args: update all packages + pis itself
                update_default(offline=args.offline)
        elif args.command == "info":
            info(args.name)
        elif args.command == "build":
            build(args.name)
        elif args.command == "init":
            init(args.name, description=args.description, skip_build=args.no_build)
        elif args.command == "run":
            return _run_script(args.pkg, args.script)
        elif args.command == "cache":
            if args.cache_cmd == "list":
                _cache_list()
            elif args.cache_cmd == "clear":
                _cache_clear(getattr(args, "name", None))
        elif args.command == "doctor":
            return doctor()
        else:
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
    except DoctorError as exc:
        _print_error("doctor", exc)
        return 1
    except KeyboardInterrupt:
        print("\npis: interrupted", file=sys.stderr)
        return 130


def _cache_list() -> None:
    """List cached zips."""
    entries = list_cache()
    if not entries:
        print(colors.dim("  cache is empty"))
        return
    print(colors.header(f"  {'Name':<20} {'Version':<12} {'Size'}"))
    print("  " + "-" * 50)
    for name, version, size in entries:
        size_str = f"{size} bytes" if size < 1024 else f"{size // 1024} KB"
        print(f"  {name:<20} {version:<12} {size_str}")
    print(f"\n  {len(entries)} cached zip(s)")


def _cache_clear(name: str | None) -> None:
    """Clear cache."""
    removed = clear_cache(name)
    if removed:
        print(colors.success(f"  cleared {removed} cached zip(s)"))
    else:
        print(colors.dim("  cache is empty"))


def _print_error(cmd: str, exc: Exception) -> None:
    """Print a friendly error message, translating known fetch errors."""
    msg = str(exc)
    if isinstance(exc, (InstallError, SearchError, UpdateError, InfoError)):
        if isinstance(exc.__cause__, NotFoundError):
            pkg = _extract_pkg_name(exc)
            if pkg:
                msg = f"package '{pkg}' not found in the repo"
            else:
                msg = "requested resource not found in the repo"
        elif isinstance(exc.__cause__, NetworkError):
            msg = f"could not reach the repo (check your connection): {exc.__cause__}"
    print(colors.error(f"pis: {cmd} error: {msg}"), file=sys.stderr)


def _extract_pkg_name(exc: Exception) -> str:
    """Try to extract a package name from an error message."""
    import re
    msg = str(exc)
    m = re.search(r"packages/([^/]+)/", msg)
    if m:
        return m.group(1)
    m = re.search(r"'([^']+)'", msg)
    if m:
        return m.group(1)
    return ""


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
