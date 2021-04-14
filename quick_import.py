import abc
from pathlib import Path
from typing import Callable, Dict, Type

import sublime
import sublime_plugin

from . import importers


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
        selection = self.view.sel()[0]
        selected_text = "" if selection.empty() else self.view.substr(selection)
        return QuickImportInputHandler(importer, selected_text)

    def description(self):
        return self.__doc__

    def is_enabled(self):
        language = resolve_language(self.view)
        return language in IMPORTER_REGISTRIES


class QuickImportInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, importer: Importer, selected_text: str):
        self.importer = importer
        self.selected_text = selected_text

    def name(self) -> str:
        return "include"

    def placeholder(self) -> str:
        return self.importer.placeholder()

    def preview(self, text: str) -> str:
        return self.importer.expand(text)

    def initial_text(self) -> str:
        return self.selected_text


def resolve_language(view: sublime.View):
    syntax = Path(view.settings().get("syntax"))
    return syntax.stem.lower()
