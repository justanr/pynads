from collections.abc import Iterable, Mapping

def _iter_but_not_str_or_map(x):
    return isinstance(x, Iterable) and not isinstance(x, (str, Mapping))
