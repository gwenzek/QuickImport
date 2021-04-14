import sublime_plugin


def cpp_expand_import(include: str) -> str:
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
