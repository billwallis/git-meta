from __future__ import annotations

import enum
import pathlib
import textwrap

import git

RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
GREY = "\033[38;5;240m"
BOLD = "\033[1m"
RESET = "\033[0m"


# TODO: These are not mutually exclusive, so an Enum is not appropriate
class RepoStatus(enum.StrEnum):
    CLEAN_AND_UPDATED = enum.auto()
    UNTRACKED_FILES = enum.auto()
    BEHIND_REMOTE = enum.auto()
    MULTIPLE_BRANCHES = enum.auto()
    DIRTY = enum.auto()
    UNKNOWN = enum.auto()


def colour(text: str, colour_: str) -> str:
    """
    Return the text in the given colour.
    """

    return f"{colour_}{text}{RESET}"


def _get_git_repos(directory: pathlib.Path) -> list[git.Repo]:
    """
    Return a sorted list of all git repositories in the given directory.
    """

    return sorted(
        [
            git.Repo(path)
            for path in directory.glob("**/.git")
            if path.is_dir()  # skip git submodules
        ],
        key=lambda r: r.working_tree_dir,
    )


def _get_repo_status(repository: git.Repo) -> RepoStatus:
    status = repository.git.status()
    if "nothing to commit, working tree clean" in status:
        return RepoStatus.CLEAN_AND_UPDATED
    if repository.is_dirty():
        return RepoStatus.DIRTY
    if "Your branch is behind" in status:
        return RepoStatus.BEHIND_REMOTE
    if "Untracked files" in status:
        return RepoStatus.UNTRACKED_FILES
    if len(repository.branches) > 1:
        return RepoStatus.MULTIPLE_BRANCHES

    return RepoStatus.UNKNOWN


def _get_status_colour(repository_status: RepoStatus) -> str:
    return {
        RepoStatus.CLEAN_AND_UPDATED: GREEN,
        RepoStatus.DIRTY: RED,
        RepoStatus.UNTRACKED_FILES: YELLOW,
        RepoStatus.BEHIND_REMOTE: YELLOW,
        RepoStatus.MULTIPLE_BRANCHES: YELLOW,
        RepoStatus.UNKNOWN: MAGENTA,
    }[repository_status]


def _pull_repo_main_branch(repository: git.Repo) -> None:
    """
    Pull the default branch.
    """

    status = repository.git.status()
    if "Your branch is behind" in status and (
        "On branch main" in status or "On branch master" in status
    ):
        try:
            # print(colour(f"\n{repository.working_tree_dir}", BOLD + BLUE))
            print(repository.git.pull())
        except TypeError:
            print(colour("pull skipped", GREY))


def pull_repo_main_branches(root_directory: pathlib.Path) -> None:
    """
    Pull the default branches.
    """

    for repo in _get_git_repos(root_directory):
        _pull_repo_main_branch(repo)


def _print_repo_statuses(repositories: list[git.Repo], print_all: bool) -> None:
    """
    Print all git repository status in the given directory.
    """

    if print_all:
        print("\nRepository statuses:")
        for repo in repositories:
            remote_url = ""
            for remote in repo.remotes:
                if remote.name == "origin":
                    try:
                        remote.fetch()
                        remote_url = remote.url
                    except git.exc.GitCommandError:
                        pass

            print(colour(f"\n{repo.working_tree_dir}", BOLD + BLUE))
            if remote_url:
                col = RED if remote_url.startswith("http") else GREY
                print(colour(f"    remote URL: {remote_url}", col))
            print(
                textwrap.indent(
                    colour(
                        repo.git.status(),
                        _get_status_colour(_get_repo_status(repo)),
                    ),
                    prefix=" " * 4,
                )
            )

    print("\nRepositories that need reviewing:")
    for repo in repositories:
        col = _get_status_colour(_get_repo_status(repo))

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
    _print_repo_statuses(repos, print_all)
