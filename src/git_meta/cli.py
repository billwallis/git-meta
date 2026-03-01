from __future__ import annotations

import argparse
import pathlib
import tomllib
from collections.abc import Sequence

import git_meta

SUCCESS = 0
FAILURE = 1
HERE = pathlib.Path(__file__).parent
PYPROJECT = HERE.parent.parent / "pyproject.toml"

RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
GREY = "\033[38;5;240m"
BOLD = "\033[1m"
RESET = "\033[0m"


def colour(text: str, colour_: str) -> str:
    """
    Return the text in the given colour.
    """

    return f"{colour_}{text}{RESET}"


def _get_version() -> str:
    pyproject = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return pyproject["project"]["version"]


def _update(args: argparse.Namespace) -> int:
    git_meta.pull_repo_main_branches(pathlib.Path(getattr(args, "root-dir")))
    return SUCCESS


def _report(args: argparse.Namespace) -> int:
    git_meta.git_report(
        root_directory=pathlib.Path(getattr(args, "root-dir")),
        fetch=args.fetch,
        print_all=args.print_all,
        quiet_level=args.quiet,
    )
    return SUCCESS


def main(argv: Sequence[str] | None = None) -> int:
    """
    Parse the arguments and run the command.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=_get_version(),
    )
    subparsers = parser.add_subparsers(dest="command")

    parser__update = subparsers.add_parser("update")
    parser__update.add_argument("root-dir")

    parser__report = subparsers.add_parser("report")
    parser__report.add_argument("root-dir")
    parser__report.add_argument(
        "--fetch",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser__report.add_argument(
        "--print-all",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser__report.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
    )

    args = parser.parse_args(argv)
    # print(args)  # for debugging
    if args.command == "update":
        return _update(args)
    if args.command == "report":
        return _report(args)

    parser.print_help()
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
