from collections import namedtuple
from .functor import fmap
from .monad import Monad

_Left = namedtuple('_Left', ['msg'])
_Right = namedtuple('_Right', ['v'])

class Either(Monad):
    """Enhanced version of Maybe. Represents a successful computation or
    a failed computation with an error msg.
    """
    def __new__(self, *args):
        raise TypeError("Instantiate Left or Right directly.")

    def __bool__(self):
        return isinstance(self, Right)

    @staticmethod
    def unit(v):
        return Right(v)

class Left(Either, _Left):
    """Similar to Nothing in that it only returns itself when fmap, apply
    or bind is called. However, Left also carries an error message instead
    of representing a completely failed computation.
    """

    def __new__(self, msg):
        return _Left.__new__(self, msg)

    def __repr__(self):
        return "Left {}".format(self.msg)

    fmap = apply = bind = lambda self, _: self

class Right(Either, _Right):
    """Represents a result of a computation. Similar to Just except it is
    semantically a finished computation.
    """

    def __new__(self, v):
        return _Right.__new__(self, v)

    def fmap(self, f):
        return Right(f(self.v))

    def apply(self, applicative):
        return fmap(self.v, applicative)

    def bind(self, f):
        return f(self.v)
