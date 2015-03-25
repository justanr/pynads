from collections.abc import Iterable, Mapping


__all__ = ('_iter_but_not_str_or_map', '_propagate_self',
           'with_metaclass')


def _iter_but_not_str_or_map(x):
    return isinstance(x, Iterable) and not isinstance(x, (str, Mapping))


def _propagate_self(self, *_):
    """Nothing, Left and potentially other monads are special in that they
    represent some sort of failure. Rather than allowing further
    computations, they simply propagate themselves instead.
    """
    return self


def with_metaclass(meta, *bases):
    """Creates an anonymous object with a metaclass. Allows compatibility
    between Python2 and Python3.
    
    >>> class MyThing(with_metaclass(type)):
    ...     pass
    >>> MyThing.__mro__
    ... (MyThing, NewBase, object)
    """
    return meta("NewBase", bases, {})
