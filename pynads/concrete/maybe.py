from abc import abstractmethod
from ..abc import Monad, Container
from ..utils.compat import wraps
from ..utils.decorators import method_optional_kwargs
from ..utils.internal import _propagate_self, Instance


__all__ = ('Maybe', 'Just', 'Nothing')


class Maybe(Monad):
    """Represents a potential computation.

    The actual constructor for Maybe doesn't return an instance of Maybe
    but instead an instance of Just or the singleton Nothing.

    The unit method returns an instance of Just, which is the minimal
    context needed for a potential computation.

    Consider the Haskell implementation of Maybe:

    .. code-block: Haskell
       data Maybe a = Nothing | Just a

       instance Functor Maybe where
           fmap f Nothing   = Nothing
           fmap f (Just x)  = Just (f x)

       instance Applicative Maybe where
           pure             = Just
           Nothing  <*> _   = Nothing
           (Just f) <*> x   = fmap f x

       instance Monad Maybe where
           return           = Just
           Nothing  >>=     = Nothing
           (Just x) >>= f   = f x

    Doing any of these actions to a Nothing results in Nothing -- like
    Billy Preston sang:

        Nothing from nothing leaves nothing
        You gotta have something if you wanna be with me
        Nothing from nothing leaves nothing
        You gotta have something if you wanna be with me

    However, mapping over a Just, returns the result wrapped in Just.
    Applying a function wrapped in Just maps it over the next value. And
    binding a Just a with a function, returns the result of the function,
    which should be a Maybe -- the function is responsible for determining
    if it should be a Nothing or (Just x).

    Maybe is helpful when you expect you'll encounter a None in Python.
    In fact, this monad is pretty much an elaborate wrapper around this
    idiom:

    .. code-block:: Python
       from random import randint
       def none_safe_inc(x):
           if x is None:
               return None
           else:
               return x+1

       def none_safe_sq(x):
           if x is None:
               return None
           else:
               return x*x

        def bad_get_int():
            x = randint(1,10)
            return x if x%2 else None

       x = bad_get_int()
       y = none_safe_inc(none_safe_mul(x))

    However, instead of writing `if x is None: return None` a bunch of times,
    the same block can be rewritten as:

    .. code-block:: Python
       from pynads import Maybe, Just

       def inc(x): return Just(x+1)
       def sqr(x): return Just(x*x)

       y = Maybe(bad_get_int()) >> sqr >> inc

    If `bad_get_int` returns None, Maybe, by default, translates None into
    Nothing (which is implemented as a Singleton, sorry). Nothing propagates
    itself over binds, mappings and applications. However, if `bad_get_int`
    returns a value, it's wrapped in Just which will allow operations to
    take effect on the value.

    The way this works is when calling Maybe directly, an optional checker
    can be passed. By default, it simply checks if the value passed is ``None``
    however, any ``a -> Bool`` function can be subsituted:

    >>> is_even = lambda x: not x%2
    >>> Maybe(3, checker=is_even)
    ... Nothing
    >>> Maybe(4, checker=is_even)
    ... Just(4)

    Since monads aren't just about the bind operator, but really about
    sequencing operations, the Maybe monad here is combined with Scala's Option
    monad. The implementation here is inspired by fn.py's version of Option.

    It's also possible to decorator callables with Maybe via
    ``Maybe.as_wrapper`` which wraps the output of a function in the Maybe
    monad. Optionally, the checker function for Maybe can be provided if the
    default shouldn't be used.
    """
    __slots__ = ()

    def __new__(self, v, checker=lambda v: v is not None):
        if checker(v):
            return super(Maybe, self).__new__(Just, v)
        return Nothing

    def __bool__(self):
        return isinstance(self, Just)

    __nonzero__ = __bool__

    @staticmethod
    def unit(v):
        return Just(v)

    @method_optional_kwargs
    @classmethod
    def as_wrapper(cls, func, checker=lambda v: v is not None):
        """Allows using Maybe as a decorator with an optional checker
        function. The default is simply the same as Maybe's default.

        .. code-block:: python
            # use the default checker
            @Maybe.as_wrapper
            def bad_get_int():
                x = randint(1, 4)
                return x if x % 2 else None

            # provide a checker function
            @Maybe.as_wrapper(checker=lambda x: x % 2)
            def bad_get_int():
                return randint(1, 4)
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cls(func(*args, **kwargs), checker=checker)
        return wrapper

    @abstractmethod
    def filter(self, predicate):
        pass

    @abstractmethod
    def get_or(self, default):
        pass

    @abstractmethod
    def get_or_call(self, func, *args, **kwargs):
        pass

    @abstractmethod
    def or_else(self, default):
        pass

    @abstractmethod
    def or_call(self, func, *args, **kwargs):
        pass


class Just(Maybe):
    """Represents a value from a calculation.
    """
    __slots__ = ()

    def __new__(cls, v):
        return Container.__new__(cls)

    def __repr__(self):
        return "Just {!r}".format(self.v)

    def __eq__(self, other):
        if isinstance(other, Just):
            return self.v == other.v
        return NotImplemented

    def fmap(self, func):
        return Just(func(self.v))

    def apply(self, other):
        return other.fmap(self.v)

    def bind(self, bindee):
        return bindee(self.v)

    def filter(self, predicate):
        return self if predicate(self.v) else Nothing

    def get_or(self, default):
        return self.v

    def get_or_call(self, *args, **kwargs):
        return self.v

    or_else = or_call = _propagate_self


class _Nothing(Maybe):
    """Singleton class representing a monadic failure in a computation.

    filter, fmap, apply and bind all return the singleton instance of Nothing
    and short circuits all further operations. However, get_or, get_or_call,
    or_else, and or_call all provide ways of recovering, so to speak, from a
    failed computation by being able to provide backup values to be provided
    in place of the Nothing
    """
    __slots__ = ()
    _inst = None
    v = Instance()  # lol

    def __new__(cls, value=None):
        if cls._inst is None:
            cls._inst = Container.__new__(cls)
        return cls._inst

    def __repr__(self):
        return "Nothing"

    def __eq__(self, other):
        return isinstance(other, _Nothing)

    filter = fmap = apply = bind = _propagate_self

    @staticmethod
    def get_or(default):
        return default

    @staticmethod
    def get_or_call(func, *args, **kwargs):
        return func(*args, **kwargs)

    @staticmethod
    def or_else(default):
        return Maybe(default)

    @staticmethod
    def or_call(func, *args, **kwargs):
        return Maybe(func(*args, **kwargs))

# Singleton Nothing
Nothing = _Nothing()
