from collections import Sequence
from itertools import chain
from ..abc import Monad, Monoid
from ..utils import _iter_but_not_str_or_map


__all__ = ('List',)


class List(Monad, Monoid, Sequence):
    """Monadic List implementation.

    There are two ways to view lists: a sequence and non-deterministic
    results -- by non-deterministic results I mean instead of choosing one
    possible result from some function, we choose all of them. A function
    that outputs a list says, "I didn't know which one you wanted, so here's
    all of them."

    In Haskell, ``[]`` has the following instances we're interested in:

        .. code-block:: Haskell
            instance Functor [] where
                fmap = map

            instance Applicative [] where
                pure a    = [a]
                fs <*> xs = [f x | x <- xs, f <- fs ]

            instance Monad [] where
                pure a   = [a]
                xs >>= f = concat (map f xs)

    The Functor instance is simple to understand: fmapping over a ``[]`` is the
    samething as mapping over a ``[]``. The function is just applied to
    every value in the list. Pynads mimics this behavior but also returns a
    new instance of List rather than a `map` object.

    For the Applicative instance, a single list is built from two lists
    by not zipping them together, but applying every function from the
    first list to every value in the second list. Note that the new list has
    the pattern [f1 x1, f2 x1, f1 x2, f2 x2, ...].  This doesn't matter in
    practice until you pull a value at a specific index.

    The monadic instance does something a little strange. It resembles the
    Functor instance, however it also flattens the result. This is because
    bind expects the function being bound to output a list itself for every
    value in the original list. A perfect example of this is finding square
    roots of natural numbers. For every natural number, there are actually
    two square roots: x and -x. The exception is 0, which only has 0 as its
    root. Heres how it looks in Pynads:

    >>> def sqrt(x):
    ...     if x == 0:
    ...         return [0]
    ...     else:
    ...         return [x**.5, -(x**.5)]
    >>> sqrt(4)
    ... [2.0, -2.0]
    >>> sqrt(0)
    ... [0]

    However, if we simply mapped this function over a list, we'd get this:

    >>> nat_nums = List(1. 4. 9)
    >>> nat_nums.fmap(sqrt)
    ... List([1.0, -1.0], [2.0, -2.0], [3.0, -3.0])

    We need to flatten this:

    >>> from itertools import chain
    >>> List(*chain.from_iterable(nat_nums.fmap(sqrt)))
    ... List(1.0, -1.0, 2.0, -2.0, 3.0, -3.0)

    This is what bind abstracts away for us:

    >>> nat_nums.bind(sqrt)
    ... List(1.0, -1.0, 2.0, -2.0, 3.0, -3.0)
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
            body = ', '.join([repr(i) for i in chain(head, [middle], tail)])

        else:
            body = ', '.join([repr(v) for v in self.v])

        return main.format(self.__class__.__name__, body)

    @classmethod
    def unit(cls, v):
        """The most basic context for a List monad is a value in a List monad.
        This is exactly equalivant to List(v). This unit method doesn't
        attempt to splat iterables or do anything fancy, which makes it
        inline with Haskell's []'s return/pure.

            .. code-block:: Haskell
                listReturn :: a -> [a]
                listReturn a = return a

                listReturn 1   -- [1]
                listReturn [1] -- [[1]]

                [1] >>= listReturn -- [1]
                -- internally what happens is:
                -- [[1]] is constructed
                -- and then flattened to [1]
        """
        return cls(v)

    def fmap(self, func):
        """fmapping over a List monad is the same as using map on the
        underlying tuple with the provided function.

        This is reflected by the Functor instance of [] in Haskell:

            .. code-block:: Haskell
                instance Functor [] where
                    fmap = map
        """
        return self.__class__(*[func(v) for v in self])

    def apply(self, other):
        """Using `<*>` between a ``[(a->b)]`` and a `[a]` in Haskell
        results in applying every function in the first list to every
        value in the second list. It is implemented like this:

            .. code-block:: Haskell
                instance Applicative [] where
                    pure x    = [x]
                    fs <*> xs = [f x | x <- xs, f <- fs]

        The comparable Python is:

            .. code-block:: Python
                [f(x) for x in xs for f in fs]

        Which is exactly how this is implemented.
        """
        return self.__class__(*[f(x) for f in self for x in other])

    def bind(self, bindee):
        """Binding a List monad to a function requires a little more
        explaination. In Haskell, ``[]`` doesn't represent a sequence
        necessarily, but rather a collection of choices.

        The function being used with ``>>=`` should, itself, return a ``[]``,
        which represents the way to choose every result from the function
        in terms of all the choices in the original ``[]``.

        For example, square roots on natural numbers actually produce *two*
        results: a positive root and negative root, except in the special case
        0 which only has itself as the root.

        We can model this in Haskell:

            .. code-block:: Haskell
                intSqrt x = sqrt $ fromIntegeral x
                trueSqrt x = if x == 0 then [0] else [intSqrt x, -intSqrt x]
                trueSqrt 4
                --[2.0, -2.0]

        Using this ``trueSqrt`` function, we can "choose" all the possible
        roots from a list of numbers:

            .. code-block:: Haskell
                map trueSqrt [1, 4, 9]
                --[[1.0, -1.0], [2.0, -2.0], [3.0, -3.0]]

        However, a list of lists isn't likely the desired result. If we wanted
        to find the roots of all these numbers, we're gonna have to jump
        through hoops (pretend the intSqrt works on negative numbers)

            .. code-block:: Haskell
                roots = map trueSqrt [1, 4, 9]
                sndRoots = map trueSqrt (concat roots)

        The concat is line noise. We started with a ``[Int]`` and ended up
        with a ``[[Int]]``. However, using ``[1,4,9] >>= trueSqrt`` gives us
        back a single list consisting of the positive and negative roots of
        the numbers. We can chain them together multiple times (assuming
        ``trueSqrt`` works on negative numbers) and only ever get back
        ``[Int]`` rather than increasingly nested ``[[[[Int]]]]``.

        The Haskell `concat` function just flattens a single level. In
        Python, there's a similar tool: ``itertools.chain.from_iterable``
        which also flattens just a single level.

        Consider the square root example above translated into terms of
        pynads:

        >>> # note: we can use regular Python
        >>> # as the return type rather than pynads.List
        >>> def true_root(x):
        ...     if x == 0:
        ...         return [0]
        ...     else:
        ...         y = x**.5
        ...         return [y, -y]
        >>> List(1, 4, 9) >> true_root
        List(1.0, -1.0, 2.0, -2.0, 3.0, -3.0)
        """
        return self.__class__(*chain.from_iterable(self.fmap(bindee)))

    def mappend(self, other):
        """In Haskell. the ``mappend`` for ``[]`` is defined as ``(++)``
        which simply takes one list and prepends it to another list.

            .. code-block:: Haskell
                [1] ++ [2,3]
                [1,2,3]
                [1] `mappend` [2,3]
                [1,2,3]

        However, this can be greatly inefficient if a bunch of lists are
        being combined as we're constantly prepending to the beginning of
        a list. In Python, we can cheat some and simply use ``itertools.chain``
        to combine many iterables into one iterable, and then feeding the
        result to ``pynads.List``.
        """
        if not _iter_but_not_str_or_map(other):
            raise TypeError("Can only append non-str/Mapping iterable to a "
                            "{!s} instance, not {!s}"
                            "".format(type(self), type(other)))
        else:
            return self.__class__(*chain(self, other))

    @classmethod
    def mconcat(cls, *monoids):
        """By default, Monoid.mconcat is provided. However, it uses reduce
        with the class defined mappend method. In the case of List, we'd
        end up just creating a bunch of List instances that would be
        instantly garbage collected. Instead, we can define our own
        implementation of mconcat that will create only one new instance.
        """
        return cls(*chain.from_iterable(monoids))

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
            return self.__class__(*self.v[idx])
        return self.v[idx]

    def __len__(self):
        return len(self.v)

    def __iter__(self):
        return iter(self.v)

    def __contains__(self, x):
        return x in self.v

    def __reversed__(self):
        return List(*reversed(self.v))

    def index(self, x):
        return self.v.index(x)

    def count(self, x):
        return self.v.count(x)
