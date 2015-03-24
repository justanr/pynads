from collections import namedtuple
from ..funcs import fmap
from ..abc import Monad
from ..utils import _propagate_self, _failed


__all__ = ('Maybe', 'Just', 'Nothing')


class Maybe(Monad):
    """Represents a potential computation.
    
    The actual constructor for Maybe doesn't return an instance of Maybe
    but instead an instance of Just or the singleton Nothing.

    The unit method returns an instance of Just, which is the minimal
    context needed for a potential computation.
    """
    __slots__ = ()

    def __new__(self, v, checker=lambda v: v is not None):
        return Just(v) if checker(v) else Nothing

    def __bool__(self):
        return isinstance(self, Just)

    @staticmethod
    def unit(v):
        return Just(v)


class Just(Maybe):
    """Represents a value from a calculation.

    Just will act as a proxy for all methods found on its value *except*
    for __repr__, __name__, fmap, apply and bind.
    """
    __slots__ = ()

    def __new__(cls, v):
        return object.__new__(cls)

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

    proxy and starproxy (see: ``pynads.abc.container.Container``) simply
    return False.
    """
    __slots__ = ()
    __inst = None

    def __new__(self, value=None):
        if self.__inst is None:
            self.__inst = object.__new__(self)
        return self.__inst

    def __repr__(self):
        return "Nothing"

    fmap = apply = bind = _propagate_self
    proxy = starproxy = _failed

# Singleton Nothing
Nothing = _Nothing()
