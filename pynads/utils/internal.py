"""A collection of utilities used internally by pynads. By no means are they
off limits for playing with, however, they aren't exported by pynads.
"""

from collections import Iterable, Mapping
from inspect import isfunction


__all__ = ('_iter_but_not_str_or_map', '_propagate_self',
           '_single_value_iter', 'with_metaclass', '_get_names',
           '_get_name', 'iscallable', 'chain_dict_update', 'Instance')


def _iter_but_not_str_or_map(maybe_iter):
    """Helper function to differ between iterables and iterables that are
    strings or mappings. This is used for pynads.concrete.List to determine
    if an iterable should be consumed or placed into a single value tuple.
    """
    return (isinstance(maybe_iter, Iterable) and
            not isinstance(maybe_iter, (str, Mapping)))


def _propagate_self(self, *_, **__):
    """Some object methods, rather doing anything meaningful with their input,
    would prefer to simply propagate themselves along. For example, this is used
    in two different ways with Just and Nothing.

    When calling any of the or_else and or_call methods on Just, there is
    already a value provided (whatever the Just is) so these methods simply
    ignore their inputs and propagate the Just along.

    However, when filtering, fmapping, applying or binding a Nothing
    (and also a Left), this method is used to signal some sort of failure in the
    chain and propagate the original object along instead.
    """
    return self


def _single_value_iter(x):
    """Helper function for pynads.concrete.list.Generator that allows
    placing a single value into an iteration context.
    """
    yield x


def with_metaclass(meta, bases=(object,), name=None):
    """Creates an anonymous object with a metaclass. Allows compatibility
    between Python2 and Python3.

    >>> class MyThing(with_metaclass(type)):
    ...     pass
    >>> MyThing.__mro__
    ... (MyThing, typeBase, object)
    """
    name = name or "{!s}Base".format(meta.__name__)
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


class Instance(object):
    """Helper to allow attaching an instance of a class to the class as a class
    attribute.

    .. code-block:: python
        class Thing(object):
            thing = Instance()

    `Thing.thing`` is an instance of the class itself. This is useful for
    monoids whos mempty is just an empty instance of the class.

    Additionally, if any arguments need to be provided, for whatever reason,
    they can be inserted via the descriptor's instantiation.

    .. code-block:: python
        class Thing(object):
            thing = Instance(hello="world")

            def __init__(self, hello):
                self.hello = hello

    And then the instance is created with those values. The instance is cached
    inside the descriptor and only created once per class.
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self._inst = None

    def __get__(self, _, cls):
        if self._inst is None:
            self._inst = cls(*self.args, **self.kwargs)
        return self._inst
