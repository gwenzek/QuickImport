from __future__ import annotations
import abc
import typing
from typing import Callable, Dict, Optional, Sequence, Type

if typing.TYPE_CHECKING:
    import sublime


class Importer(abc.ABC):
    def expand(self, include: str) -> str:
        """The core of the importer, converts a module name into a full import."""
        ...

    def placeholder(self) -> str:
        """Placeholder for the input box.

        Should be use to give a hint to the user of what kind of input can be handled.
        """
        ...

    def insertion_regex(self) -> str:
        """The import will be inserted where this regex is found in the file.

        We assumes that the imports will be sorted by another tool.
        Modules are free to override `insertion_point` to do something smarter
        """
        ...

    def insertion_point(self, view: sublime.View) -> int:
        """Where to insert the import."""
        includes = view.find_all(self.insertion_regex())
        if not includes:
            return 0
        return view.line(includes[-1]).end() + 1


IMPORTER_REGISTRY: Dict[str, Importer] = {}


def register(language: str) -> Callable[[Type[Importer]], Type[Importer]]:
    """Register an Importer implementation for a language.

    The language name must match the one used by Sublime Text.
    """
    language = language.lower()

    def _register(cls: Type[Importer]) -> Type[Importer]:
        assert (
            language not in IMPORTER_REGISTRY
        ), f"Found 2 importers for language {language}."
        IMPORTER_REGISTRY[language] = cls()
        return cls

    return _register


def resolve_importer(language: str) -> Optional[Importer]:
    language = language.lower()
    return IMPORTER_REGISTRY.get(language)


def supported_languages() -> Sequence[str]:
    return list(IMPORTER_REGISTRY.keys())
