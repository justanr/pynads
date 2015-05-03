from abc import abstractmethod
from functools import reduce
from .container import ContainerABC


class Monoid(ContainerABC):
    """
    In Haskell, `Monoid` is a typeclass that provides an interfaces for
    how mempty, mappend and mconcat interact with data types. It's
    defined like this:

    .. code-block:: Haskell
        class Monoid m where
            mempty  :: m
            mappend :: m -> m -> m
            mconcat :: [m] -> m
            mconcat :: foldr mappend mempty

    `mempty` represents a "Zero" value for a certain data structure. `mappend`
    -- while looking like it would deal with lists in particular -- is a
    function that knows how to join two monoidal values together. `mconcat`
    knows how to go from a list of monoidal values to a single monoid value,
    by default this is implemented as folding over the list from the right
    beginning with the structure's "Zero" value.

    Saying "Zero value" is a handy shortcut for saying "this is a value when
    used with mappend and X, where X is a monoidal data structure, the
    result is X."

    The Haskell wiki for Data.Monoid gives the following examples:

    .. code-block:: Haskell
        mappend mempty x = x
        mappend x mempty = x

    In Python, consider what happens when you any of the following:

    .. code-block:: Python
        [1,2,3,4] + []
        {'a': 10, 'b': 7}.update({})
        (1,2,3) + ()
        1 + 0
        'hello' + ''

    There are even "zero values" for more complex objects as well. For
    example, `datetime.datetime(2015, 4, 1) + datetime.timedelta(days=0)` is
    the same as not adding the timedelta at all! This isn't to claim that
    these are all monoids, just to give examples of "zero values."

    Zero values depend on more on the operation preformed by `mappend` than
    the data structure. For example, in Haskell there are actually two types
    of numeric monoids: Sum and Product. Both have different mempty values:

    - 0 for Sum, because mappend is represented as `(+)`
    - 1 for Product, because mappened is represented as `(*)`

    If they shared the same mempty, one would be wrong: `(*) 1 0` is zero and
    `(+) 1 1` is two. So it's important to consider the implication of how
    mappend is implemented before deciding what the "Zero value" is.

    While pynads will not enforce this, to be consider a proper monoid,
    a monoidal structure must statisfy an additional requirement: the
    structure's mappend must be transative. That is:

        .. code-block:: Haskell
            mappend x (mappend y z) == mappend (mappend x y) z

    Similar to how:

        .. code-block:: Python
            1 + (2 + 3) == (1 + 2) + 3

    Rather, it is up the implementations of Monoid to fulfill this requirement.

    In the context of `pynads`, Monoid serves as an interface. It defines
    an operator `+` which calls the mappend method with the instance and
    other object as arguments. And, like Haskell, it provides a default
    implementation of mconcat via reduce.

    Monoid also defines one abstract method and "an abstract property":

    - mappend needs to be defined so two monoidal values can be joined
    - mempty needs to be an attribute at the class level that represents
    the zero value of the monoidal structure.

    Since there's already `__new__` and metaclass muckery elsewhere in
    `pynads`, enforcement of having mempty is handled by Monoid's `__new__`
    method which introspects the class upon instantiation and raises a
    TypeError when it doesn't find mempty in the MRO.

    If multiple monoidal types are needed from one structure, it's best
    to create a parent class which inherits from Monoid, and then children
    classes that define mempty and mappend as needed. Consider, for example:

    .. code-block:: Python
        class NumMonoid(Monoid):
            # defines common methods...
            pass

        class SumMonoid(NumMonoid):
            mempty = 0

            def mappend(self, other):
                return SumMonoid(self.v + other.v)

        class ProdMonoid(NumMonoid):
            mempty = 1

            def mappend(self, other):
                return ProdMonoid(self.v * other.v)
    """
    __slots__ = ()

    def __new__(cls, *a, **k):
        if all('mempty' not in c.__dict__ for c in cls.mro()):
            msg = "Can't instantiate abstract class {!s} with " \
                  "abstract property mempty.".format(cls.__name__)
            raise TypeError(msg)
        return super(Monoid, cls).__new__(cls, *a, **k)

    def __add__(self, other):
        """Shortcut to self,mappend(other)
        """
        return self.mappend(other)

    @abstractmethod
    def mappend(self, other):
        """This method should define how to take two monoidal values of
        the same structure and return a single monoidal value of the same
        structure.
        """
        return False

    @classmethod
    def mconcat(cls, *monoids):
        """Similar to Haskell, this class also provides a default
        implementation of mconcat which simply reduces a list of monoids
        using the monoid's mappend method as the accumulator.

        However, this method may not performant for all monoids. See:
        ``pynads.concrete.list.List``. In that case, override mconcat
        as a classmethod and provide an implementation.
        """
        if len(monoids) < 2:
            raise TypeError("Need at least two values for mconcat")
        return reduce(cls.mappend, monoids)
