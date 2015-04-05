from abc import abstractmethod
from .functor import Functor


class Applicative(Functor):
    """Applicative Functors are data types that can store potential
    computations. Since Applicative Functors are also functors, they are also
    mappable and must implement the `fmap` method.

    Consider the Haskell Applicative typeclass:

        .. code-block:: Haskell
            typeclass Applicative f where
                pure :: a -> f a
                <*>  :: f (a -> b) -> f a -> f b

    All `pure` does is take a regular value and places it into a "minimal
    context" needed to use `<*>`. In Haskell, it can just know what it needs
    to do. However, Python lacks these capabilities, so pynad's take on `pure`
    -- called `unit` -- takes a value and an Applicative class and returns an
    instance of that Applicative with that value supplied.

    `<*>` is a more powerful version of `fmap`. Instead of taking a function
    by itself, it accepts an instance of Applicative that is holding a
    function as well as another Applicative instance and maps the stored
    function over the second's stored value.

    Examining some instances of Applicative may be helpful:

        .. code-block:: Haskell
            instance Applicative Maybe where
                pure           = Just
                (Just f) <*> x = fmap f x
                Nothing  <*> _ = Nothing

            instance Applicative [] where
                pure [a]  = [a]
                fs <*> xs = [f x | x <- xs, f <- fs]

            instance Applicative (Either a) where
                pure            = Right
                (Left x)  <*> _ = Left x
                (Right f) <*> x = fmap f x

            instance Applicative ((->) r) where
                pure x  = \_ -> x
                f <*> g = \e -> (f e) (g e)

    The Applicative instance of Maybe is straight forward: pure simply places
    a value into Just (remember that Haskell automatically curries functions
    and data constructors are just functions). `pure 4 :: Maybe Int` outputs
    `Just 4`. The `<*>` definition for Maybe follows its Functor fmap
    definition. A function contained in a `Just` is fmapped over the next
    value. But attempting to map a Nothing over something results in Nothing.

    `[]`'s instance may look a little weird. But `[]` represents a
    "non-deterministic" computation, or rather a computation that results
    in multiple values. It's pure simply takes a value and places it in
    a singleton list. But `<*>` looks strange. However, all it does is take a
    list of functions and a list of values and applies every function to
    every value. In Python, it'd look like this:

    >>> [f(x) for x in xs for f in fs]

    Either's applicative instance follows from its Functor instance. A Right
    mapped over a value returns the result of the function in Right fmapped
    over the value. A Left, however, simply propagates.

    For `((->) r)`, it looks odd. In this case, pure takes a value and
    returns a function that ignores its input and returns the initial value.
    But `<*>` takes two functions and returns a function that accepts a value
    and then feeds that value first to `f` which then returns a function,
    the value is then fed to `g` which returns a result. The new function is
    fed the new result and returns it result. Complicated? Just a little.

    Consider this example (from Learn You A Haskell):
    `(+) <*> (+3) <*> (*100) $ 5`. To break this down:

        .. code-block:: Haskell
            let f = (+)
            let g = (+3)
            let h = (*100)

            -- (+) <$> (+3) means fmap f g means f.g
            let i = (+) . (+3)

            -- <*> composition of i and h
            let j = \e -> (i e) (h e)
            --    = \e -> (((+) . (+3)) e) ((*100) e)

            -- feeding 5 through j ends up looking like this:
            -- j 5 = (((+) . (+3)) 5) ((*100) 5)
            -- j 5 = ((+) (5+3)) (5*100)
            -- j 5 = (+) (8) (500)
            -- j 5 = 8 + 500
            -- j 5 = 508

    In pynads, the Applicative ABC offers two abstract methods and one
    concrete method.

    ``apply`` is the way applicative interactive with each other. The initial
    Applicative needs to be a function that will accept all following
    Applicatives as arguments. It's possible to chain multiple calls to
    apply together if the initial function returns a function
    (or is curried).

    >>> J_mul_two = Just(lambda x: lambda y: x*y)
    >>> J_mul_two.apply(Just(4)).apply(Just(5))
    ... Just 20

    ``unit`` puts a value in the most minimal context needed to form the
    Applicative. In most cases, it will simply be `self.__class__(v)` However,
    it is possible to store multiple values in an Applicative, so no default
    implementation is provided. However, unit should be implemented as a
    classmethod or staticmethod -- preferably classmethod.

    ``__mul__`` (*) is short hand for apply and allows quickly stringing
    together Applicatives. A nice helper for quickly composing applicative
    computations is using the `%` inherited from `pynads.abc.Functor` which
    is the fmap infix operator...

    >>> mul_two = lambda x: lambda y: x*y
    >>> mul_two % Just(4) * Just(5)
    ... Just 20
    """
    __slots__ = ()

    def __mul__(self, f):
        """Shortcut to Applicative.apply for quickly stringing
        Applicatives together.
        """
        return self.apply(f)

    @abstractmethod
    def apply(self, functor):
        return False

    @classmethod
    @abstractmethod
    def unit(cls, v):
        return NotImplemented
