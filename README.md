# hatch-project-name

| | |
| --- | --- |
| CI/CD | [![CI - Test](https://github.com/valentinoli/hatch-project-name/actions/workflows/test.yml/badge.svg)](https://github.com/valentinoli/hatch-project-name/actions/workflows/test.yml) [![CD - Build](https://github.com/valentinoli/hatch-project-name/actions/workflows/build.yml/badge.svg)](https://github.com/valentinoli/hatch-project-name/actions/workflows/build.yml) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/hatch-project-name.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/hatch-project-name/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-project-name.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/hatch-project-name/) |
| Meta | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://docs.astral.sh/uv/) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://mypy.readthedocs.io/en/stable/) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) |

-----

This provides a build hook plugin for [Hatch](https://github.com/pypa/hatch) that writes the project name defined in `pyproject.toml` to a file.

**Table of Contents**

- [Configuration](#configuration)
  - [Build hook options](#build-hook-options)
  - [Editable installs](#editable-installs)
- [Rationale](#rationale)
- [License](#license)

## Configuration

The [build hook plugin](https://hatch.pypa.io/latest/plugins/build-hook/reference/) name is `project-name`.

- ***pyproject.toml***

    ```toml
    [project]
    name = "my-project"

    [tool.hatch.build.hooks.project-name]
    dependencies = ["hatch-project-name"]
    name-file = "src/my_project/_name.py"
    ```

- ***hatch.toml***

    ```toml
    [project]
    name = "my-project"

    [build.hooks.project-name]
    dependencies = ["hatch-project-name"]
    name-file = "src/my_project/_name.py"
    ```

Building the project will generate the file

- ***_name.py***

    ```python
    project_name = __project_name__ = distribution_name = __distribution_name__ = "my-project"
    ```

> [!NOTE]
> This file is generated and should not be committed to version control. Remember to add it to your `.gitignore`. The plugin will automatically include it in your project’s built sdists and wheels.

Now you can import the project name:

```py
from my_project import project_name

print(project_name)
```

### Build hook options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `name-file` | `str` | ***REQUIRED*** | The relative path to the Python file that gets updated with the project name. |

### Editable installs

The name file is only updated upon install or build. Thus the name in an [editable install](https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs) (Hatch's [dev mode](https://hatch.pypa.io/latest/config/build/#dev-mode)) will be incorrect if the name is changed in `pyproject.toml` and the project is not rebuilt.

## Rationale

The [Hatch project name](https://hatch.pypa.io/latest/config/metadata/#name) is a required field defined in the `[project]` table in `pyproject.toml`:

```toml
[project]
name = "my-project"
```

The [`[project]`](https://packaging.python.org/en/latest/specifications/pyproject-toml/#declaring-project-metadata-the-project-table) table specifies the project’s [core metadata](https://packaging.python.org/en/latest/specifications/core-metadata/#core-metadata). The [`name`](https://packaging.python.org/en/latest/specifications/pyproject-toml/#name) project metadata field corresponds to the distribution package [`Name`](https://packaging.python.org/en/latest/specifications/core-metadata/#core-metadata-name).

> A distribution package is a piece of software that you can install. Most of the time, this is synonymous with “project”. When you type `pip install pkg`, or when you write `dependencies = ["pkg"]` in your `pyproject.toml`, pkg is the name of a distribution package. [...]

> Most of the time, a distribution package provides one single import package (or non-package module), with a matching name. For example, `pip install numpy` lets you `import numpy`.

> However, this is only a convention. PyPI and other package indices *do not enforce any relationship* between the name of a distribution package and the import packages it provides. [...]

Source: [Distribution package vs. import package](https://packaging.python.org/en/latest/discussions/distribution-package-vs-import-package/)

The project/distribution name might be needed in code for various reasons. One might be that you are using the `importlib.metadata` standard library module to access project metadata. For instance:

```py
from importlib import metadata

distribution_name = "my-project"
version = metadata.version(distribution_name)
```

Or you might simply want to log the name.

```py
import logging

logger = logging.getLogger()

project_name = "my-project"
logger.info(f"Project name: {project_name}")
```

The Python standard library does not provide a standardized function to programmatically access the current project/distribution name that works without limitations. This is because, as quoted above, no relationship is enforced between the name of a distribution package and the importable import packages it provides. You can of course just hardcode the project/distribution name as in the examples above, but this is not ideal since it is preferable to maintain `pyproject.toml` as the single source of truth for your project metadata.

The following method (originally [posted here](https://github.com/pypa/hatch/issues/2019)) is the best you can achieve with the standard library [`importlib.metadata`](https://docs.python.org/3/library/importlib.metadata.html) module, but it has important limitations.

Say one top-level module or import package name in your project is `my_tool`. Then you can do:

```py
from importlib import metadata

def get_project_name() -> str:
    pkg_name = "my_tool"
    pkg_to_dists = metadata.packages_distributions()
    return pkg_to_dists[pkg_name][0]
```

This uses [`importlib.metadata.packages_distributions()`](https://docs.python.org/3/library/importlib.metadata.html#importlib.metadata.packages_distributions) to map one of the top-level names to the project/distribution name.

This method has the following limitations:

1. It does not work for namespace packages as the top-level namespace will map to potentially multiple distributions.
2. It does not work with an editable install (unless you are using `setuptools`, see more details [here](https://github.com/pypa/packaging-problems/issues/609) and [here](https://github.com/python/importlib_metadata/issues/402)). The main reason is that `importlib.metadata` "operates on third-party distribution packages installed into Python’s site-packages directory".

Alternatively, Hatch provides a CLI command `hatch project metadata name` that outputs the project name. However, this is cumbersome to use in Python code as you need to use something like `subprocess.run` to invoke the command in a working directory that contains the project source code. It additonally requires that Hatch is installed.

An even better alternative then is to generate a file containing the project name on-the-fly and include it in the distribution—and this is exactly what the `hatch-project-name` build hook does! Since the file is generated, you should exclude it from version control. This maintains `pyproject.toml` as the source of truth for the project name. Furthermore, Python project templates built with tools like cookiecutter and Copier will not need to parameterize the project name in Python source files.

## License

`hatch-project-name` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
