"""
Entry point into the package.
"""

import pathlib
import textwrap

import git

HERE = pathlib.Path(__file__).parent


def get_git_repos(directory: pathlib.Path) -> list[git.Repo]:
    """
    Get all git repositories in the given directory.
    """
    return [
        git.Repo(path)
        for path in directory.glob("**/.git")
        if path.is_dir()  # skip git submodules
    ]


def print_repo_statuses(repositories: list[git.Repo]) -> None:
    """
    Get all git repositories in the given directory.
    """

    print("\nRepository statuses:")
    for repo in repositories:
        print(f"\n{repo.working_tree_dir}")
        print(textwrap.indent(repo.git.status(), prefix=" " * 4))

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


def print_unexpected_remotes(repositories: list[git.Repo]) -> None:
    """
    Print unexpected remotes in the given repositories.
    """

    for repo in repositories:
        if "\\Repos\\third-parties\\" not in repo.working_tree_dir:
            for remote in repo.remotes:
                if not remote.url.startswith("https://github.com/billwallis/"):
                    print(f"\n{repo.working_tree_dir}")
                    print(f"    {remote.url}")


def main(repositories_directory: pathlib.Path) -> None:
    """
    Entry point into the module.
    """
    print("Getting git repositories...")
    repos = get_git_repos(repositories_directory)
    print(f"Found {len(repos)} git repositories.")
    # print_repo_statuses(repos)
    print_unexpected_remotes(repos)


if __name__ == "__main__":
    main(HERE.parent.parent.parent)
