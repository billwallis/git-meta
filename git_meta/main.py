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
    return [git.Repo(path) for path in directory.glob("**/.git")]


def main(repositories_directory: pathlib.Path) -> None:
    """
    Entry point into the module.
    """
    print("Getting git repositories...")
    repos = get_git_repos(repositories_directory)
    print(f"Found {len(repos)} git repositories.")

    print("\nRepository statuses:")
    for repo in repos:
        print(f"\n{repo.working_tree_dir}")
        print(textwrap.indent(repo.git.status(), prefix=" " * 4))

    print("\nRepositories that need reviewing:")
    for repo in repos:
        if all(b.name in ["main", "master"] for b in repo.branches):
            if repo.is_dirty():
                print(f"\n{repo.working_tree_dir}")
                print(" " * 4, "repo is dirty")
        else:
            print(f"\n{repo.working_tree_dir}")
            for branch in repo.branches:
                print(" " * 4, branch.name)


if __name__ == "__main__":
    main(HERE.parent.parent.parent)
