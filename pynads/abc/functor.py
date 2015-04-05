from abc import ABCMeta, abstractmethod
from .container import Container
from ..utils import with_metaclass


class Functor(with_metaclass(ABCMeta, Container)):
    """Functors are data types that know how to be mapped over.

    Consider the Haskell Functor typeclass:

        .. code-block:: Haskell
            class Functor a where
                fmap :: (a->b) -> f a -> f b

    as well as some examples:

        .. code-block:: Haskell
            instance Functor Maybe where
                fmap f Nothing  = Nothing
                fmap f (Just x) = Just (f x)

            instance Functor [] where
                fmap = map

            instance Functor (Either a) where
                fmap f (Left x)  = Left x
                fmap f (Right x) = Right (f x)

            --even functions can be mapped over!
            instance Functor ((->) r) where
                fmap = (.)

    Functor is a typeclass that accepts a type constructor (Maybe, Either, [])
    which is kind: `* -> *` -- that is, it needs a single argument to become
    a "concrete type."  Note: Kinds are types for types, essentially, and
    `* -> *` is said "star to star". `instance Functor Maybe` works because
    Maybe has the type constructor: `Maybe a` which is `* -> *`

    The reason for two definitions of `fmap` is that Maybe has two data
    constructors -- Just and Nothing. Mapping a function over `Just`
    outputs the results of the function when applied to the value stored in
    Just wrapped in a Just. But mapping over a Nothing -- which represents
    a failure -- outputs Nothing.

    And the same for `[]`. We can't say `instance Functor [a]` because `[a]`
    takes no arguments. The reason for `fmap = map` is used is because `map`
    has type `(a -> b) -> [a] -> [b]` which is exactly the type of fmap if
    it was specialized to `[]`. "Take a function that goes from a to b, and a
    [a] and give back a [b]."

    However, Either needs to be partially applied to become a Functor because
    its type constructor is `Either a b` -- `* -> * -> * ->`. This also means
    that Either's fmap can only map over instances of `Right` and not `Left`.
    Why? Consider the type of fmap if it was specialized to Either.
    `fmap :: (b -> c) -> (Either a b) -> (Either a c)` We can see that
    `(Either a)` corresponds to `f` in fmap's original type. Whereas the `b`
    type that isn't partially applied corresponds to the `a` in the original
    type. Essentially: `(Either a) == f` and `b == a` in `f a`.

    Similar to Maybe, Either has two definitions of `fmap` because it has
    two data constructors: `Left` which represents a failure with an error
    message and `Right` which represents a successful computation.

    The same applies to the function constructor `(->)`. It is kind `* -> *`
    so it needs to be partially applied. However, mapping over a function with
    a function is just function composition, which is denoted by the `(.)`
    function in Haskell. In Python, the same thing would look like this:

        .. code-block:: Python
            def compose(f, g):
                return lambda *a, **k: f(g(*a, **k))

    `(.)` is a function that takes two functions and returns a function that
    runs the first function and then passes the output to the second function.
    Unsurprisingly, `(.)` has type: `(a -> b) -> (r -> a) -> (r -> b)` which
    matches `fmap` specialized to `(->)`.

    To implement the functor interface, all the subclass needs to do is
    implement fmap. fmap should return a new functor with the new data in it,
    preserving all other data.

    >>> # see pynads.concrete.map.Map however
    >>> class FMapDict(dict, Functor):
    >>>     def fmap(self, f):
    >>>         return FMapDict((k, f(v)) for k,v in self.items())

    However, pynads and Haskell both don't enforce this restriction. You
    *could* do this:

        .. code-block: Haskell
            data MyType a = MyType { thing :: a, count :: Int }

            instance Functor MyType where
                fmap f (MyType x c) = MyType (f x) (c + 1)

    But since this implementation of fmap has the "side effect" of increasing
    the count in MyType, it can't be considered a true Functor since this
    check must be true:

        .. code-block:: Haskell
            fmap id MyType == MyType
            -- False because MyType {thing = x, count = 1} will be changed
            -- to MyType {thing = f x, count = 2}

    In the `FMapDict` example above, all `fmap` does is map over the values
    in a dictionary and leaves the keys unchanged. Making the identity check
    above valid:

    >>> f = FMapDict({'a':10, 'b':7})
    >>> assert f.fmap(lambda x: x) == f

    Similar to Haskell, pynads has an "infix" fmap operator: `%`, which was
    chosen because it is superficially similar to `<$>`. Using the above
    FMapDict example, it could also be written as:

    >>> f = FMapDict({'a': 10, 'b': 7})
    >>> (lambda x: x) % f

    The `%` operator is implemented using the `__rmod__` magic method, so
    the function comes first then the Functor it is being applied to.

    See Also:
        - pynads.concrete.map.Map
        - pynads.funcs.lifted.fmap
    """
    __slots__ = ()

    @abstractmethod
    def fmap(self, f):
        return False

    def __rmod__(self, f):
        return self.fmap(f)
