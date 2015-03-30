from collections.abc import Iterable, Mapping
from inspect import isfunction


__all__ = ('_iter_but_not_str_or_map', '_propagate_self',
           '_single_value_iter', 'with_metaclass', '_get_names',
           '_get_name', 'iscallable')


def _iter_but_not_str_or_map(x):
    """Helper function to differ between iterables and iterables that are
    strings or mappings. This is used for pynads.concrete.List to determine
    if an iterable should be consumed or placed into a single value tuple.
    """
    return isinstance(x, Iterable) and not isinstance(x, (str, Mapping))


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
    ... (MyThing, NewBase, object)
    """
    return meta("NewBase", bases, {})


def iscallable(f):
    """Helper function to determine if a passed object is callable.
    Some versions of Python 3 (3.0 and 3.1) don't have the callable builtin.

    Returns True if the passed object appears callable (has the __call__ method
    defined). However, calling the object may still fail.
    """
    return hasattr(f, '__call__')


def _get_name(f):
    """Attempts to extract name from a given callable.
    """
    # interop with functools.partial and objects that emulate it
    if hasattr(f, 'func') and hasattr(f.func, '__name__'):
        return "partialed {!s}".format(f.func.__name__)
    # callable object that isn't a function
    elif not isfunction(f) and hasattr(f, '__class__'):
        return f.__class__.__name__
    # must be just a regular function
    else:
        return f.__name__


def _get_names(*fs):
    """Helper function for pynads.funcs.compose that intelligently extracts
    names from the passed callables, including already composed functions,
    partially applied functions (functools.partial or similar) and callable
    objects.
    """
    names = []
    for f in fs:
        # extract names from a previously
        # composed group of functions
        if hasattr(f, 'fs'):
            names.extend(_get_names(*f.fs))
        else:
            names.append(_get_name(f))
    return names
