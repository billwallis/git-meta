from __future__ import annotations

import argparse
import pathlib
import textwrap
from collections.abc import Sequence

import git

SUCCESS = 0
FAILURE = 1
HERE = pathlib.Path(__file__).parent

RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
GREY = "\033[38;5;240m"
BOLD = "\033[1m"
RESET = "\033[0m"


def colour(text: str, colour_: str) -> str:
    """
    Return the text in the given colour.
    """

    return f"{colour_}{text}{RESET}"


def _get_git_repos(directory: pathlib.Path) -> list[git.Repo]:
    """
    Get all git repositories in the given directory.
    """

    return [
        git.Repo(path)
        for path in directory.glob("**/.git")
        if path.is_dir()  # skip git submodules
    ]


def print_repo_statuses(repositories: list[git.Repo], print_all: bool) -> None:
    """
    Get all git repositories in the given directory.
    """

    if print_all:
        print("\nRepository statuses:")
        for repo in repositories:
            for remote in repo.remotes:
                remote.fetch()
            print(colour(f"\n{repo.working_tree_dir}", BOLD + BLUE))

            col = GREEN
            if repo.is_dirty():
                col = RED
            if (
                "Your branch is behind" in repo.git.status()
                or "Untracked files" in repo.git.status()
            ):
                col = YELLOW

            print(
                textwrap.indent(
                    colour(repo.git.status(), col),
                    prefix=" " * 4,
                )
            )

    print("\nRepositories that need reviewing:")
    for repo in repositories:
        if all(b.name in ["main", "master"] for b in repo.branches):
            if repo.is_dirty():
                print(f"\n{repo.working_tree_dir}")
                print(" " * 4, "repo is dirty")
        else:
            print(f"\n{repo.working_tree_dir}")
            for branch in repo.branches:
                print(" " * 4, branch.name)


def git_report(
    root_directory: pathlib.Path,
    print_all: bool,
) -> None:
    """
    Report on git repositories in the given directory.
    """

    print(f"Getting git repositories at {root_directory}...")
    repos = _get_git_repos(root_directory)
    print(f"Found {len(repos)} git repositories.")
    print_repo_statuses(repos, print_all)


def main(argv: Sequence[str] | None = None) -> int:
    """
    Parse the arguments and run the command.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("root-dir")
    parser.add_argument("--print-all", action=argparse.BooleanOptionalAction)
    args = parser.parse_args(argv)

    git_report(
        root_directory=pathlib.Path(getattr(args, "root-dir")),
        print_all=args.print_all,
    )

    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
