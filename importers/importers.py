import abc
import typing
from typing import Callable, Dict, Type

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
        """
        ...

    def insertion_point(self, view: "sublime.View") -> int:
        """Where to insert the import."""
        includes = view.find_all(self.insertion_regex())
        if len(includes) > 0:
            return view.line(includes[-1]).end() + 1
        return 0


IMPORTER_REGISTRY: Dict[str, Importer] = {}


def register(language: str) -> Callable[[Type[Importer]], Type[Importer]]:
    """Register an Importer class to the language."""
    language = language.lower()

    def _register(cls: Type[Importer]) -> Type[Importer]:
        assert (
            language not in IMPORTER_REGISTRY
        ), f"Found 2 importers for language {language}."
        IMPORTER_REGISTRY[language] = cls()
        return cls

    return _register


def resolve_importer(language: str) -> Importer:
    language = language.lower()
    assert (
        language in IMPORTER_REGISTRY
    ), f"Unknown language {language!r}, chose from {IMPORTER_REGISTRY.keys()}"
    return IMPORTER_REGISTRY[language]
