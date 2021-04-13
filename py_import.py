import sublime
import sublime_plugin

import logging

from pathlib import Path
logger = logging.getLogger(__file__)

KNOWN_IMPORT = {
    "Path": "pathlib Path",
    "np": "numpy as np",
    "List": "typing List"
}


def py_full_include(include: str) -> str:
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

    if include in KNOWN_IMPORT:
        include = KNOWN_IMPORT[include]

    if "/" in include:
        included_file = Path(include)
        if included_file.exists():
            include = ".".join(p.name for p in included_file.parents[::-1])
            include += included_file.stem

    if " " not in include:
        return "import " + include + alias

    module, name = include.split(" ", 1)
    return "from {} import {}{}".format(module, name, alias)


class IncludeInputHandler(sublime_plugin.TextInputHandler):
    def name(self) -> str:
        return "include"

    def placeholder(self):
        return "numpy as np"

    def preview(self, text):
        return py_full_include(text)


class QuickImportPythonCommand(sublime_plugin.TextCommand):
    """Add an #include statement."""

    def run(self, edit: None, include: str):
        print("calling PyImportCommand.run")
        if not include:
            return

        view = self.view
        last_include = view.line(view.find_all("^import")[-1])
        view.insert(edit, last_include.end(), "\n" + py_full_include(include))

    def input(self, args):
        print("calling PyImportCommand.input({})".format(args))
        if "include" not in args:
            return IncludeInputHandler()

    def description(self):
        return self.__doc__

    # def is_enabled(self):
    #     return self.view.match_selector(0, "source.py")
