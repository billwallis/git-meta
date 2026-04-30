import pathlib
import subprocess
from collections.abc import Iterable
from typing import Any

HERE = pathlib.Path(__file__).parent

type GitCompletedProcess = (
    subprocess.CompletedProcess[str]
    | subprocess.CompletedProcess[bytes]
    | subprocess.CompletedProcess[Any]
)


def _git_cmd(
    args: Iterable[str],
    git_dir: pathlib.Path | None = None,
) -> GitCompletedProcess:
    cmds = ("git",) if git_dir is None else ("git", "-C", git_dir)
    return subprocess.run(
        args=(*cmds, *args),
        check=False,  # DON'T raise an exception on non-zero return codes
        capture_output=True,
    )


def run_git_cmd(
    args: Iterable[str],
    git_dir: pathlib.Path | None = None,
) -> tuple[int, str, str]:
    proc = _git_cmd(args=args, git_dir=git_dir)

    assert isinstance(proc.stdout, bytes)  # noqa: S101
    assert isinstance(proc.stderr, bytes)  # noqa: S101

    return (
        proc.returncode,
        proc.stdout.decode().rstrip(),
        proc.stderr.decode().rstrip(),
    )
