from collections import namedtuple
from ..funcs import fmap
from ..abc import Monad, Container
from ..utils import _propagate_self


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

       y = (bad_get_int & Maybe) >> sqr >> inc

    If `bad_get_int` returns None, Maybe, by default, translates None into
    Nothing (which is implemented as a Singleton, sorry). Nothing propagates
    itself over binds, mappings and applications. However, if `bad_get_int`
    returns a value, it's wrapped in Just which will allow operations to
    take effect on the value.
    """
    __slots__ = ()

    def __new__(self, v, checker=lambda v: v is not None):
        if checker(v):
            return super(Maybe, self).__new__(Just, v)
        return Nothing

    def __bool__(self):
        return isinstance(self, Just)

    @staticmethod
    def unit(v):
        return Just(v)


class Just(Maybe):
    """Represents a value from a calculation.
    """
    __slots__ = ()

    def __new__(cls, v):
        return Container.__new__(cls)

    def __repr__(self):
        return "Just {!r}".format(self.v)

    def fmap(self, f):
        return Just(f(self.v))

    def apply(self, applicative):
        return fmap(self.v, applicative)

    def bind(self, f):
        return f(self.v)

    def __eq__(self, other):
        if isinstance(other, Just):
            return self.v == other.v
        return NotImplemented


class _Nothing(Maybe):
    """Singleton class representing a monadic failure in a computation.

    fmap, apply and bind all return the singleton instance of Nothing
    and short circuits all further bind operations.
    """
    __slots__ = ()
    __inst = None

    def __new__(self, value=None):
        if self.__inst is None:
            self.__inst = Container.__new__(self)
        return self.__inst

    def __repr__(self):
        return "Nothing"

    fmap = apply = bind = _propagate_self

# Singleton Nothing
Nothing = _Nothing()
