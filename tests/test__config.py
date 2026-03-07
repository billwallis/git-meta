import pathlib
from typing import Any

import pytest

from git_meta import config


@pytest.fixture(scope="function")
def standard_config(tmp_path: pathlib.Path) -> config.Config:
    conf = config.Config()
    repo_conf = {
        # repo: default branch
        "repos/foo": "main",
        "repos/bar": "master",
        "repos/baz": "develop",
        "repos/default": None,
    }
    for repo, default_branch in repo_conf.items():
        config.set_repository_config(
            config=conf,
            repository=tmp_path / repo,
            key="default_branch_name",
            value=default_branch,
        )

    return conf


@pytest.mark.parametrize(
    "doc, conf",
    [
        # Empty config
        ({}, config.Config()),
        # Standard config
        (
            {
                "repositories": {
                    "~/repos/foo": {"default_branch_name": "main"},
                    "~/repos/bar": {"default_branch_name": "master"},
                    "~/repos/baz": {"default_branch_name": "develop"},
                    "~/repos/default": {},
                },
            },
            config.Config(
                repositories={
                    "~/repos/foo": config.RepoConfig("main"),
                    "~/repos/bar": config.RepoConfig("master"),
                    "~/repos/baz": config.RepoConfig("develop"),
                    "~/repos/default": config.RepoConfig(),
                },
            ),
        ),
    ],
)
def test__config__from_json__happy_path(
    doc: dict,
    conf: config.Config,
):
    assert config.Config.from_json(doc) == conf


@pytest.mark.parametrize(
    "key, value",
    [("default_branch_name", "feature-branch")],
)
def test__set_repository_config__happy_path(
    standard_config: config.Config,
    tmp_path: pathlib.Path,
    key: str,
    value: Any,
):
    config.set_repository_config(
        config=standard_config,
        repository=tmp_path,
        key=key,
        value=value,
    )

    actual = getattr(standard_config.repositories[str(tmp_path)], key)
    assert actual == value


@pytest.mark.parametrize(
    "repo, key, expected",
    [("repos/foo", "default_branch_name", "main")],
)
def test__unset_repository_config__happy_path(
    standard_config: config.Config,
    tmp_path: pathlib.Path,
    repo: str,
    key: str,
    expected: Any,
):
    repository = tmp_path / repo
    config.unset_repository_config(
        config=standard_config,
        repository=repository,
        key=key,
    )

    actual = getattr(standard_config.repositories[str(repository)], key)
    assert actual == expected
