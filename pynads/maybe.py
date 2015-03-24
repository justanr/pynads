from collections import namedtuple
from .functor import fmap
from .monad import Monad


class Maybe(Monad):
    """Represents a potential computation.
    
    The actual constructor for Maybe doesn't return an instance of Maybe
    but instead an instance of Just or the singleton Nothing.

    The unit method returns an instance of Just, which is the minimal
    context needed for a potential computation.
    """
    def __new__(self, v, checker=lambda v: v is not None):
        return Just(v) if checker(v) else Nothing

    def __bool__(self):
        return isinstance(self, Just)

    @staticmethod
    def unit(v):
        return Just(v)


class Just(Maybe):
    """Represents a value from a calculation.
    """

    def __new__(cls, v):
        return object.__new__(cls)

    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return "Just {!r}".format(self.v)

    def __eq__(self, other):
        return isinstance(other, Just) and self.v == other.v

    def fmap(self, f):
        return Just(f(self.v))

    def apply(self, applicative):
        return fmap(self.v, applicative)

    def bind(self, f):
        return f(self.v)

class _Nothing(Maybe):
    """Singleton class representing a monadic failure in a computation.
    
    fmap, apply and bind all return the singleton instance of Nothing
    and short circuits all further bind operations.
    """
    __inst = None

    def __new__(self, value=None):
        if self.__inst is None:
            self.__inst = object.__new__(self)
        return self.__inst

    def __repr__(self):
        return "Nothing"

    fmap = apply = bind = lambda self, _: self

# Singleton Nothing
Nothing = _Nothing()
