import os
import pathlib

_get = os.environ.get

# https://specifications.freedesktop.org/basedir/latest/
HOME = pathlib.Path(_get("HOME", _get("USERPROFILE", "."))).resolve()
DATA_HOME = pathlib.Path(_get("XDG_DATA_HOME", HOME / ".local/share"))
STATE_HOME = pathlib.Path(_get("XDG_STATE_HOME", HOME / ".local/state"))
CACHE_HOME = pathlib.Path(_get("XDG_CACHE_HOME", HOME / ".cache"))
CONFIG_HOME = pathlib.Path(_get("XDG_CONFIG_HOME", HOME / ".config"))

# DATA_DIRS = pathlib.Path(_get("XDG_DATA_DIRS", HOME / "/usr/local/share/:/usr/share/"))
# CONFIG_DIRS = pathlib.Path(_get("XDG_CONFIG_DIRS", HOME / "/etc/xdg"))
# RUNTIME_DIR = pathlib.Path(_get("XDG_RUNTIME_DIR"))
