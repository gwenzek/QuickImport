from typing import Dict

from . import importers

# TODO: make this configurable
KNOWN_PACKAGES = {"std", "builtin"}


def get_name(include: str):
    return include.split(".")[0]


def zig_expand_import(include: str) -> str:
    """Decides whether to append a .zig or not"""
    include = include.strip()
    if not include:
        return '@import("");'

    name = get_name(include)
    if include.endswith(".zig"):
        return f'const {name} = @import("{include}");'

    if "." in include:
        # If the user has started typing ".zig", complete it for them
        base, suffix = include.rsplit(".", 1)
        if "zig".startswith(suffix):
            return f'const {name} = @import("{base}.zig");'

    # Don't add .zig to the standard packages
    # Also tries to detect the build option package.
    if include in KNOWN_PACKAGES or include.endswith("_options"):
        return f'const {name} = @import("{include}");'

    return f'const {name} = @import("{include}.zig");'


@importers.register("Zig")
class ZigImporter(importers.Importer):
    def insertion_regex(self) -> str:
        return r'^(pub )?const .* = @import\("'

    def placeholder(self) -> str:
        return "std"

    def expand(self, include: str) -> str:
        return zig_expand_import(include)


def zig_samples() -> Dict[str, str]:
    return {
        # basic imports
        "std": 'const std = @import("std");',
        "builtin": 'const builtin = @import("builtin");',
        "module.zig": 'const module = @import("module.zig");',
        # completes ".zig":
        "module": 'const module = @import("module.zig");',
        "module.": 'const module = @import("module.zig");',
        "module.z": 'const module = @import("module.zig");',
        "module.zi": 'const module = @import("module.zig");',

    }


def test_zig_expand_samples() -> None:
    for base, expanded in zig_samples().items():
        assert expanded == zig_expand_import(base)
