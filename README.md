# QuickImport

A minimalist SublimeText plugin
to make it easier to import 
Python modules
or C++ headers.

## Stay focus

This plugin comes with a single command,
`quick_import`
that allows you to 
insert a line
at the top of the file.

This allows breaking your flow
when you have to stop writing your function
to go at the top of the file 
and add a stupid `import functools`

## Unobstrusive

This plugins will help you
write the import statement.
Typing `numpy` will be translated to `import numpy`.
A live preview of the result
is shown below the input box,
so there are no suprises.

No magic is going on,
no automatic detection of availables modules/header.
Just you and your fingers.

## Installation

Not on PackageControl yet.
Install it by cloning the repo
into your Packages directory.

No keybindings is added by default.
I personally use this:

```json
{"keys": ["super+i"], "command": "quick_import", "context": [{"key": "selector", "operand": "source.python"}]},
{"keys": ["super+i"], "command": "quick_import", "context": [{"key": "selector", "operand": "source.c++"}]},
```

## Extensible

Since the plugin is pretty minimalistic
supporting another language is pretty easy.
`CppImporter` is literally 24 lines long.
