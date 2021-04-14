from typing import Dict


def cpp_expand_import(include: str) -> str:
    """Decides whether to wrap the include in "..." or <...>."""
    include = include.strip()
    if include.endswith(".h"):
        return '#include "%s"' % include
    elif include[0] == '"' or include[-1] == '"':
        return "#include %s" % include
    elif include[0] == "<" or include[-1] == ">":
        return "#include %s" % include
    else:
        return "#include <%s>" % include


def cpp_samples() -> Dict[str, str]:
    return {
        # basic imports
        "vector": "#include <vector>",
        "vector.h": '#include "vector.h"',
        # bailout:
        "<vector.h>": "#include <vector.h>",
        '"vector"': '#include "vector"',
        # TODO: bailout with fix
        # "<vector.h": "#include <vector.h>",
    }


def test_cpp_expand_samples() -> None:
    for base, expanded in cpp_samples().items():
        assert expanded == cpp_expand_import(base)
