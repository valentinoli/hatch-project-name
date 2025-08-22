from contextlib import nullcontext as does_not_raise
from pathlib import Path

import pytest

from hatch_project_name.plugin import ProjectNameBuildHook


@pytest.mark.parametrize(
    ("config", "expected_exception"),
    [
        (
            {"name-file": "foo/_name.py"},
            does_not_raise(),
        ),
        (
            {"name-file": 9000},
            pytest.raises(
                TypeError,
                match="Option `name-file` for build hook `project-name` must be a string",
            ),
        ),
        (
            {},
            pytest.raises(
                ValueError,
                match="Option `name-file` for build hook `project-name` is required",
            ),
        ),
    ],
)
def test_name_file(
    new_project_basic: Path,
    config: dict,
    expected_exception,
):
    build_dir = str(new_project_basic / "dist")
    build_hook = ProjectNameBuildHook(
        str(new_project_basic),
        config,
        None,
        None,  # type: ignore[arg-type]
        build_dir,
        "wheel",
    )

    with expected_exception:
        assert build_hook.config_name_file == config["name-file"]
