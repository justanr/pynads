"""A collection of utilities used internally by pynads. By no means are they
off limits for playing with, however, they aren't exported by pynads.
"""

from collections import Iterable, Mapping
from inspect import isfunction


__all__ = ('_iter_but_not_str_or_map', '_propagate_self',
           '_single_value_iter', 'with_metaclass', '_get_names',
           '_get_name', 'iscallable', 'chain_dict_update')


def _iter_but_not_str_or_map(maybe_iter):
    """Helper function to differ between iterables and iterables that are
    strings or mappings. This is used for pynads.concrete.List to determine
    if an iterable should be consumed or placed into a single value tuple.
    """
    return (isinstance(maybe_iter, Iterable) and
            not isinstance(maybe_iter, (str, Mapping)))


def _propagate_self(self, *_, **__):
    """Nothing, Left and potentially other monads are special in that they
    represent some sort of failure. Rather than allowing further
    computations, they simply propagate themselves instead.
    """
    return self


def _single_value_iter(x):
    """Helper function for pynads.concrete.list.Generator that allows
    placing a single value into an iteration context.
    """
    yield x


def with_metaclass(meta, *bases):
    """Creates an anonymous object with a metaclass. Allows compatibility
    between Python2 and Python3.

    >>> class MyThing(with_metaclass(type)):
    ...     pass
    >>> MyThing.__mro__
    ... (MyThing, typeBase, object)
    """
    name = "{!s}Base".format(meta.__name__)
    return meta(name, bases, {})


def iscallable(func):
    """Helper function to determine if a passed object is callable.
    Some versions of Python 3 (3.0 and 3.1) don't have the callable builtin.

    Returns True if the passed object appears callable (has the __call__ method
    defined). However, calling the object may still fail.
    """
    return hasattr(func, '__call__')


def _get_name(obj):
    """Attempts to extract name from a given object.
    """
    try:
        # interop with functools.partial and objects that emulate it
        if hasattr(obj, 'func') and hasattr(obj.func, '__name__'):
            return "partialed {!s}".format(obj.func.__name__)
        # callable object that isn't a function
        elif not isfunction(obj) and hasattr(obj, '__class__'):
            return obj.__class__.__name__
        # must be just a regular function
        else:
            return obj.__name__
    except AttributeError:
        return ''


def _get_names(*objs):
    """Helper function for pynads.funcs.compose that intelligently extracts
    names from the passed callables, including already composed functions,
    partially applied functions (functools.partial or similar) and callable
    objects.
    """
    names = []
    for obj in objs:
        # extract names from a previously
        # composed group of functions
        if hasattr(obj, 'fs'):
            names.extend(_get_names(*obj.fs))
        else:
            names.append(_get_name(obj))
    return names


def chain_dict_update(*ds):
    """Updates multiple dictionaries into one dictionary.
    If the same key appears multiple times, then the last appearance wins.

    >>> m, n, o = {'a':10}, {'b':7}, {'a':4}
    >>> chain_dict_updates(m, n, o)
    ... {'b': 7, 'a': 4}
    """
    dct = {}
    for d in ds:
        dct.update(d)
    return dct
