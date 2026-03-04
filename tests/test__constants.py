import importlib
import pathlib

import pytest

from git_meta import constants


def test__home_path_defaults_are_used(monkeypatch: pytest.MonkeyPatch):
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
