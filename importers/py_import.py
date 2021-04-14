import os
import typing
from typing import Dict

PY_KNOWN_IMPORTS = {
    "Path": "pathlib Path",
    "np": "numpy as np",
    "pd": "pandas as pd",
}

for typename in dir(typing):
    if typename[0] == typename[0].upper():
        PY_KNOWN_IMPORTS[typename] = "typing " + typename


def py_expand_import(include: str) -> str:
    include = include.strip()

    if include.startswith("import ") or include.startswith("from "):
        # allow user to bailout by typing the full line themselves
        return include

    # Do resolution first in case it contains an alias.
    include = PY_KNOWN_IMPORTS.get(include, include)
    alias = ""
    if " as " in include:
        # TODO: do string splitting
        include, alias = include.rsplit(" as ", 1)
        alias = " as " + alias

    # Try resolution again now that we have stripped alias.
    include = PY_KNOWN_IMPORTS.get(include, include)

    if os.sep in include:
        include, ext = include.rsplit(os.extsep, 1)
        include = include.replace(os.sep, ".")

    if " " not in include:
        return "import " + include + alias

    module, name = include.split(" ", 1)
    return f"from {module} import {name}{alias}"


def py_samples() -> Dict[str, str]:
    return {
        # basic imports
        "foo bar": "from foo import bar",
        "foo/bar.py": "import foo.bar",
        # aliased imports
        "np": "import numpy as np",
        "foobar as bar": "import foobar as bar",
        "foo/bar.py as foobar": "import foo.bar as foobar",
        "foo bar as foobar": "from foo import bar as foobar",
        "Sequence as Seq": "from typing import Sequence as Seq",
        # type imports
        "Any": "from typing import Any",
        "Sequence": "from typing import Sequence",
        # yes there is typing.re, but we don't want to import that by default
        "re": "import re",
        # Detect when we need to bailout
        "import np": "import np",
        "import foobar as bar": "import foobar as bar",
        "import foo bar": "import foo bar",
        "import Sequence": "import Sequence",
        "from np": "from np",
    }


def test_py_expand_samples() -> None:
    for base, expanded in py_samples().items():
        assert expanded == py_expand_import(base)
