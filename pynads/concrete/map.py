from collections import Mapping
from ..abc import Applicative, Monoid
from ..utils.internal import classproperty
from ..utils import chain_dict_update


class Map(Applicative, Monoid, Mapping):
    """An attempt at implementing a Python dictionary as a Applicative Functor.

    Similar to Haskell's Data.Map datatype but also serving as an
    Applicative as well.

    There are differences between Data.Map and dict:

    - Data.Map is a balanced binary tree, dict is a hash table
    - Data.Map can support more data type (must only be Ord k) where as
    dict requires its keys to be hashable (i.e. non-mutable).

    The Functor implementation for Map simply maps a function over the values
    of the internal dictionary.

    The Applicative instance for Map takes a Map that holds callables as values
    and matches them to inputs in the joining Maps. If a key is found to not
    exist in any of these mappings, then it is discarded rather than attempting
    to hold on to it.

    Map is also a Monoid. It's mempty is simply an empty dictionary, and its
    mappend and mconcat are functionally the same. Both delegate to a helper
    function which updates a blank dictionary from one or more joining
    dictionaries. In both instances, if a key appears in multiple maps,
    then the last appearance wins.
    """
    __slots__ = ()
    _mempty = None

    def __init__(self, v=None, **kwds):
        data = {}
        if v:
            data.update(v)
        data.update(kwds)

        super(Map, self).__init__(data)

    def __repr__(self):
        return "{!s}({!r})".format(self.__class__.__name__, self.v)

    @classproperty
    def mempty(cls):
        if cls._mempty is None:
            cls._mempty = cls()
        return cls._mempty

    @classmethod
    def unit(cls, v):
        """Similar to Data.Map.singleton: accepts a tuple with key-value
        pair in it and returns a mapping with that sinlge value.
        """
        return cls([v])

    def fmap(self, func):
        """Maps a function over the values in the mapping.

        >>> m = Map({'a': 1, 'b': 2, 'c': 3})
        >>> m.fmap(lambda x: x+1)
        ... Map({'a': 2, 'b': 3, 'c': 4})
        """
        return self.__class__({k: func(v) for k, v in self.v.items()})

    def apply(self, other):
        """Maps functions that appear in this mapping to their
        corresponding values in another mapping, ignoring keys that
        don't appear in either.

        Missing a key from either mapping causes it to disappear altogether
        from the final product.

        >>> m = Map({'a': lambda x: lambda y: x+y})
        >>> n = Map({'a': 1})
        >>> o = Map({'a': 2})
        >>> m * n * o
        ... Map({'a': 3})

        >>> p = Map({'b': 10})
        >>> m * n * p * o
        ... Map({})

        This can be useful for filter with the pynads.funcs.identity function.
        """
        keys = set(self.keys()) & set(other.keys())
        staging = {k: self[k](other[k]) for k in keys}
        return self.__class__(staging)

    @classmethod
    def fromkeys(cls, keys, value=None):
        """Delegates to __builtin__.dict.fromkeys then returns an
        Applicative Map with that dictionary.

        Allows easily constructing a Map from an iterable of keys and
        provides them with a default value.
        """
        return cls(dict.fromkeys(keys, value))

    def mappend(self, other):
        """Joining two mapping together is as easy as creating a new mapping
        representing the values from both mappings.
        """
        return self.__class__(chain_dict_update(self, other))

    @classmethod
    def mconcat(cls, *ds):
        """Similar to pynads.concrete.list.List, Map provides its own
        implementation of mconcat so it doesn't create a bunch of
        orphanded dictionaries to be garbage collected.
        """
        return cls(chain_dict_update(*ds))

    # from collections.Mapping
    def __len__(self):
        return len(self.v)

    def __contains__(self, x):
        return x in self.v

    def __iter__(self):
        return iter(self.v)

    def __getitem__(self, k):
        return self.v[k]

    # niceities
    def keys(self):
        return self.v.keys()

    def __eq__(self, other):
        if isinstance(other, Map):
            return self.v == other.v
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)
