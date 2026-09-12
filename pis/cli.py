"""pis command-line interface.

Usage:
    pis install <name> [--force] [--progress]
    pis uninstall <name>
    pis list
    pis search [query]
    pis update [name] [--all] [--force]
    pis info <name>
    pis build <name>
    pis --version
"""

from __future__ import annotations

import argparse
import sys

from pis import __version__
from pis.builder import BuildError, build
from pis.info import InfoError, info
from pis.installer import InstallError, install
from pis.lister import list_installed
from pis.searcher import SearchError, search
from pis.uninstaller import UninstallError, uninstall
from pis.updater import UpdateError, update, update_all


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
        else:  # pragma: no cover - argparse enforces required subcommand
            parser.print_help()
            return 1
        return 0
    except InstallError as exc:
        print(f"pis: install error: {exc}", file=sys.stderr)
        return 1
    except UninstallError as exc:
        print(f"pis: uninstall error: {exc}", file=sys.stderr)
        return 1
    except SearchError as exc:
        print(f"pis: search error: {exc}", file=sys.stderr)
        return 1
    except UpdateError as exc:
        print(f"pis: update error: {exc}", file=sys.stderr)
        return 1
    except InfoError as exc:
        print(f"pis: info error: {exc}", file=sys.stderr)
        return 1
    except BuildError as exc:
        print(f"pis: build error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\npis: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
