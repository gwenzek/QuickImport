import sublime
import sublime_plugin

import logging
import typing

from pathlib import Path

logger = logging.getLogger(__file__)

PY_KNOWN_IMPORTS = {
    "Path": "pathlib Path",
    "np": "numpy as np",
}

for typename in dir(typing):
    if typename[0] == typename[0].upper():
        PY_KNOWN_IMPORTS[typename] = "typing " + typename


def py_expand_import(include: str) -> str:
    include = include.strip()

    if include.startswith("import ") or include.startswith("from "):
        # include looks ok
        return include

    # Extract alias ASAP
    alias = ""
    if " as " in include:
        # TODO: do string splitting
        include, alias = include.rsplit(" as ", 1)
        alias = " as " + alias

    include = PY_KNOWN_IMPORTS.get(include, include)

    if "/" in include:
        included_file = Path(include)
        if included_file.exists():
            include = ".".join(p.name for p in included_file.parents[::-1])
            include += included_file.stem

    if " " not in include:
        return "import " + include + alias

    module, name = include.split(" ", 1)
    return "from {} import {}{}".format(module, name, alias)
