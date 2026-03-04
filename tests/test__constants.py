import pathlib
import sys

import pytest


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

    # We need to import _inside_ the test since we need the env vars to have
    # been unset _before_ importing the constants. There has to be a better
    # alternative, though
    sys.modules.pop("git_meta.constants", None)
    from git_meta import constants  # noqa: PLC0415

    here = pathlib.Path.cwd()

    assert constants.HOME == here
    assert constants.DATA_HOME == here / ".local/share"
    assert constants.STATE_HOME == here / ".local/state"
    assert constants.CACHE_HOME == here / ".cache"
    assert constants.CONFIG_HOME == here / ".config"
