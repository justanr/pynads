"""This module serves a singular purpose: Being able to accept an arbitrary
object and determine the best way to use mappend and mconcat on it. Sometimes
that best way is not at all.
"""

from collections import Sequence, Mapping, Set
from itertools import chain
from numbers import Number
from operator import add, or_
from .compat import filter, reduce
from .internal import chain_dict_update

_builtin_types = (float, int, str, list, tuple, set, frozenset, dict)
_generic_types = (Number, str, Sequence, Mapping, Set)

_builtin_mempties = {
    float: 0.0,
    int: 0,
    complex: 0j,
    str: '',
    list: [],
    tuple: (),
    set: set(),
    frozenset: frozenset(),
    dict: {}
}


_seq_mappend = lambda a, b: list(chain(a,b))

_generic_mappends = {
    Number: add,
    str: add,
    Sequence: _seq_mappend,
    Mapping: chain_dict_update,
    Set: or_,
}

_builtin_to_generic = {
    int: Number,
    float: Number,
    complex: Number,
    str: str,
    list: Sequence,
    tuple: Sequence,
    dict: Mapping,
    set: Set,
    frozenset: Set
}


def _get_generic_type(obj, generics=_generic_types, 
                      known_to_generics=_builtin_to_generic):
    """Attempt to get the most generic type possible.
    
    If the passed object is an instance of a builtin type,
    then a simple dictionary lookup is performed, otherwise,

    """
    if type(obj) in known_to_generics:
        return known_to_generics[type(obj)]
    return next(filter(lambda g: isinstance(obj, g), generics), None)


def _get_generic_mappend(generic, known_mappends=_generic_mappends):
    """Accepts a generic type and returns its generic mappend.
    """
    return known_mappends.get(generic, None)


def get_generic_mappend(obj, generics=_generic_types,
                        known_to_generics=_builtin_to_generic,
                        known_mappends=_generic_mappends):
    """Accepts an arbitrary object and attempts find its generic type and then
    its generic mappend. If a generic type can't be determined, a type error
    is raised.

    Optionally, a customized iterable of generics, a mapping of known types
    to generic types or a mapping of generic types to mappends can be passed.
    """
    generic = _get_generic_type(obj, generics, known_to_generics)

    if generic is None:
        raise TypeError("No known generic for {!r} instance of {!s}"
                        "".format(obj, type(obj)))
    
    mappend = _get_generic_mappend(generic, known_mappends)

    if mappend is None:
        raise TypeError("No known generic mappend for {!r} instance of {!s}"
                        "".format(obj, type(obj)))

    return mappend


def get_generic_mempty(obj, known_mempties=_builtin_mempties):
    """Accepts an object and tries to find its known mempty value. If no
    known mempty exists, a TypeError is raised.
    
    Optionally, a mapping of known type to mempty values can be passed. The
    default value is a mapping of only types found in builtin: int, float,
    complex, str, list, tuple, dict, set and frozenset.
    """
    mempty = known_mempties.get(type(obj), None)
    if mempty is None:
        raise TypeError("No known mempty for {!r} instance of {!s}"
                        "".format(obj, type(obj)))
    return mempty

def generic_mconcat(mappend, *objs):
    """Generic implementation of mconcat for known monodic objects that don't
    define it.
    """
    return reduce(mappend, objs)
