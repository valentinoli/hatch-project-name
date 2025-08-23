import os
import subprocess
import sys
from pathlib import Path


def create_file(path: Path):
    with open(path, "a"):
        os.utime(path, None)


def read_file(path: Path):
    with open(path) as f:
        return f.read()


def write_file(
    path: Path,
    contents: str,
):
    with open(path, "w") as f:
        f.write(contents)


def _run_command(*command, **kwargs):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **kwargs,
    )
    stdout, _ = process.communicate()
    stdout = stdout.decode("utf-8")

    if process.returncode:
        raise Exception(stdout)  # noqa: TRY002

    return stdout


def build_project(
    *args,
    **kwargs,
):
    env = os.environ.copy() if "env" not in kwargs else kwargs["env"]
    _run_command(
        sys.executable,
        "-m",
        "hatchling",
        "build",
        *args,
        env=env,
    )
