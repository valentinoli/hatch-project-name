import zipfile
from typing import TYPE_CHECKING

import pytest

from tests.utils import build_project, read_file

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    "project_fixture",
    ["new_project_basic", "new_project_root_elsewhere"],
)
def test_basic(
    request: pytest.FixtureRequest,
    project_fixture: str,
):
    new_project: Path = request.getfixturevalue(project_fixture)
    build_project("-t", "wheel")

    build_dir = new_project / "dist"
    assert build_dir.is_dir()

    artifacts = list(build_dir.iterdir())
    assert len(artifacts) == 1
    [wheel_file] = artifacts

    assert wheel_file.name == "my_app-1.2.3-py2.py3-none-any.whl"

    extraction_directory = new_project.parent / "_archive"
    extraction_directory.mkdir()

    with zipfile.ZipFile(build_dir / wheel_file, "r") as zip_archive:
        zip_archive.extractall(extraction_directory)

    metadata_directory = extraction_directory / "my_app-1.2.3.dist-info"
    assert metadata_directory.is_dir()

    package_directory = extraction_directory / "my_app"
    assert package_directory.is_dir()
    assert len(list(package_directory.iterdir())) == 5

    assert (package_directory / "__init__.py").is_file()
    assert (package_directory / "foo.py").is_file()
    assert (package_directory / "bar.py").is_file()
    assert (package_directory / "baz.py").is_file()

    name_file = package_directory / "_name.py"
    assert name_file.is_file()

    file_contents = read_file(name_file)
    assert (
        file_contents
        == 'project_name = __project_name__ = distribution_name = __distribution_name__ = "my-app"\n'
    )
