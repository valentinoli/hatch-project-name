import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import pytest

from tests.utils import create_file, write_file


@contextmanager
def create_project(
    directory: Path,
    metadata: str,
    *,
    nested=False,
) -> Generator[Path, None, None]:
    root_dir = project_dir = directory / "my-app"
    root_dir.mkdir()

    gitignore_file = root_dir / ".gitignore"
    write_file(gitignore_file, "/my_app/_name.py")

    if nested:
        project_dir = root_dir / "project"
        project_dir.mkdir()

    project_file = project_dir / "pyproject.toml"
    write_file(project_file, metadata)

    package_dir = project_dir / "my_app"
    os.mkdir(package_dir)

    create_file(package_dir / "__init__.py")
    create_file(package_dir / "foo.py")
    create_file(package_dir / "bar.py")
    create_file(package_dir / "baz.py")

    origin = Path.cwd()
    os.chdir(project_dir)
    try:
        yield project_dir
    finally:
        os.chdir(origin)


@pytest.fixture(
    scope="session",
)
def new_project_basic_toml() -> str:
    return """\
[build-system]
requires = [
    "hatchling",
]
build-backend = "hatchling.build"

[project]
name = "my-app"
version = "1.2.3"

[tool.hatch.build.targets.wheel.hooks.project-name]
name-file = "my_app/_name.py"
"""


@pytest.fixture
def new_project_basic(
    tmp_path: Path,
    new_project_basic_toml: str,
) -> Generator[Path, None, None]:
    with create_project(
        tmp_path,
        new_project_basic_toml,
    ) as project:
        yield project


@pytest.fixture
def new_project_root_elsewhere(
    tmp_path: Path,
    new_project_basic_toml: str,
) -> Generator[Path, None, None]:
    with create_project(
        tmp_path,
        new_project_basic_toml,
        nested=True,
    ) as project:
        yield project
