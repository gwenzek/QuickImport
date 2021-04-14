import sublime
import sublime_plugin

import abc
from pathlib import Path
from typing import Callable, Dict, Type
from .py_import import py_expand_import
from .cpp_import import cpp_expand_import

IMPORTER_REGISTRIES: Dict[str, "Importer"] = {}


class QuickImportInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, importer: "Importer"):
        self.importer = importer

    def name(self) -> str:
        return "include"

    def placeholder(self) -> str:
        return self.importer.placeholder()

    def preview(self, text: str) -> str:
        return self.importer.expand(text)


class QuickImportCommand(sublime_plugin.TextCommand):
    """Add an import statement at the top of the file"""

    def run(self, edit: None, include: str):
        importer = resolve_importer(self.view)

        if not include:
            return

        insertion_point = importer.insertion_point(self.view)
        include = importer.expand(include)
        self.view.insert(edit, insertion_point, include + "\n")

    def input(self, args):
        importer = resolve_importer(self.view)
        return QuickImportInputHandler(importer)

    def description(self):
        return self.__doc__

    def is_enabled(self):
        language = resolve_language(self.view)
        return language in IMPORTER_REGISTRIES


class Importer(abc.ABC):
    def insertion_point(self, view: sublime.View) -> int:
        ...

    def placeholder(self) -> str:
        ...

    def expand(self, include: str) -> str:
        ...


def register(language: str) -> Callable[[Type[Importer]], Type[Importer]]:
    language = language.lower()

    def _register(cls: Type[Importer]) -> Type[Importer]:
        assert (
            language not in IMPORTER_REGISTRIES
        ), f"Found 2 importers for language {language}."
        IMPORTER_REGISTRIES[language] = cls()
        return cls

    return _register


def resolve_language(view: sublime.View):
    syntax = Path(view.settings().get("syntax"))
    return syntax.stem.lower()


def resolve_importer(view: sublime.View) -> "Importer":
    language = resolve_language(view)
    assert (
        language in IMPORTER_REGISTRIES
    ), f"Unknown language {language!r}, chose from {IMPORTER_REGISTRIES.keys()}"
    return IMPORTER_REGISTRIES[language]


@register("Python")
class PythonImporter(Importer):
    def insertion_point(self, view: sublime.View) -> int:
        last_include = view.line(view.find_all("^import")[-1])
        return last_include.end() + 1

    def placeholder(self) -> str:
        return "numpy as np"

    def expand(self, include: str) -> str:
        return py_expand_import(include)


@register("C++")
class CppImporter(Importer):
    def insertion_point(self, view: sublime.View) -> int:
        last_include = view.line(view.find_all("^#include ")[-1])
        return last_include.end() + 1

    def placeholder(self) -> str:
        return "vector"

    def expand(self, include: str) -> str:
        return cpp_expand_import(include)
