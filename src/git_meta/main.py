from __future__ import annotations

import asyncio
import enum
import pathlib
import textwrap

from git_meta import config, git

RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
GREY = "\033[38;5;240m"
BOLD = "\033[1m"
RESET = "\033[0m"


type GitWorkingDir = pathlib.Path


class GitError(Exception):
    pass


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


def _print_multiline(text: str, prefix: str = "") -> None:
    print(textwrap.indent(text, prefix=prefix), flush=True)


def _is_subdirectory(
    repo_dir: GitWorkingDir,
    repo_dirs: list[GitWorkingDir],
) -> bool:
    """
    Return ``True`` if the repository directory is a subdirectory of another
    repository directory, else ``False``.
    """

    return any(
        repo_dir.is_relative_to(other)
        for other in repo_dirs
        if repo_dir != other
    )


def _get_git_repos(directory: pathlib.Path) -> list[GitWorkingDir]:
    """
    Return a sorted list of all git repositories in the given directory.
    """

    repos = [
        path.parent.resolve()
        for path in directory.glob("**/.git")
        if path.is_dir()  # skip git submodules
    ]

    return [
        repo_path
        for repo_path in sorted(repos)
        if not _is_subdirectory(repo_path, repos)
    ]


def _get_git_repo_branches(repo_dir: GitWorkingDir) -> list[str]:
    rc, out, err = git.run_git_cmd(
        args=("branch", "--list"),
        git_dir=repo_dir,
    )

    if rc != 0:
        print(err)
        return []

    return [b[2:] for b in out.split("\n")]


def _get_git_repo_status(repo_dir: GitWorkingDir) -> tuple[str, RepoStatus]:  # noqa: PLR0911
    rc, out, err = git.run_git_cmd(
        args=("status",),
        git_dir=repo_dir,
    )

    status = out
    if rc != 0:
        return err, RepoStatus.UNKNOWN
    if "Changes not staged for commit" in status:
        return status, RepoStatus.DIRTY
    if "Your branch is behind" in status:
        return status, RepoStatus.BEHIND_REMOTE
    if "Untracked files" in status:
        return status, RepoStatus.UNTRACKED_FILES
    if len(_get_git_repo_branches(repo_dir)) > 1:
        return status, RepoStatus.MULTIPLE_BRANCHES
    if "nothing to commit, working tree clean" in status:
        return status, RepoStatus.CLEAN_AND_UPDATED

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


def _get_remote_url(
    repo_dir: GitWorkingDir,
    origin_name: str = "origin",
) -> str:
    rc, out, err = git.run_git_cmd(
        args=("remote", "get-url", origin_name),
        git_dir=repo_dir,
    )

    if rc != 0:
        print(err)
        return ""

    return out


def _fetch_repo(
    repo_dir: GitWorkingDir,
    origin_name: str = "origin",
) -> str:
    rc, out, err = git.run_git_cmd(
        args=(
            "fetch",
            origin_name,
            "--no-recurse-submodules",
            "--progress",
            "--prune",
        ),
        git_dir=repo_dir,
    )

    return out if rc == 0 else err


def _pull_repo(repo_dir: GitWorkingDir) -> str:
    rc, out, err = git.run_git_cmd(
        args=("pull", "--no-recurse-submodules"),
        git_dir=repo_dir,
    )

    if rc != 0:
        raise GitError(err)

    return out


def _pull_repo_main_branch(
    repo_dir: GitWorkingDir,
    conf: config.Config,
    fetch: bool,
) -> None:
    if fetch:
        if progress := _fetch_repo(repo_dir):
            _print_multiline(progress)

    git_status, _ = _get_git_repo_status(repo_dir)
    if repo_config := conf.repositories.get(str(repo_dir)):
        default_branch = repo_config.default_branch_name
    else:
        default_branch = "main"

    if (
        "Your branch is behind" in git_status
        and f"On branch {default_branch}" in git_status
    ):
        try:
            print(
                colour(f"\nUpdating {repo_dir}...", BOLD + BLUE),
                flush=True,
            )
            _print_multiline(_pull_repo(repo_dir), prefix="\t")
        except GitError as e:
            _print_multiline(colour(str(e), RED), prefix="\t")


async def pull_repo_main_branches(
    root_directory: pathlib.Path,
    fetch: bool,
) -> None:
    """
    Pull the default branches.
    """

    print(
        f"Updating git repositories at '{root_directory.resolve()}'", flush=True
    )
    repositories = _get_git_repos(directory=root_directory)
    conf = config.load_config()
    print(f"Found {len(repositories)} git repositories", flush=True)

    await asyncio.gather(
        *[
            asyncio.to_thread(
                _pull_repo_main_branch,
                repo_dir=repo,
                conf=conf,
                fetch=fetch,
            )
            for repo in repositories
        ],
        return_exceptions=True,
    )


def _report_on_repo(
    repo_dir: GitWorkingDir,
    fetch: bool,
    print_all: bool,
    quiet_level: int,
) -> None:
    if fetch:
        if progress := _fetch_repo(repo_dir):
            _print_multiline(progress)

    remote_url = _get_remote_url(repo_dir, "origin")
    git_status, repo_status = _get_git_repo_status(repo_dir)
    repo_header = colour(f"\n{repo_dir}", BOLD + BLUE)
    if remote_url:
        repo_header += colour(f"  (origin: {remote_url})", GREY)

    if print_all or repo_status != RepoStatus.CLEAN_AND_UPDATED:
        status_colour = _get_status_colour(repo_status)
        status_message = repo_status if quiet_level > 0 else git_status

        print(repo_header, flush=True)
        _print_multiline(colour(status_message, status_colour), prefix="\t")


async def git_report(
    root_directory: pathlib.Path,
    fetch: bool,
    print_all: bool,
    quiet_level: int,
) -> None:
    """
    Report on git repositories in the given directory.
    """

    print(
        f"Reporting on git repositories at '{root_directory.resolve()}'",
        flush=True,
    )
    repositories = _get_git_repos(directory=root_directory)
    print(f"Found {len(repositories)} git repositories", flush=True)

    futures = [
        asyncio.to_thread(
            _report_on_repo,
            repo_dir=repo,
            fetch=fetch,
            print_all=print_all,
            quiet_level=quiet_level,
        )
        for repo in repositories
    ]
    await asyncio.gather(*futures, return_exceptions=True)
