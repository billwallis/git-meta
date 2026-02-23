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

    return sorted(
        [
            git.Repo(path)
            for path in directory.glob("**/.git")
            if path.is_dir()  # skip git submodules
        ],
        key=lambda r: r.working_tree_dir,
    )


def _get_status_colour(repository: git.Repo) -> str:
    status = repository.git.status()
    col = GREEN
    if "Your branch is behind" in status or "Untracked files" in status:
        col = YELLOW
    if repository.is_dirty():
        col = RED

    return col


def print_repo_statuses(repositories: list[git.Repo], print_all: bool) -> None:
    """
    Get all git repositories in the given directory.
    """

    if print_all:
        print("\nRepository statuses:")
        for repo in repositories:
            for remote in repo.remotes:
                if remote.name == "origin":
                    try:
                        remote.fetch()
                    except git.exc.GitCommandError:
                        pass
            print(colour(f"\n{repo.working_tree_dir}", BOLD + BLUE))
            print(
                textwrap.indent(
                    colour(repo.git.status(), _get_status_colour(repo)),
                    prefix=" " * 4,
                )
            )

    print("\nRepositories that need reviewing:")
    for repo in repositories:
        col = _get_status_colour(repo)

        if all(b.name in ["main", "master"] for b in repo.branches):
            if repo.is_dirty():
                print(colour(f"\n{repo.working_tree_dir}", BOLD + BLUE))
                print(colour("    repo is dirty", col))
        else:
            print(colour(f"\n{repo.working_tree_dir}", BOLD + BLUE))
            for branch in repo.branches:
                print(colour(f"    {branch.name}", col))


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
