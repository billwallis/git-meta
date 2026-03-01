from __future__ import annotations

import contextlib
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


def _get_git_repo_status(repository: git.Repo) -> tuple[str, RepoStatus]:
    status = repository.git.status()
    if "nothing to commit, working tree clean" in status:
        return status, RepoStatus.CLEAN_AND_UPDATED
    if repository.is_dirty():
        return status, RepoStatus.DIRTY
    if "Your branch is behind" in status:
        return status, RepoStatus.BEHIND_REMOTE
    if "Untracked files" in status:
        return status, RepoStatus.UNTRACKED_FILES
    if len(repository.branches) > 1:
        return status, RepoStatus.MULTIPLE_BRANCHES

    return status, RepoStatus.UNKNOWN


def _get_status_colour(repository_status: RepoStatus) -> str:
    return {
        RepoStatus.CLEAN_AND_UPDATED: GREEN,
        RepoStatus.DIRTY: RED,
        RepoStatus.UNTRACKED_FILES: YELLOW,
        RepoStatus.BEHIND_REMOTE: YELLOW,
        RepoStatus.MULTIPLE_BRANCHES: YELLOW,
        RepoStatus.UNKNOWN: MAGENTA,
    }[repository_status]


def _fetch_repo(repository: git.Repo) -> None:
    try:
        origin = repository.remote("origin")
    except ValueError:
        return

    with contextlib.suppress(git.exc.GitCommandError):
        origin.fetch()


def pull_repo_main_branches(
    root_directory: pathlib.Path,
    fetch: bool,
) -> None:
    """
    Pull the default branches.
    """

    print(f"Updating git repositories at {root_directory}...")
    repositories = _get_git_repos(directory=root_directory)
    print(f"Found {len(repositories)} git repositories")
    for repo in repositories:
        if fetch:
            _fetch_repo(repo)

        git_status, _ = _get_git_repo_status(repo)
        if "Your branch is behind" in git_status and (
            "On branch main" in git_status or "On branch master" in git_status
        ):
            try:
                print(
                    colour(
                        f"\nUpdating {repo.working_tree_dir}...", BOLD + BLUE
                    )
                )
                print(textwrap.indent(repo.git.pull(), prefix="\t"))
            except TypeError:
                print(
                    textwrap.indent(colour("pull skipped", GREY), prefix="\t")
                )


def git_report(
    root_directory: pathlib.Path,
    fetch: bool,
    print_all: bool,
    quiet_level: int,
) -> None:
    """
    Report on git repositories in the given directory.
    """

    print(f"Reporting on git repositories at {root_directory}...")
    repositories = _get_git_repos(directory=root_directory)
    print(f"Found {len(repositories)} git repositories")
    for repo in repositories:
        if fetch:
            _fetch_repo(repo)

        remote_url = ""
        with contextlib.suppress(ValueError):
            remote_url = repo.remote("origin").url

        git_status, repo_status = _get_git_repo_status(repo)
        repo_header = colour(f"\n{repo.working_tree_dir}", BOLD + BLUE)
        if remote_url:
            repo_header += colour(f"  (origin: {remote_url})", GREY)

        if print_all or repo_status != RepoStatus.CLEAN_AND_UPDATED:
            status_colour = _get_status_colour(repo_status)
            status_message = repo_status if quiet_level > 0 else git_status

            print(repo_header)
            print(
                textwrap.indent(
                    colour(status_message, status_colour),
                    prefix="\t",
                )
            )
