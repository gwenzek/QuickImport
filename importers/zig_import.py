from typing import Dict

from . import importers

# TODO: make this configurable
KNOWN_PACKAGES = {"std", "builtin"}


def get_name(include: str):
    include = include.rsplit("/", 1)[-1]
    return include.split(".")[0]


def zig_expand_import(include: str) -> str:
    """Decides whether to append a .zig or not"""
    include = include.strip()
    if not include:
        return '@import("");'

    if "=" in include or "@" in include:
        # bailout, the user want to type everything themselves
        return include

    name = get_name(include)
    if include.endswith(".zig"):
        return f'const {name} = @import("{include}");'

    if " " in include:
        # the user wants to combine import and field access:
        # const Foo = @import("foo.zig").Foo;
        base, suffix = include.rsplit(" ", 1)
        return f"const {suffix} = {zig_import(base)}.{suffix};"

    if "." in include:
        base, suffix = include.rsplit(".", 1)
        if "zig".startswith(suffix) or base == ".":
            # don't mistake .zig suffix and ../ prefix for submodule alias
            pass
        else:
            # If the user is trying to alias a submodule: "std.testing"
            return f"const {suffix} = {include};"

    return f"const {name} = {zig_import(include)};"


def zig_import(include: str) -> str:
    """Complete .zig suffix when needed.

    Don't add .zig to std package or build option package.
    """
    if include in KNOWN_PACKAGES or include.endswith("_options"):
        return f'@import("{include}")'
    elif "." in include:
        base, suffix = include.rsplit(".", 1)
        if "zig".startswith(suffix):
            # Complete .zig suffix
            return f'@import("{base}.zig")'
        elif include.startswith("../"):
            # Relative import
            return f'@import("{include}.zig")'
        return f'@import("{include}")'
    else:
        return f'@import("{include}.zig")'


@importers.register("Zig")
class ZigImporter(importers.Importer):
    def insertion_regex(self) -> str:
        return r'^(pub )?const .* = @import\("'

    def placeholder(self) -> str:
        return "std"

    def expand(self, include: str) -> str:
        return zig_expand_import(include)


ZIG_SAMPLES = {
    # basic imports
    "std": 'const std = @import("std");',
    "builtin": 'const builtin = @import("builtin");',
    "module.zig": 'const module = @import("module.zig");',
    "../module": 'const module = @import("../module.zig");',
    # alias a module from std
    "std.testing": "const testing = std.testing;",
    # completes ".zig":
    "module": 'const module = @import("module.zig");',
    "module.": 'const module = @import("module.zig");',
    "module.z": 'const module = @import("module.zig");',
    "module.zi": 'const module = @import("module.zig");',
    # bailout:
    "const a =": "const a =",
    "@imp": "@imp",
    # import and access
    "module Clz": 'const Clz = @import("module.zig").Clz;',
    "../module Clz": 'const Clz = @import("../module.zig").Clz;',
    "../module.z Clz": 'const Clz = @import("../module.zig").Clz;',
}


def test_zig_expand_samples() -> None:
    for base, expanded in ZIG_SAMPLES.items():
        assert expanded == zig_expand_import(base)
