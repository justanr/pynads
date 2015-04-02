from collections.abc import Sequence, Iterable
from itertools import chain
from ..abc import Monad, Monoid
from ..funcs import fmap
from ..utils import _iter_but_not_str_or_map


__all__ = ('List',)


class List(Monad, Monoid, Sequence):
    """Monadic list.

    The List monad can be used to deal with non-deterministic results:

    >>> def sqrt(x):
    ...     "Calc pos and neg roots"
    ...     v = x**(.5)
    ...     return (-v, v)
    >>> ([1,4,9] & List) >> sqrt
    ... List [-1.0,1.0,-2.0,2.0,-3.0,3.0]

    They can also be used for transforming non-deterministic results:

    >>> l = [1,2,3] & List
    >>> fmap(lambda x: x+2, l)
    ... List [3,4,5]

    As well as applying multiple functions to arguments:

    >>> add_two = lambda x: x+2
    >>> mul_two = lambda x: x*2
    >>> fs = [add_two, mul_two] & List
    >>> fs * ([1,4,9] & List)
    ... List(2,8,18,3,6,11)

    Despite the name, this Monad is closer to Python's ``tuple`` than ``list``
    this is because Haskell's lists are immutable. List doesn't support
    item assignment after creation.

    List's unit method can differ between an iterable and strings and mappings.
    When it recieves a string or mapping, it simply places that value into
    context. However, when it receives any other iterable, it consumes that
    value and puts them all into context:

    >>> "fred" & List
    ... List("fred")
    >>> [1,2,3] & List
    ... List(1,2,3)
    >>> {1:'a', 2:'b'} & List
    ... List({1:'a', 2:'b'})

    Usually type checking is frowned upon in Python -- and rightfully so --
    but List tries to do this intelligentlly with a helper function that
    checks against abstract base classes (except for the case of string
    where the actual `str` class is checked against) and ``isinstance``.
    Any data structure that defines an `__iter__` method but doesn't inherit
    from the `collections.abc.Mapping` or `str` classes will be consumed.

    Unlike Haskell, this process is *eager* so passing an infinite sequence
    will just cause it to compute forever, probably blowing memory out of the
    water as well.

    List is also monoidal. It's mempty unit is an empty tuple and mappend
    is simply tuple addition. List provides its own mconcat method which
    uses itertools.chain to create a single consumable iterator rather than
    creating many List instances in between the beginning and final results
    similar to ``str.join`` vs ``str1 + str2 + str3 + ...``.
    """
    __slots__ = ()
    mempty = ()

    def __init__(self, *vs):
        # rather than tyring to do all sorts of
        # complicated stuff with actually being a tuple
        # but also a monad, we'll just proxy all the
        # needed operations to a tuple
        # also alleviates the need for ``__new__``
        super(List, self).__init__(vs)

    def __repr__(self):
        main = "{!s}({!s})"
        if len(self) > 10:
            head = self.v[:5]
            middle = '...{!s} more...'.format(len(self) - 10)
            tail = self.v[-5:]
            body = ','.join([str(i) for i in chain(head, [middle], tail)])

        else:
            body = ','.join([str(v) for v in self.v])

        return main.format(self.__class__.__name__, body)

    @classmethod
    def unit(cls, v):
        """The most basic context for a List monad is a value in a tuple.
        However, it's likely that strings and mappings shouldn't be splatted
        into the delegated tuple.

        If that's the desired behavior,
        """
        if _iter_but_not_str_or_map(v):
            return cls(*v)
        return cls(v)

    def fmap(self, f):
        return self.unit([f(v) for v in self.v])

    def apply(self, applicative):
        vals = [f(x) for f in self.v for x in applicative.v]
        return self.unit(vals)

    def bind(self, f):
        return self.unit(chain.from_iterable(fmap(f, self)))

    def mappend(self, other):
        """Chains together an instance of List with a non-str/Mapping
        iterable to produce a new List instance containing all values.
        """
        if not _iter_but_not_str_or_map(other):
            msg = "Can only mappend non-str/Mapping iter with {!s}" \
                  "not {!r}".format(self.__class__.__name__, type(other))
            raise TypeError(msg)
        return self.unit(chain(self, other))

    @classmethod
    def mconcat(cls, *monoids):
        """Rather using what amounts to reduce(add, *monoids, ()), List's
        mconcat uses itertools.chain to create a single iterator out of many
        and feeds that to List.unit.
        """
        return cls.unit(chain(*monoids))

    # here be boring stuff...
    def __hash__(self):
        return hash(("List", self.v))

    def __eq__(self, other):
        if isinstance(other, List):
            return self.v == other.v
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, List):
            return not self.v == other.v
        return NotImplemented

    # functools.total_ordering (2.7+)
    # I miss thee! D:
    def __lt__(self, other):
        if isinstance(other, List):
            return self.v < other.v
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, List):
            return self.v > other.v
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, List):
            return self.v <= other.v
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, List):
            return self.v >= other.v
        return NotImplemented

    def __iadd__(self, other):
        return self + other

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return self.v[idx] & List
        return self.v[idx]

    def __len__(self):
        return len(self.v)

    def __iter__(self):
        return iter(self.v)

    def __contains__(self, x):
        return x in self.v

    def __reversed__(self):
        return reversed(self.v)

    def index(self, x):
        return self.v.index(x)

    def count(self, x):
        return self.v.count(x)
