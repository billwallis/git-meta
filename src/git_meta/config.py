from __future__ import annotations

import dataclasses
import functools
import json
import pathlib
from typing import Any

from git_meta.constants import CONFIG_HOME, PROGRAM

DEFAULT_CONFIG_FILEPATH = CONFIG_HOME / PROGRAM / "config.json"


# Can we do something (mixin?) to automatically add `from_json` to dataclasses
# and to automatically recursively call it?


@dataclasses.dataclass
class RepoConfig:
    default_branch_name: str = "main"

    @classmethod
    def from_json(cls, doc: dict) -> RepoConfig:
        return cls(**doc)


@dataclasses.dataclass
class Config:
    repositories: dict[str, RepoConfig] = dataclasses.field(
        default_factory=dict
    )

    @classmethod
    def from_json(cls, doc: dict) -> Config:
        return cls(
            repositories={
                k: RepoConfig.from_json(v)
                for k, v in doc.get("repositories", {}).items()
            }
        )


@functools.cache
def load_config(filepath: pathlib.Path | None = None) -> Config:
    _path = filepath if filepath is not None else DEFAULT_CONFIG_FILEPATH
    if _path.exists():
        with open(_path) as f:
            return Config.from_json(json.load(f))
    else:
        return Config()


def save_config(config: Config, filepath: pathlib.Path | None = None) -> None:
    _path = filepath if filepath is not None else DEFAULT_CONFIG_FILEPATH
    _path.parent.mkdir(parents=True, exist_ok=True)
    with open(_path, "w+") as f:
        json.dump(dataclasses.asdict(config), f, indent=2)

    load_config.cache_clear()


def set_repository_config(
    config: Config,
    repository: pathlib.Path,
    key: str,
    value: Any,
) -> None:
    repo_path = str(repository.resolve().absolute())
    if repo_path not in config.repositories:
        config.repositories[repo_path] = RepoConfig()
    setattr(config.repositories[repo_path], key, value)


def unset_repository_config(
    config: Config,
    repository: pathlib.Path,
    key: str,
) -> None:
    repo_path = str(repository.resolve().absolute())
    if repo_path not in config.repositories:
        config.repositories[repo_path] = RepoConfig()
    delattr(config.repositories[repo_path], key)
