import abc
import functools
import typing
from pathlib import Path
from typing import Callable, Dict, Optional, Type

import sublime
import sublime_plugin

if typing.TYPE_CHECKING:
    import importers
else:
    from . import importers


class QuickImportInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, importer: importers.Importer, selected_text: str):
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


class QuickImportCommand(sublime_plugin.TextCommand):
    """Add an import statement at the top of the file"""

    def run(self, edit: sublime.Edit, include: str) -> None:
        importer = self.resolve_importer()
        if not importer or not include:
            return

        insertion_point = importer.insertion_point(self.view)
        include = importer.expand(include)
        self.view.insert(edit, insertion_point, include + "\n")

    def input(self, args: dict) -> Optional[QuickImportInputHandler]:
        importer = self.resolve_importer()
        if importer is None:
            return None
        selection = self.view.sel()[0]
        selected_text = "" if selection.empty() else self.view.substr(selection)
        return QuickImportInputHandler(importer, selected_text)

    def description(self):
        return self.__doc__

    def is_enabled(self) -> bool:
        return self.resolve_importer() is not None

    @functools.lru_cache()
    def resolve_importer(self) -> Optional[importers.Importer]:
        syntax = Path(self.view.settings().get("syntax"))
        language = syntax.stem.lower()
        return importers.resolve_importer(language)


def plugin_loaded() -> None:
    print("[QuickImport] Loaded QuickImport for", importers.supported_languages())
