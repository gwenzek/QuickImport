import sublime_plugin


def full_include(include):
  """Decides whether to wrap the include in "..." or <...>."""
  include = include.strip()
  if include.endswith('.h'):
    return '#include "%s"' % include
  elif include[0] == '"' or include[-1] == '"':
    return '#include %s' % include
  elif include[0] == '<' or include[-1] == '>':
    return '#include %s' % include
  else:
    return '#include <%s>' % include


class IncludeInputHandler(sublime_plugin.TextInputHandler):
  def name(self):
    return "include"

  def placeholder(self):
    return '<vector>'

  def confirm(self, text):
    return text

  def preview(self, text):
    return full_include(text)


class QuickImportCpp(sublime_plugin.TextCommand):
  """Add an #include statement."""

  def run(self, edit, include):
    if not include:
      return

    view = self.view
    last_include = view.line(view.find_all('^#include ')[-1])
    view.insert(
        edit, last_include.end(), '\n' + full_include(include))

  def input(self, args):
    if "include" not in input:
      return IncludeInputHandler()

  def description(self):
    return self.__doc__

  def is_enabled(self):
    return self.view.match_selector(0, 'source.c++')
