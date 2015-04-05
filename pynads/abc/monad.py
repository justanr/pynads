from abc import abstractmethod
from .applicative import Applicative


class Monad(Applicative):
    r"""Monads are probably the most misunderstood concept in Haskell.
    All a monad truly means is that it's a context for a value that
    provides a mechanism for interacting with that value.

    Consider the Haskell Monad typeclass:

        .. code-block:: Haskell
            class Monad m where
                return :: a -> m a
                (>>=) :: m a -> (a -> b) -> m b

                (>>) :: m a -> m b -> m b
                x >> y = x >>= \_ -> y 

                fail :: String -> m a
                fail msg = error msg

    The only real things that need to be concerned with are `return` and
    `(>>=)`. `(>>)` is just a shortcut to ignoring a monadic value in
    favor of the next one in the chain. `fail` is used by Haskell as a way
    to indicate failure. Oddly, sadly, it throws an exception by default
    instead of providing a blank interface. Luckily, it can be easily
    overridden.

    `return` is just Applicative's pure. Because reasons, pure
    and return are different things but do the exact same thing. That leaves
    `(>>=)` -- also known as bind, shove, push, etc -- which looks scary 
    but really isn't.

    The type signature of `(>>=)` looks very similar to fmap! Essentially,
    it's fmap in reverse. Instead of taking a function and mapping it over
    a Functor, `(>>=)` takes a monad and places its value into a function.
    The only contract in place is that the final result of a `(>>=)` call
    is a monad of the same type, e.g `Just 4 >>= \x -> Nothing`. 
    Just and Nothing are both "members" of the Maybe type.

    Like before, Maybe, Either, [] and (->)  will be our guides here:

        .. code-block:: Haskell
            instance Monad Maybe where
                return = Just
                (Just x) >>= f = f x
                Nothing  >>= _ = Nothing

            instance Monad (Either a) where
                return = Right
                (Left x)  >>= _ = Left x
                (Right x) >>= f = f x

            instance Monad [] where
                return a = [a]
                xs >>= f = concat (map f xs)

             instance Monad ((->) r) where
                return x = \_ -> x
                f >>= g  = \e -> (g (f e)) e

    Maybe and Either's monads are really straight forward. `return` is the
    success data type. And `(>>=)` does pattern matching to see if a value
    should be passed to a function or if a failure needs to propagate.

    For example:

        .. code-block:: Haskell
            isEven x = x `mod` 2 == 0
            incIfEven = if isEven x then Just (x+1) else Nothing 
            Just 4 >>= incIfEven
            -- Just 5
            Just 5 >>= incIfEven >>= incIfEven
            -- Nothing
    
    It becomes more clear that the failure is simply propagating when Either
    becomes involved:

        .. code-block:: Haskell
            incIfEven = if isEven x then Right (x+1) 
                        else Left ("Got odd: " ++ show x)
            Right 4 >>= incIfEven
            -- Right 5
            Right 5 >>= incIfEven >>= incIfEven
            -- Left "Got odd: 5"

    This is a powerful thing in its own right. By using `(>>=)` with Maybe or
    Either, we can bail out of a computation early and not worry about
    anything further happening. Moreover, it allows us to focus on what the
    failure condition is (in this case, an odd number) without worrying
    about if we got a Just/Right or a Nothing/Left and reacting that way.
    The simple, raw power of these monads can't be overstated.

    Moving onto [], which represents "non-deterministic" computations. Keep
    in mind that "non-determinism" means multiple results in this context.
    An excellent example is finding the square root of a natural number,
    theres actually *two* results: a positive root and a negative root, except
    in the case of 0, then the only root is 0.

        .. code-block:: Haskell
            intSqrt x  = sqrt $ fromIntegral x
            trueSqrt x = if x == 0 then [0] else [intSqrt x, -intSqrt x]
            trueSqrt 4
            [2.0, -2.0]

    Using this, we can find the roots of a list of natural numbers:

        .. code-block:: Haskell
        map trueSqrt [1,4,9]
        [[1.0, -1.0], [2.0, -2.0], [3.0, -3.0]]

    Except we probably don't want to produce a list of lists, rather we'd want
    a single unified list of these roots. In Haskell, flattening a list of
    lists is done by using the concat function.

        .. code-block:: Haskell
        concat $ map trueSqrt [1,4,9]
        [1.0, -1.0, 2.0, -2.0, 3.0, -3.0]

    And this is exactly what `(>>=)` does for []. Given a non-determistic
    input, find some non-deterministic output for each value and create
    one unified non-deterministic output. Simply put: Take a list, compute
    a list based on each value in the original list, then take all those
    lists and create a single list.

    Now for the really scary looking monad instance of (->). The bind results
    in a function which accepts a single argument and feeds it first to
    the left hand function, then takes that result and feeds it to the right
    hand function which returns a function, then the original e is passed
    to the resulting function. It's probably clearer to break it down this
    way:

        .. code-block:: Haskell
        f >>= g = \e -> let a = f e
                            h = g a
                        in h e

    This makes the flow much clearer and makes the purpose of the bind
    operation apparent: threading a value (or environment) through multiple
    function calls. In fact, it's pretty much the same as `((->) r)`'s `<*>`
    operator, just in reverse! Instead of feeding the result of `(g e)` through
    `(f e)`, we feed the result of `(f e)` through `(g e)`.

    In pynads, the Monad ABC defines one abstract method and two concrete
    methods.

    ``bind`` is the abstract method, and it defines the actual binding
    operation. The final result of bind *should* be a new instance of the
    monad, rather than manipulating the instance. However, pynads offers
    no guards against this.

    >>> Just(4).bind(lambda x: Just(x+1))
    ... Just 5

    ``__rshift__`` is the operator form of it.

    >>> Just(4) >> (lambda x: Just(x+1))
    ... Just 5

    There's also ``__ilshift__`` which is the "assignment" variant of it;
    however, it merely allows shortcutting:

    >>> r = Just(4)
    >>> r = r >> (lambda x: Just(x+1))
    >>> # instead, do this...
    >>> r <<= lambda x: x+1
    >>> repr(r)
    ... Just 5
    """
    __slots__ = ()

    @abstractmethod
    def bind(self, f):
        r"""Pushes a value into a monadic transformer function.

        :param callable f: A callable the accepts a single plain value
        and returns a monad.

        >>> Just(4).bind(lambda x: Just(x+2) if x > 4 else Nothing())
        ... Nothing

        Since the result of bind should be an instance of Monad, it's
        possible to chain multiple calls together:

        >>> add_two = lambda x: Just(x+2)
        >>> Just(2).bind(add_two).bind(add_two)
        """
        return False

    def __rshift__(self, f):
        r"""Pushes a value into a monadic transformer function.

        :param callable f: A callable that accepts a single plain value
        and returns a monad.

        >>> Just(4) >> (lambda x: Just(x+2) if x > 4 else Nothing())
        ... Nothing

        It's also possible to chain multiple transforms together:

        >>> add_two = lambda x: Just(x+2)
        >>> Just(2) >> add_two >> add_two
        ... Just 6

        """
        return self.bind(f)

    def __ilshift__(self, f):
        r"""Helper operator. The same as using bind or >> but
        as an assignment operator. The return value is *new* monad
        not an altered one.

        >>> m = Right(4)
        >>> m <<= lambda x: Right(x+2) if x < 1 else Left("greater than 1")
        >>> print(m)
        Left greater than 1

        """
        return self.bind(f)
