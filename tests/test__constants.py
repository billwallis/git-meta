import importlib
import pathlib

import pytest

from git_meta import constants


def test__constants__default_values_are_used(monkeypatch: pytest.MonkeyPatch):
    env_vars = [
        "HOME",
        "USERPROFILE",
        "XDG_DATA_HOME",
        "XDG_STATE_HOME",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
    ]
    for env_var in env_vars:
        monkeypatch.delenv(env_var, raising=False)

    # We need to reload the module since we need the env vars to have been
    # unset _before_ defining the constants
    importlib.reload(constants)
    here = pathlib.Path.cwd()

    assert constants.HOME == here
    assert constants.DATA_HOME == here / ".local/share"
    assert constants.STATE_HOME == here / ".local/state"
    assert constants.CACHE_HOME == here / ".cache"
    assert constants.CONFIG_HOME == here / ".config"


def test__constants__environment_variables_are_used(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    env_vars = {
        "HOME": tmp_path,
        "USERPROFILE": tmp_path,
        "XDG_DATA_HOME": tmp_path / "data",
        "XDG_STATE_HOME": tmp_path / "state",
        "XDG_CACHE_HOME": tmp_path / "cache",
        "XDG_CONFIG_HOME": tmp_path / "config",
    }
    for env_var_name, env_var_value in env_vars.items():
        monkeypatch.setenv(name=env_var_name, value=str(env_var_value))

    # We need to reload the module since we need the env vars to have been
    # updated _before_ defining the constants
    importlib.reload(constants)

    assert constants.HOME == tmp_path
    assert constants.DATA_HOME == tmp_path / "data"
    assert constants.STATE_HOME == tmp_path / "state"
    assert constants.CACHE_HOME == tmp_path / "cache"
    assert constants.CONFIG_HOME == tmp_path / "config"
